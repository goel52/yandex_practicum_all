import importlib
import os
import sys

import psycopg2
from airflow.hooks.base import BaseHook

# from airflow.hooks.base_hook import BaseHook

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

    sys.path.append(full_lesson_path)

    try:
        user_py = importlib.import_module(realization_file[:-3])
    except Exception as e:
        return False, f'\n{TerminalColors.WARNING}{e.__class__.__name__}\n\n{e}{TerminalColors().ENDC}\n'

    try:
        with psycopg2.connect(dsn=dsn) as conn:
            conn.autocommit = True
            cur = conn.cursor()
            
            sql_create_test_table = '''
                DROP TABLE IF EXISTS stage.customer_research_test CASCADE;
                CREATE TABLE stage.customer_research_test(
                ID serial,
                date_id          TIMESTAMP ,
                category_id integer,
                geo_id   integer,
                sales_qty    integer,
                sales_amt numeric(14,2),
                PRIMARY KEY (ID)
                );
            '''

            cur.execute(sql_create_test_table)

        conntest = BaseHook.get_connection('pg_connection')

        user_py.load_file_to_pg(
            'customer_research.csv',
            'customer_research_test',
            conntest
        )

        with psycopg2.connect(dsn=dsn) as conn:
            conn.autocommit = True
            cur = conn.cursor()
            
            sql_check = 'select * from stage.customer_research_test'
            cur.execute(sql_check)
            row = cur.fetchall()

            sql_drop = 'DROP TABLE IF EXISTS stage.customer_research_test CASCADE;'
            cur.execute(sql_drop)

        if len(row) == 0:
            return False, f'Функция не выполняет загрузку данных в БД'

    except Exception as e:
        return False, f'\n{TerminalColors.WARNING}{e.__class__.__name__}\n\n{e}{TerminalColors().ENDC}\n'

    return True, True