import ast
import datetime
from typing import Optional, Tuple

import pyspark.sql.functions as F
from pyspark.sql import SparkSession
from pyspark.sql.window import Window

from sprint_7_check_service.ast_tools.ast_visitors_custom import NodeQuery


def input_event_paths(date, depth):
    dt = datetime.datetime.strptime(date, '%Y-%m-%d')
    return ["/user/username/data/events/date="
            f"{(dt-datetime.timedelta(days=x)).strftime('%Y-%m-%d')}"
            for x in range(depth)]


class TagTops:
    RESPONSE_KEY = '4Gn4c3m12C'

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

        if not tree.node(ast.FunctionDef, name='tag_tops').exists:
            return (False,
                    'Отсутствует функция `tag_tops`.')

        tag_tops_str = ast. unparse(
            tree.node(ast.FunctionDef, name='tag_tops').all[0])

        exec(tag_tops_str, None, None)

        date = '2011-02-01'

        try:
            tag_tops_result = eval(
                f"tag_tops('{date}', 3, spark)",
                {'tag_tops': eval('tag_tops'),
                 'input_event_paths': input_event_paths,
                 'spark': spark,
                 'F': F,
                 'Window': Window}).collect()
        except Exception as e:
            return False, f'Исправьте решение, ошибка: {e}'

        if len(tag_tops_result) != 6:
            return (False, 'Функция возвращает количество строк не равное'
                    ' количеству пользователей в выборке')

        if (set(tag_tops_result[0].asDict().keys()) !=
           {'tag_top_1', 'tag_top_3', 'user_id', 'tag_top_2'}):
            return (False, 'Функция должна вернуть результат в четырех '
                    'колонках `user_id`, `tag_top_1`, `tag_top_2`,'
                    ' `tag_top_3`')

        for row in tag_tops_result:
            if row.user_id == 2 and (
                    row.tag_top_1 != 'tag_2' or
                    row.tag_top_2 != 'tag_1' or
                    row.tag_top_3 is not None):
                return (False, 'Функция не удовлетворяет условиям задачи в'
                        ' части распределения тэгов по рангам')

        return True, None
