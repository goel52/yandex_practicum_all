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


def best_permutation(r1, r2, i, idx, perm):
    found = False
    out = []
    if i == len(r1):
        l_idx = len(idx)
        if l_idx:
            for j in range(i):
                if perm[j] == 'x':
                    perm[j] = idx.pop()
        return [tuple(perm)]

    for j in idx:
        if r1[i] == r2[j]:
            found = True
            ndx = idx[:]
            ndx.remove(j)
            out += best_permutation(r1, r2, i + 1, ndx, perm + [j])
    if not found:
        out += best_permutation(r1, r2, i + 1, idx, perm + ['x'])
    return out

def compare_result(usr, usr_d, sol, sol_d, order_sensitive):
    usr_cols = len(usr_d)
    sol_cols = len(sol_d)
    usr_rows = len(usr)
    sol_rows = len(sol)
    if usr_cols > sol_cols:
        error_message = f'Количество столбцов больше ожидаемого. Ожидается: {sol_cols}'
        print_author_rows_dataset(0, sol_d, sol) #d_platform
        print_user_rows_dataset(0, usr_d, usr) #d_platform
        return False, error_message
    if usr_cols < sol_cols:
        error_message = f'Количество столбцов меньше ожидаемого. Ожидается: {sol_cols}'
        print_author_rows_dataset(0, sol_d, sol) #d_platform
        print_user_rows_dataset(0, usr_d, usr) #d_platform
        return False, error_message
    if usr_rows > sol_rows:
        error_message = f'Количество строк больше ожидаемого. Ожидается: {sol_rows}'
        print_author_rows_dataset(-1, sol_d, sol) #d_platform
        print_user_rows_dataset(-1, usr_d, usr) #d_platform
        return False, error_message
    if usr_rows < sol_rows:
        error_message = f'Количество строк меньше ожидаемого. Ожидается: {sol_rows}'
        print_author_rows_dataset(-1, sol_d, sol) #d_platform
        print_user_rows_dataset(-1, usr_d, usr) #d_platform
        return False, error_message
    return True, None

#d_platform
def print_user_rows_dataset(row = 0, col_user = None, r_user = None): 
    print('\nВывод результата пользователя:')
    print_rows_dataset(col_user, r_user, row)

#d_platform
def print_author_rows_dataset(row = 0, col_author = None, r_author = None): 
    print('\nОжидаемый результат:')
    print_rows_dataset(col_author, r_author, row)

#d_platform
def print_rows_dataset(col_ds, row_ds, row):
    count_col = len(col_ds)
    import pandas as pd
    pd.set_option('display.max_seq_items', 5)
    df = pd.DataFrame(
        row_ds,
        columns=[col_ds[n].name for n in range(count_col)]
    )
    start = 0
    end = len(row_ds)
    if end > 20 and row != -1:
        start = max(0, row-3)
        end = min(start + 18, end)
        print(f'<выведены строки с {start} по {end}>')

    if end:
        print(f'{TerminalColors.WARNING}\n{df.loc[start:end]}{TerminalColors.ENDC}')
    else:
        print(f'{TerminalColors.WARNING}\nТаблица не содержит данных{TerminalColors.ENDC}')

def de_test(
        full_lesson_path: str,
        realization_file='realization.sql',
        sql_author=None,
        dsn='postgresql://jovyan:jovyan@localhost:5432/de'):

    path_test = os.path.dirname(os.path.abspath(__file__))
  


    sql_user_file = f'{full_lesson_path}/{realization_file}'
    sql_user = open(sql_user_file, 'r').read()

    try:

        with psycopg2.connect(dsn=dsn) as conn:
            conn.autocommit = True
            cur = conn.cursor()

            cur.execute(sql_user)
            # col_user = cur.description
            # r_user = cur.fetchall()

            sql_c_d_calendar = 'select fact_date from mart.d_calendar'
            sql_c_d_customer = 'select first_name, last_name, city_id from mart.d_customer'
            sql_c_d_item = 'select item_name from mart.d_item'

            cur.execute(sql_c_d_calendar)
            col_user_calendar = cur.description
            r_user_calendar = cur.fetchall()

            cur.execute(sql_c_d_customer)
            col_user_customer = cur.description
            r_user_customer = cur.fetchall()

            cur.execute(sql_c_d_item)
            col_user_item = cur.description
            r_user_item = cur.fetchall()

            sql_author = '''
                delete from mart.f_activity;
                delete from mart.f_daily_sales;

                --d_calendar
                delete from mart.d_calendar;

                with all_dates as (
                        select distinct to_date(date_time::TEXT,'YYYY-MM-DD') as date_time from stage.user_activity_log
                        union
                        select distinct to_date(date_time::TEXT,'YYYY-MM-DD') from stage.user_order_log
                        union
                        select distinct to_date(date_id::TEXT,'YYYY-MM-DD') from stage.customer_research
                        order by date_time)
                INSERT INTO mart.d_calendar (date_id, fact_date, day_num, month_num, month_name,year_num)
                select 
                    distinct ROW_NUMBER () OVER (
                    ORDER BY date_time
                    ) as date_id
                    ,date_time as fact_date
                    ,EXTRACT(day from date_time)::INT as day_num
                    ,EXTRACT(month from date_time)::INT as month_num
                    ,to_char(date_time, 'Mon') as month_name
                    ,EXTRACT(year from date_time)::INT as year_num
                from all_dates;

                --d_customer
                delete from mart.d_customer;

                INSERT INTO mart.d_customer  (customer_id, first_name, last_name,city_id)
                select distinct customer_id
                        ,first_name
                        ,last_name
                        ,max (city_id)
                from stage.user_order_log 
                group by customer_id , first_name, last_name;

                --d_item
                delete from mart.d_item;

                INSERT INTO mart.d_item  (item_id, item_name)
                select distinct item_id
                        ,item_name
                from stage.user_order_log ;
                '''
            cur.execute(sql_author)

            cur.execute(sql_c_d_calendar)
            col_author_calendar = cur.description
            r_author_calendar = cur.fetchall()

            cur.execute(sql_c_d_customer)
            col_author_customer = cur.description
            r_author_customer = cur.fetchall()

            cur.execute(sql_c_d_item)
            col_author_item = cur.description
            r_author_item = cur.fetchall()

            sql_clear = '''
                delete from mart.d_calendar;
                delete from mart.d_customer;
                delete from mart.d_item;
            '''
            cur.execute(sql_clear)

            print('Проверка таблицы mart.d_calendar...')

            cmp_res = compare_result(
                r_user_calendar,
                col_user_calendar,
                r_author_calendar,
                col_author_calendar,
                False)
            
            if cmp_res[0] == False:
                return False, cmp_res[1]

            print('Проверка таблицы mart.d_customer...')

            cmp_res = compare_result(
                r_user_customer,
                col_user_customer,
                r_author_customer,
                col_author_customer,
                False)
            
            if cmp_res[0] == False:
                return False, cmp_res[1]

            print('Проверка таблицы mart.d_item...')

            cmp_res = compare_result(
                r_user_item,
                col_user_item,
                r_author_item,
                col_author_item,
                False)

            if cmp_res[0] == False:
                return False, cmp_res[1]

            cur.execute(sql_author) # восстанавливаем данные

    except FileNotFoundError:
        error_message = (f'Не найден файл с решением {realization_file}')
        return False, error_message
    except Exception as e:
        error_message = (str(e))
        return False, error_message
    else:
        flag, err = cmp_res
        return flag, err
