import ast
import datetime
from random import randint
from typing import Optional, Tuple
from pyspark.sql import SparkSession

import pyspark.sql.functions as F

from sprint_7_check_service.ast_tools.ast_visitors_custom import NodeQuery
from sprint_7_check_service.spark_tools.event_df import event_find_new_tags
from sprint_7_check_service.spark_tools.tags_verified import tags_verified_df


class FindNewTags:
    RESPONSE_KEY = 'yuYyLHDDSz'

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

        if not tree.node(ast.Import, names__0__name='datetime').exists:
            return (False,
                    'Отсутствует `import datetime`.')

        if not tree.node(ast.FunctionDef, name='input_paths').exists:
            return (False,
                    'Отсутствует функция `input_paths`.')

        if len(tree.node(ast.FunctionDef).all) != 1:
            return (False,
                    'В решении ожидается одна функция.')

        today = datetime.datetime.now()
        test_date = today - datetime.timedelta(randint(0, 1000))
        test_date_1 = test_date - datetime.timedelta(1)

        test_date = test_date.strftime('%Y-%m-%d')
        test_date_1 = test_date_1.strftime('%Y-%m-%d')

        exec(ast.unparse(tree.node(ast.FunctionDef).all[0]))

        try:
            test_paths = eval(f"input_paths('{test_date}', 3)")
        except Exception as e:
            return False, f'Исправьте решение, ошибка: {e}'

        if type(test_paths) is not list:
            return (False, f'{type(list)} Функция `input_paths` должна '
                    f'возвращать объект `list`, у Вас `{type(test_paths)}`')

        if len(test_paths) != 3:
            return (False,
                    'Функция `input_paths` должна возвращать список с '
                    'длиной равной `depth`, для depth=3 Ваше решение вернуло '
                    f'список длиной {len(test_paths)}')

        for item in test_paths:
            if type(item) is not str:
                return (False,
                        'Элементы возвращаемого сприска должны быть '
                        f'типа string, у Вас - {type(item)}')

        if f'date={test_date}/event_type=message' not in test_paths[0]:
            return (False,
                    'На выходе должен возвращаться список путей датасетов с '
                    'сообщениями за заданное количество дней, начиная с '
                    f'входной даты. Для входных параметров date=`{test_date}`,'
                    'depth=3 часть пути ожидается вида '
                    f'`date={test_date}/event_type=message`, у Вас:'
                    f'{test_paths[0]}'
                    )

        if f'date={test_date_1}/event_type=message' not in test_paths[1]:
            return (False,
                    'На выходе должен возвращаться список путей датасетов с '
                    'сообщениями за заданное количество дней, начиная с '
                    f'входной даты. Для входных параметров date=`{test_date}`,'
                    'depth=3 часть пути даты следующей до входной ожидается '
                    f'вида `date={test_date_1}/event_type=message`, у Вас:'
                    f'{test_paths[1]}'
                    )

        assigns = {}

        for assign in ['messages',
                       'all_tags',
                       'verified_tags',
                       'candidates']:
            if not tree.node(ast.Assign, targets__0__id=assign).exists:
                return (False,
                        'В решении отсутствует назначение'
                        f' переменной `{assign}`')
            py_str = ast.unparse(tree.node(
                ast.Assign, targets__0__id=assign).all[0])
            assigns.update({assign: py_str})

        count_unique_tags = randint(30, 50)
        messages = event_find_new_tags(spark,
                                       count_unique_users=100,
                                       count_unique_tags=count_unique_tags)
        verified_tags = tags_verified_df(spark)

        try:
            all_tags = eval(assigns['all_tags'].replace('all_tags =', ''),
                            None,
                            {'messages': messages,
                            'F': F})
        except Exception as e:
            return (False,
                    f'В строке `all_tags =` исправьте решение, ошибка: {e}')

        try:
            candidates = eval(
                assigns['candidates'].replace('candidates =', ''),
                None,
                {'verified_tags': verified_tags,
                 'all_tags': all_tags})
        except Exception as e:
            return (False,
                    f'В строке `candidates =` исправьте решение, ошибка: {e}')

        student_candidates = len(candidates.collect())
        if student_candidates != count_unique_tags:
            return (False,
                    f'Проверьте решение, на данных с {count_unique_tags} '
                    'уникальными тэгами, в `candidates` '
                    f'попало {student_candidates}')

        return True, None
