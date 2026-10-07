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
            r_auth = '''PARTITION BY ((dialogs.message_ts)::date) GROUP BY (CASE WHEN ("datediff"('year', (dialogs.message_ts)::date, ((now())::timestamptz(6))::date) >= 2) THEN (date_trunc('year', (dialogs.message_ts)::date))::date WHEN ("datediff"('month', (dialogs.message_ts)::date, ((now())::timestamptz(6))::date) >= 3) THEN (date_trunc('month', (dialogs.message_ts)::date))::date ELSE (dialogs.message_ts)::date END);'''

            sql_select = f'''
                select export_objects('','{user_login}.dialogs');
            '''

            cur.execute(sql_select)
            r_user = cur.fetchone()

            if r_auth not in r_user[0]:
                return False, 'Создайте таблицу согласно условий задания. Не найдено требуемое партиционирование.'

    except FileNotFoundError:
        error_message = (f'Не найден файл с решением {realization_file}')
        return False, error_message
    except Exception as e:
        error_message = (str(e))
        return False, error_message
    else:
        # flag, err = cmp_res
        # return flag, err
        return True, None

if __name__== '__main__':
    LESSON_TESTS_PATH = '/app/sprint-6-tests'
    res = de_test(LESSON_TESTS_PATH, 'de06020601auth.py')
    print(res)
