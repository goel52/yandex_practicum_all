import ast
from typing import Optional, Tuple

from sprint_7_check_service.ast_tools.ast_visitors_custom import NodeQuery


class MockSql():
    class read():
        def json(path):
            return path


class MockEwentsWrite():
    def __init__(self, mock_str: str) -> None:
        self.mock_str = mock_str

    def write():
        pass

    def partitionBy(_: str):
        pass

    def format(_: str):
        pass

    def save(self, _: str):
        return _


class JobsWithParams:
    RESPONSE_KEY = 'DJhlUTi6G5'

    def __init__(self) -> None:
        pass

    def check(self,
              student_solution: str,
              student_file_name: str = 'realization.py'
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

        if not tree.node(ast.Import, names__0__name='sys').exists:
            return (False,
                    'Отсутствует `import sys`, не меняйте прекод.')

        if not (
            tree.node(ast.ImportFrom, module='pyspark').exists
            and tree.node(ast.ImportFrom, names__0__name='SparkConf').exists
            and tree.node(ast.ImportFrom, names__1__name='SparkContext').exists
        ):
            return (False,
                    'Отсутствует `from pyspark import SparkConf, SparkContext`'
                    ' не меняйте прекод.')

        if not tree.node(ast.Assign, targets__0__id='events').exists:
            return (False,
                    'Не найдено назначение переменной `events`')

        t_events = tree.node(ast.Assign, targets__0__id='events')

        if 'sql' not in t_events.node('id').all:
            return (False,
                    'Не найдено назначение `events = sql...`')

        if 'read' not in t_events.node('attr').all:
            return (False,
                    'Не найдено назначение `events = sql.read...`')

        if 'json' not in t_events.node('attr').all:
            return (False,
                    'Ожидается вызов атрибута `json` метода `read`')

        sql = MockSql  # noqa
        base_input_path = 'test_base_input_path'  # noqa
        date = 'test_date'  # noqa

        try:
            user_path = eval(
                ast.unparse(t_events.all[0]).replace('events = ', '')
                )
        except NameError:
            return (False,
                    'Для получения директории чтения '
                    'используйте переменные `base_input_path` и `date`')
        except Exception as e:
            return (False,
                    'Проверьте получение директории чтения '
                    f'`events = sql.read.json()`\nОшибка:{type(e)}\n{str(e)}')

        if user_path != 'test_base_input_path/date=test_date':
            return (False,
                    'Проверьте, что в `events = sql.read.json()` '
                    'передается путь вида `base_input_path/date=date` '
                    'получаемый из переменных `base_input_path`, `date`')

        if not tree.node(ast.Expr).all:
            return (False,
                    'Не найдено выражение `events.write...`')

        events_write = ast.unparse(tree.node(ast.Expr).all[0])

        if 'events.write' not in events_write:
            return (False,
                    'Дополните выражение `events.write...`, не меняйте'
                    ' структуру прекода')
        elif "partitionBy('event_type')" not in events_write:
            return (False,
                    "Не найден вызов метода `partitionBy('event_type')`")
        elif "format('parquet')" not in events_write:
            return (False,
                    "Не найден вызов метода `format('parquet')`")
        elif "save(" not in events_write:
            return (False,
                    "Не найден вызов метода `save()`")

        events_write = tree.node(ast.Expr).all[0]

        events = MockEwentsWrite
        events.write = events
        events.write.partitionBy = events
        events.write.partitionBy.format = events

        base_output_path = 'test_base_output_path'  # noqa

        save_path = eval(ast.unparse(events_write))

        if 'test_base_output_path/date=test_date' != save_path:
            return (False,
                    'Проверьте, что в `save()` '
                    'передается путь вида `base_output_path/date=date` '
                    'получаемый из переменных `base_output_path`, `date`')

        return True, None
