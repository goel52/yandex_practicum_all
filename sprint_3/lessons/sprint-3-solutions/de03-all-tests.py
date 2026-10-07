import os
import sys
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

DE_S3_TESTS = (
    # ( # не выполняется решение юзера
    #     'de03020801',
    #     '2. Анализ вводных по задаче/8. Описание его схемы/Задание 1',
    #     'de03020801auth.sql',
    #     'exec_user_sql',
    # ),
    # airflow connections add 'create_files_api' \
    #     --conn-json '{
    #         "conn_type": "http",
    #         "host": "d5dg1j9kt695d30blp03.apigw.yandexcloud.net"
    #     }'    
    (
        'de03030503',
        '5. Реализация ETL в Airflow/3. Extract как сделать запрос на генерацию файла через API/Задание 3',
        'de03030503auth.py',
    ),
)

LESSON_TESTS_PATH = '/app/sprint-3-tests'

def clear_comments(query):
    clear_query = ''
    for lines_query in query.splitlines():
        if lines_query.strip() and lines_query.strip()[0:2] != '--':
            clear_query += lines_query + '\n'
    return clear_query

def exec_user_sql(
        full_lesson_path: str,
        realization_file='realization.sql',
        sql_author=None,
        dsn='postgresql://jovyan:jovyan@localhost:5432/de'):
    
    sql_file_user = f'{full_lesson_path}/{realization_file}'
    try:
        # sql_user = open(sql_file_user, 'r').read()
        with open(sql_file_user, 'r') as f:
            sql_user = f.read()
        set_queries_user = clear_comments(sql_user).strip().split(';')
        while '' in set_queries_user:
            set_queries_user.remove('')
        
        if len(set_queries_user) == 0:
            return False, 'Файл realization.sql пуст.'

        # with psycopg2.connect(dsn=dsn, options='-c statement_timeout=0') as conn:
        with psycopg2.connect(dsn=dsn) as conn:
            conn.autocommit = True
            cur = conn.cursor()
            print(f'{TerminalColors.HEADER}-- exec sql user{TerminalColors.ENDC}')
            for queries in set_queries_user:
                print(queries)
                cur.execute(queries)
                # TODO: проеврять какая таблица создана и сразу тестировать, проверять какой импорт выполнен и сразу проверяьть воизбежании неверных решений и зависании на других этапах см. тикет DS-4708 

                print(f'{TerminalColors.OKGREEN}-- ok{TerminalColors.ENDC}')
            # conn.commit()
            print(f'{TerminalColors.HEADER}-- check{TerminalColors.ENDC}')
    except FileNotFoundError:
        print('Не найден файл realization.sql, проверяем состояние базы...')    
    except Exception as e:
        return False, e
    return 'exec_user_sql ok'
    
        

def all_tests():
    sys.path.append(LESSON_TESTS_PATH)
    from de_s3_tests import run_tests

    for test in DE_S3_TESTS:
        DE_S3_TEST = test[0]
        print(DE_S3_TEST, ' - ', test[1], end='')
        realization_file = test[2] if test[2] else test[0]
        # выполнение решения юзера для тестов которые не выполняют решение
        dsn = 'postgresql://jovyan:jovyan@localhost:5432/de'
        if len(test) > 3:
            if test[3] == 'exec_user_sql':
                if len(test) > 4:
                    dsn = test[4]
                print('\nВыполнение авторского...')
                result = exec_user_sql(
                    full_lesson_path=LESSON_TESTS_PATH,
                    realization_file=realization_file,
                    dsn=dsn
                )
                print(result)
        result = run_tests(
            full_lesson_path=LESSON_TESTS_PATH,
            de_s3_test=DE_S3_TEST,
            realization_file=realization_file
        )
        print(result)

if __name__ == '__main__':
    all_tests()
