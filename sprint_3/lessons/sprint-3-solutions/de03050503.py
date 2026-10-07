import os
import sys
import importlib
import traceback
import psycopg2

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
        realization_file='realization.py',
        sql_author=None,
        dsn='postgresql://jovyan:jovyan@localhost:5432/de'):


    try:
        with psycopg2.connect(dsn=dsn) as conn:
            conn.autocommit = True
            cur = conn.cursor()

            tables = (
                'customer_research',
                'user_activity_log',
                'user_order_log'
            )

            for table in tables:
                sql_check = f'select * from stage.{table} limit 10'
                cur.execute(sql_check)
                row = cur.fetchall()
                if len(row) == 0:
                    return False, f'Таблица stage.{table} не заполнена данными'

    except Exception as e:
        return False, f'\n{TerminalColors.WARNING}{e.__class__.__name__}\n\n{e}{TerminalColors().ENDC}\n'


    return True, None
    