import ast
from typing import Optional, Tuple

from pyspark.sql import SparkSession

from sprint_7_check_service.ast_tools.ast_visitors_custom import NodeQuery


class CompareDf:
    RESPONSE_KEY = 'apaYcksAK1'

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

        if not tree.node(ast.FunctionDef,
                         name='compare_df').exists:
            return (False,
                    'Отсутствует функция `compare_df`.')

        compare_df_str = ast. unparse(
            tree.node(ast.FunctionDef, name='compare_df').all[0])

        namespace = {}
        try:
            exec(compare_df_str, namespace)
            compare_df = namespace['compare_df']
        except Exception as e:
            return False, f'Исправьте решение, ошибка: {e}'

        schema = 'Name string, Age long'
        rows = [('Max', 55), ('Yan', 54), ('Ann', 25)]
        base = spark.createDataFrame(rows, schema)
        same = spark.createDataFrame(list(reversed(rows)), schema)
        changed = spark.createDataFrame([('Max', 56), *rows[1:]], schema)
        missing = spark.createDataFrame(rows[:-1], schema)
        duplicate = spark.createDataFrame([*rows, rows[0]], schema)
        empty = spark.createDataFrame([], schema)
        cases = [
            (base, same, True, 'одинаковые данные с другим порядком строк'),
            (base, same.select('Age', 'Name'), True, 'другой порядок колонок'),
            (base, same.toDF('Name1', 'Age2'), False, 'другие имена колонок'),
            (base, changed, False, 'отличающееся значение'),
            (base, missing, False, 'пропущенная строка'),
            (missing, base, False, 'лишняя строка'),
            (base, duplicate, False, 'лишний дубликат'),
            (duplicate, duplicate, True, 'одинаковые данные с дубликатами'),
            (empty, empty, True, 'два пустых датафрейма'),
        ]
        for left, right, expected, description in cases:
            try:
                result = compare_df(left, right)
            except Exception as e:
                return False, f'Исправьте решение ({description}), ошибка: {e}'
            if type(result) is not bool or result != expected:
                return False, f'Неверный результат: {description}; ожидается {expected}.'
        return True, None
