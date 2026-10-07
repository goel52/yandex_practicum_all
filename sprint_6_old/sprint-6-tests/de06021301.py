import importlib
import os
import sys
import traceback
from numpy import r_

import vertica_python


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

conn_test = {
    'host': 'vertica.tgcloudenv.ru',
    'port': 5433,
    'user': 'tester_readonly_all',
    'password': 'WN0rql2hkq9yNvz',
    'database': 'dwh',
    'autocommit': True
}


def de_test(
        full_lesson_path: str,
        realization_file='realization.sql',
        sql_author=None,
        dsn='postgresql://jovyan:jovyan@localhost:5432/de',
        user_login=None):

    try:
        if user_login is None:
            user_py = importlib.import_module(realization_file[:-3])

            user_login = user_py.vertica_user
        print(f'login: {user_login}')
    except Exception as e:
        traceback.print_exc()
        return False, f'\n{TerminalColors.WARNING}Исправьте ошибки в файле {realization_file}{TerminalColors.ENDC}\n'

    try:
        with vertica_python.connect(**conn_test) as conn:
            cur = conn.cursor()

            sql_not_nul = f'SELECT count(*) FROM {user_login}.dialogs;'
            sql_nul = f"SELECT count(*) FROM {user_login}.dialogs WHERE message_ts::date in ('2004-01-01', '2005-12-31');"

            cur.execute(sql_not_nul)
            r_user = cur.fetchone()

            if r_user[0] == 0:
                return False, f'Таблица {user_login}.dialogs не содержит данных'

            cur.execute(sql_nul)
            r_user = cur.fetchone()

            if r_user[0] != 0:
                return False, f'Проверочный запрос {sql_nul} возвращает данные. Выполните задание. Обратите внимание, что тест не вполняет код пользователя. Удалите партиции и запустите проверку.'

    except FileNotFoundError:
        error_message = (f'Не найден файл с решением {realization_file}')
        return False, error_message
    except Exception as e:
        error_message = (str(e))
        return False, error_message
    else:
        return True, None

if __name__== '__main__':
    LESSON_TESTS_PATH = '/app/sprint-6-tests'
    res = de_test(LESSON_TESTS_PATH, 'de06020601auth.py')
    print(res)
