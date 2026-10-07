import ast
import datetime
from random import randint
from typing import Optional, Tuple

from sprint_7_check_service.ast_tools.ast_visitors_custom import NodeQuery


class DefInputPaths:
    RESPONSE_KEY = 'rK6YrRAkPV'

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
            return False, f'Исправтье решение, ошибка: {e}'

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

        return True, None
