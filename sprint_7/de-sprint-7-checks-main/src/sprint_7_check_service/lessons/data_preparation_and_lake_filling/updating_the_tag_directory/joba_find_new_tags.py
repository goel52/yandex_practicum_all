import ast
import datetime
from random import randint
from typing import Optional, Tuple
from pyspark.sql import SparkSession

from sprint_7_check_service.ast_tools.ast_visitors_custom import NodeQuery


class JobaFindNewTags:
    RESPONSE_KEY = 'oKGR1Y9EeT'

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
                     'suggested_cutoff',
                     'base_input_path',
                     'verified_tags_path',
                     'base_output_path']

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
                    '300',
                    'test_base_input_path',
                    'test-verified_tags_path',
                    'test-base_output_path']

        variables_eval = {}

        item = 0
        for variable in variables:
            try:
                var_eval = eval(
                    assigns[variable].replace(f'{variable} =', ''),
                    None,
                    {'sys': _sys})
            except Exception as e:
                return (
                    False,
                    f'В строке c `{variable} =` исправьте решение, ошибка: {e}'
                    )
            variables_eval.update({variable: var_eval})
            item += 1
            expected = _sys.argv[item]
            if variable in ('days_count', 'suggested_cutoff'):
                valid = (type(var_eval) is str and var_eval == expected) or (type(var_eval) is int and var_eval == int(expected))
            else:
                valid = var_eval == expected
            if not valid:
                return (False,
                        f'Переменная `{variable}` должна принимать значение'
                        f' из `sys.argv[{item}]')

        node_paths = def_main.node(ast.Assign, targets__0__id='paths')

        if not node_paths.exists:
            return (False,
                    'В функции `main` отсутствует назначение'
                    ' переменной `paths`')
        py_paths = ast.unparse(node_paths.all[0])

        dt = datetime.datetime.strptime(variables_eval['date'], '%Y-%m-%d')

        try:
            paths_eval = eval(
                py_paths.replace('paths =', ''),
                {'test': 'test',
                 'base_input_path': variables_eval['base_input_path'],
                 'dt': dt,
                 'days_count': variables_eval['days_count'],
                 'datetime': datetime})
        except Exception as e:
            return (False,
                    f'В строке c `paths =` исправьте решение, ошибка: {e}')

        auth_path = [f"{variables_eval['base_input_path']}/date={(dt-datetime.timedelta(days=x)).strftime('%Y-%m-%d')}/event_type=message" for x in range(int(variables_eval['days_count']))]  # noqa

        if len(auth_path) != len(paths_eval):
            return (False,
                    f'Длина списка path = {len(paths_eval)}, ожидается - '
                    f'{len(auth_path)}. '
                    'Проверьте метод получения списка `paths`, c входными '
                    'переменными `base_input_path = '
                    f'{variables_eval["base_input_path"]}`, `date = '
                    f'{variables_eval["date"]}`, `days_count = '
                    f'{variables_eval["days_count"]}`')

        for item in range(0, len(auth_path)):
            if paths_eval[item] != auth_path[item]:
                return (False,
                        f'path[{item}] = {paths_eval[item]}, ожидается - '
                        f'{auth_path[item]}. '
                        'Проверьте метод получения списка `paths`, c входными '
                        'переменными `base_input_path = '
                        f'{variables_eval["base_input_path"]}`, `date = '
                        f'{variables_eval["date"]}`, `days_count = '
                        f'{variables_eval["days_count"]}`')

        # TODO: test  .write.parquet(f"{base_output_path}/date={date}")
        return True, None
