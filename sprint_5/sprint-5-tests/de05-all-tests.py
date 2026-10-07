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

DE_S5_TESTS = (
    (
        'de05030601',
        'Тема 3. Проектирование DWH/5. Проектирование слоя CDM/Задание 1',
        'de05030601auth.sql',
    ),
    (
        'de05030602',
        'Тема 3. Проектирование DWH/5. Проектирование слоя CDM/Задание 2',
        'de05030602auth.sql',
    ),
    (
        'de05030603',
        'Тема 3. Проектирование DWH/5. Проектирование слоя CDM/Задание 3',
        'de05030603auth.sql',
    ),
    (
        'de05030604',
        'Тема 3. Проектирование DWH/5. Проектирование слоя CDM/Задание 4',
        'de05030604auth.sql',
    ),
    (
        'de05030605',
        'Тема 3. Проектирование DWH/5. Проектирование слоя CDM/Задание 5',
        'de05030605auth.sql',
    ),
    (
        'de05030701',
        'Тема 3. Проектирование DWH/6. Проектирование слоя STG/Задание 1',
        'de05030701auth.sql',
        'exec_user_sql'
    ),
    (
        'de05030702', # ????
        'Тема 3. Проектирование DWH/6. Проектирование слоя STG/Задание 2',
        'de05030702auth.sql',
        'exec_user_sql'
    ),
    (
        'de05030703',
        'Тема 3. Проектирование DWH/6. Проектирование слоя STG/Задание 3',
        'de05030703auth.sql',
        'exec_user_sql'
    ),
    (
        'de05030801',
        'Тема 3. Проектирование DWH/7. Хранение исторических данных/Задание 1',
        'de05030801auth.sql',
        'exec_user_sql'
    ),
    (
        'de05030802',
        'Тема',
        'de05030802auth.sql',
        'exec_user_sql'
    ),
    (
        'de05030803',
        'Тема',
        'de05030803auth.sql',
        'exec_user_sql'
    ),
    (
        'de05030804',
        'Тема',
        'de05030804auth.sql',
        'exec_user_sql'
    ),
    (
        'de05030805',
        'Тема',
        'de05030805auth.sql',
        'exec_user_sql'
    ),
    (
        'de05030806',
        'Тема',
        'de05030806auth.sql',
        'exec_user_sql'
    ),
    (
        'de05030807',
        'Тема',
        'de05030807auth.sql',
        'exec_user_sql'
    ),
    (
        'de05030808',
        'Тема',
        'de05030808auth.sql',
        'exec_user_sql'
    ),
    (
        'de05030809',
        'Тема',
        'de05030809auth.sql',
        'exec_user_sql'
    ),
    (
        'de05030810',
        'Тема',
        'de05030810auth.sql',
        'exec_user_sql'
    ),
    (
        'de05030901',
        'Тема',
        'de05030901auth.sql'
    ),
)

LESSON_TESTS_PATH = '/app/sprint-5-tests'

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
    from de_s5_tests import run_tests

    for test in DE_S5_TESTS:
        DE_S5_TEST = test[0]
        print(DE_S5_TEST, ' - ', test[1], end='')
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
            de_s5_test=DE_S5_TEST,
            realization_file=realization_file
        )
        print(result)

if __name__ == '__main__':
    all_tests()
