import os

import psycopg2

#d_platform
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


def de_test(
        full_lesson_path: str,
        realization_file='realization.sql',
        sql_author=None,
        dsn='postgresql://jovyan:jovyan@localhost:5432/de'):

    try:
        with psycopg2.connect(dsn=dsn) as conn:
            cur = conn.cursor()

            tables = ('customer_research', 'user_activity_log', 'user_order_log')
            for table in tables:
                sql_select = f'select * from stage.{table} limit 10;'
                cur.execute(sql_select)
                r_user = cur.fetchall()

                if len(r_user) == 0:
                    return False, f'{TerminalColors.WARNING}\nТаблица `stage.{table}` не содержит данных{TerminalColors.ENDC}'

    except FileNotFoundError:
        error_message = (f'Не найден файл с решением {realization_file}')
        return False, error_message
    except Exception as e:
        error_message = (str(e))
        return False, error_message
    else:
        return True, None
