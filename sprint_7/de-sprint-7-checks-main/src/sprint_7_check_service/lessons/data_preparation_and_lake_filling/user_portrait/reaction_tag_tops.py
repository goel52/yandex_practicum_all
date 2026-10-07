import ast
import datetime
from typing import Optional, Tuple

import pyspark.sql.functions as F
from pyspark.sql import SparkSession
from pyspark.sql.window import Window

from sprint_7_check_service.ast_tools.ast_visitors_custom import NodeQuery
from .tag_tops import input_event_paths


class ReactionTagTops:
    RESPONSE_KEY = 'gvWFf0D782'

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

        if not tree.node(ast.FunctionDef, name='reaction_tag_tops').exists:
            return (False,
                    'Отсутствует функция `reaction_tag_tops`.')

        reaction_tag_tops_str = ast. unparse(
            tree.node(ast.FunctionDef, name='reaction_tag_tops').all[0])

        exec(reaction_tag_tops_str, None, None)

        date = '2011-02-01'

        try:
            reaction_tag_tops_result = eval(
                f"reaction_tag_tops('{date}', 3, spark)",
                {'reaction_tag_tops': eval('reaction_tag_tops'),
                 'input_event_paths': input_event_paths,
                 'spark': spark,
                 'F': F,
                 'Window': Window}).collect()
        except Exception as e:
            return False, f'Исправьте решение, ошибка: {e}'

        if len(reaction_tag_tops_result) != 6:
            return (False, 'Функция возвращает количество строк не равное'
                    ' количеству пользователей в выборке')

        if (set(reaction_tag_tops_result[0].asDict().keys()) !=
            {'dislike_tag_top_2', 'like_tag_top_3',
             'dislike_tag_top_3', 'user_id',
             'like_tag_top_2', 'like_tag_top_1', 'dislike_tag_top_1'}):
            return (False, 'Функция должна вернуть результат в семи '
                    'колонках `user_id`, `like_tag_top_1`, `like_tag_top_2`,'
                    ' `like_tag_top_3`, `dislike_tag_top_1`, '
                    '`dislike_tag_top_2`, `dislike_tag_top_3`')

        for row in reaction_tag_tops_result:
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
