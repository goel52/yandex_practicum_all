import ast
import datetime
from random import randint
from typing import Optional, Tuple
from pyspark.sql import SparkSession

from sprint_7_check_service.ast_tools.ast_visitors_custom import NodeQuery


class PySparkJob:
    RESPONSE_KEY = 'InUWykr9z0'

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

        def_main = tree.node(ast.FunctionDef, name='main')

        variables = ['date',
                     'days_count',
                     'events_base_path',
                     'output_base_path'
                     ]

        assigns = {}

        for assign in variables:
            if not def_main.node(ast.Assign, targets__0__id=assign).exists:
                return (False,
                        'В функции `main` отсутствует назначение'
                        f' переменной `{assign}`')
            py_str = ast.unparse(def_main.node(
                ast.Assign, targets__0__id=assign).all[0])
            assigns.update({assign: py_str})

        today = datetime.datetime.now()
        test_date = (
            today - datetime.timedelta(randint(0, 1000))
            ).strftime('%Y-%m-%d')

        class _sys:
            argv = ['_test.py',
                    test_date,
                    '5',
                    'test-events_base_path',
                    'test_output_base_path'
                    ]

        variables_eval = {}

        item = 0
        for variable in variables:
            try:
                var_eval = eval(
                    assigns[variable].replace(f'{variable} =', ''),
                    {},
                    {'sys': _sys})
            except Exception as e:
                return (
                    False,
                    f'В строке c `{variable} =` исправьте решение, ошибка: {e}'
                    )
            variables_eval.update({variable: var_eval})
            item += 1
            expected = _sys.argv[item]
            if variable in ('days_count',):
                valid = (type(var_eval) is str and var_eval == expected) or (type(var_eval) is int and var_eval == int(expected))
            else:
                valid = var_eval == expected
            if not valid:
                return (False,
                        f'Переменная `{variable}` должна принимать значение'
                        f' из `sys.argv[{item}]')

        return True, None
