import importlib
import sys
import traceback
import __main__
import os

import vertica_python

from template_comparsion.compare_with_template import prepare_code, compare_nodes, STR_TO_REPLACE

STR_TO_REPLACE = [
    '# Адрес сервера из инструкции',
    '# Порт из инструкции',
    '# Полученный логин',
    '# Пароль',
    'res = cur.fetchall()',
    'return res'
]

class TerminalColors:
        HEADER = '\033[95m'
        OKBLUE = '\033[94m'
        OKCYAN = '\033[96m'
        OKGREEN = '\033[92m'
        WARNING = '\033[93m'
        FAIL = '\033[91m'
        ENDC = '\033[0m'
        BOLD = '\033[1m'
        UNDERLINE = '\033[4m'

def auth_try_select(conn_info):
    with vertica_python.connect(**conn_info) as conn:
        cur = conn.cursor()
        cur.execute("Select 1 as a1;")
        res = cur.fetchall()
        return res


def de_test(
        full_lesson_path: str,
        realization_file='realization.py',
        sql_author=None,
        dsn='postgresql://jovyan:jovyan@localhost:5432/de',
        precod=None):

    # проверка на нарушение прекода
    if not precod:
        precod = f'{os.path.dirname(os.path.abspath(__file__))}/{__name__}precod.py'
    # Подготовка темплейта к сравнению и инициализация логера ошибок
    nodes_template, ErrorLog = prepare_code(precod, str_to_rpl=STR_TO_REPLACE)
    # Подготовка кода студента к сравнению
    nodes_user, _ = prepare_code(realization_file, is_template=False, ErrorLog=ErrorLog, str_to_rpl=STR_TO_REPLACE)
    # Сравнение деревьев темплейта и студента (элементы темплейта должны быть в дереве студента)
    compare_nodes(nodes_template, nodes_user, ErrorLog)

    try:
        user_py = importlib.import_module(realization_file[:-3])
    except Exception as e:
        traceback.print_exc()
        return False, f'\n{TerminalColors.WARNING}Исправьте ошибки в файле {realization_file}{TerminalColors.ENDC}\n'

    try:
        user_conn_info = user_py.conn_info

        res_auth = auth_try_select(user_conn_info) #проверка параметров подключения

        res = user_py.try_select(user_conn_info)

        if res != res_auth:
            return False, f'Проверьте функцию `try_select`, результат отличается от ожидаемого {res_auth} != {res}'

    except TypeError as e:
        return False, f'Проверьте параметры подключения в `conn_info`\n{e}'
    except Exception as e:
        return False, e

    return True, None

if __name__== '__main__':
    LESSON_TESTS_PATH = __main__.__file__.split('/de')[0]
    sys.path.append(LESSON_TESTS_PATH)
    auth_file = __main__.__file__.replace('.py','auth.py').split('/')[-1]
    res = de_test(LESSON_TESTS_PATH, realization_file=auth_file)
    print(res)
