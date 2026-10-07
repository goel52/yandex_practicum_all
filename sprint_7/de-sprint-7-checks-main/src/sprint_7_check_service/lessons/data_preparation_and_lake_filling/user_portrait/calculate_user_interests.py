import ast
import datetime
from typing import Optional, Tuple

import pyspark.sql.functions as F
from pyspark.sql import SparkSession
from pyspark.sql.window import Window

from sprint_7_check_service.ast_tools.ast_visitors_custom import NodeQuery
from .tag_tops import input_event_paths


def tag_tops(date, depth, spark):
    message_paths = input_event_paths(date, depth)
    result = spark.read\
        .option("basePath", "/user/username/data/events")\
        .parquet(*message_paths) \
        .where("event_type = 'message'") \
        .where("event.message_channel_to is not null")\
        .select(F.col("event.message_id").alias("message_id"),
                F.col("event.message_from").alias("user_id"),
                F.explode(F.col("event.tags")).alias("tag"))\
        .groupBy("user_id", "tag")\
        .agg(F.count("*").alias("tag_count"))\
        .withColumn("rank", F.row_number().over(Window.partitionBy("user_id")
                    .orderBy(F.desc("tag_count"), F.desc("tag"))))\
        .where("rank <= 3")\
        .groupBy("user_id")\
        .pivot("rank", [1, 2, 3])\
        .agg(F.first("tag"))\
        .withColumnRenamed("1", "tag_top_1")\
        .withColumnRenamed("2", "tag_top_2")\
        .withColumnRenamed("3", "tag_top_3")

    return result


def reaction_tag_tops(date, depth, spark):
    reaction_paths = input_event_paths(date, depth)
    reactions = spark.read\
        .option("basePath", "/user/username/data/events")\
        .parquet(*reaction_paths)\
        .where("event_type='reaction'")

    all_message_tags = spark.read.parquet("/user/username/data/events")\
        .where("event_type='message' and event.message_channel_to is not null")\
        .select(F.col("event.message_id").alias("message_id"),
                F.col("event.message_from").alias("user_id"),
                F.explode(F.col("event.tags")).alias("tag"))

    reaction_tags = reactions\
        .select(F.col("event.reaction_from").alias("user_id"),
                F.col("event.message_id").alias("message_id"),
                F.col("event.reaction_type").alias("reaction_type")).join(
                    all_message_tags.select("message_id", "tag"), "message_id")

    reaction_tops = reaction_tags\
        .groupBy("user_id", "tag", "reaction_type")\
        .agg(F.count("*").alias("tag_count"))\
        .withColumn("rank", F.row_number().over(
            Window.partitionBy("user_id", "reaction_type")
            .orderBy(F.desc("tag_count"), F.desc("tag"))))\
        .where("rank <= 3")\
        .groupBy("user_id", "reaction_type")\
        .pivot("rank", [1, 2, 3])\
        .agg(F.first("tag"))\
        .cache()

    like_tops = reaction_tops\
        .where("reaction_type = 'like'")\
        .drop("reaction_type")\
        .withColumnRenamed("1", "like_tag_top_1")\
        .withColumnRenamed("2", "like_tag_top_2")\
        .withColumnRenamed("3", "like_tag_top_3")

    dislike_tops = reaction_tops\
        .where("reaction_type = 'dislike'")\
        .drop("reaction_type")\
        .withColumnRenamed("1", "dislike_tag_top_1")\
        .withColumnRenamed("2", "dislike_tag_top_2")\
        .withColumnRenamed("3", "dislike_tag_top_3")

    result = like_tops\
        .join(dislike_tops, "user_id", "full_outer")

    return result


class CalculateUserInterests:
    RESPONSE_KEY = 'JF6yDqayC1'

    def __init__(self) -> None:
        pass

    def check(self,
              student_solution: str,
              spark: SparkSession,
              student_file_name: str = 'realization.py',
              ) -> Tuple[bool, Optional[str]]:
        try:
            tree = NodeQuery(ast.parse(
                student_solution,
                student_file_name,
                mode='exec'))

        except Exception as e:
            return (False,
                    'Ваш код нельзя исполнить,'
                    f' ошибка: {type(e)}.\n'
                    f'{str(e)}')

        for func in ('tag_tops',
                     'reaction_tag_tops',
                     'calculate_user_interests'):
            if not tree.node(ast.FunctionDef,
                            name=func).exists:
                return (False,
                        f'Отсутствует функция `{func}`.')

        calculate_user_interests_str = ast. unparse(
            tree.node(ast.FunctionDef, name='calculate_user_interests').all[0])

        exec(calculate_user_interests_str)

        date = '2011-02-01'

        try:
            calculate_user_interests_result = eval(
                f"calculate_user_interests('{date}', 1, spark)",
                {'calculate_user_interests': eval('calculate_user_interests'),
                 },
                {
                 'input_event_paths': input_event_paths,
                 'spark': spark,
                 'F': F,
                 'Window': Window
                 }).collect()
        except Exception as e:
            return False, f'Исправьте решение, ошибка: {e}'

        if len(calculate_user_interests_result) != 6:
            return (False, 'Функция возвращает количество строк не равное'
                    ' количеству пользователей в выборке')

        if (set(calculate_user_interests_result[0].asDict().keys()) !=
            {'user_id', 'tag_top_1', 'tag_top_2', 'tag_top_3',
             'like_tag_top_1', 'like_tag_top_2', 'like_tag_top_3',
             'dislike_tag_top_1', 'dislike_tag_top_2', 'dislike_tag_top_3'}):
            return (False, 'Функция должна вернуть результат в семи '
                    'колонках `user_id`, `tag_top_1`, `tag_top_2`,'
                    ' `tag_top_3`, `like_tag_top_1`, `like_tag_top_2`,'
                    ' `like_tag_top_3`, `dislike_tag_top_1`,'
                    ' `dislike_tag_top_2`, `dislike_tag_top_3`')

        for row in calculate_user_interests_result:
            if row.user_id == '2' and (
                    row.like_tag_top_1 is not None or
                    row.like_tag_top_2 is not None or
                    row.like_tag_top_3 is not None or
                    row.dislike_tag_top_1 != 'tag_2' or
                    row.dislike_tag_top_2 is not None or
                    row.dislike_tag_top_3 is not None):
                return (False, 'Функция не удовлетворяет условиям задачи в'
                        ' части распределения лайков по рангам')

        return True, None
