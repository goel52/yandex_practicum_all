import importlib
import os
import sys
import traceback

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

auth_login = 'de8a13notrulez_gmail_com'.upper()


def de_test(
        full_lesson_path: str = None,
        realization_file='realization.sql',
        sql_author=None,
        dsn='postgresql://jovyan:jovyan@localhost:5432/de',
        user_login=None):

    try:
        if user_login is None:
            user_py = importlib.import_module(realization_file[:-3])
            user_login = user_py.vertica_user.upper()
        print(f'login: {user_login}')
    except Exception as e:
        traceback.print_exc()
        return False, f'\n{TerminalColors.WARNING}Исправьте ошибки в файле {realization_file}{TerminalColors.ENDC}\n'

    try:
        with vertica_python.connect(**conn_test) as conn:
            cur = conn.cursor()

            # проверка DWH.l_admins - потом оптимизировать
            print('Проверка таблицы `l_admins`...')
            sql_select = f'''
                select count(*) FROM {user_login}__DWH.l_admins;
            '''
            cur.execute(sql_select)
            col_user = cur.description
            r_user = cur.fetchall()

            if len(r_user) == 0:
                return False, f'В таблице l_admins нет данных'

            # проверка DWH.l_groups_dialogs - потом оптимизировать
            print('Проверка таблицы `l_groups_dialogs`...')
            sql_select = f'''
                select count(*) FROM {user_login}__DWH.l_groups_dialogs;
            '''
            cur.execute(sql_select)
            col_user = cur.description
            r_user = cur.fetchall()

            if len(r_user) == 0:
                return False, f'В таблице l_groups_dialogs нет данных'

            # проверка DWH.l_user_message - потом оптимизировать
            print('Проверка таблицы `l_user_message`...')
            sql_select = f'''
                select count(*) FROM {user_login}__DWH.l_user_message;
            '''
            cur.execute(sql_select)
            col_user = cur.description
            r_user = cur.fetchall()

            if len(r_user) == 0:
                return False, f'В таблице l_user_message нет данных'


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
