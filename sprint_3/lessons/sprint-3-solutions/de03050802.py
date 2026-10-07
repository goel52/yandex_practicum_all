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

            sql_c_f_activity = 'select date_id, click_number from mart.f_activity'
            sql_c_f_daily_sales = 'SELECT date_id, item_id, customer_id, price, quantity, payment_amount FROM mart.f_daily_sales'

            cur.execute(sql_c_f_activity)
            col_user_activity = cur.description
            r_user_activity = cur.fetchall()

            cur.execute(sql_c_f_daily_sales)
            col_user_daily_sales = cur.description
            r_user_daily_sales = cur.fetchall()

            if len(r_user_activity) == 0:
                return False, f'Скрипт не наполнил данными таблицу mart.f_activity'
            if len(r_user_daily_sales) == 0:
                return False, f'Скрипт не наполнил данными таблицу mart.f_daily_sales'

            sql_author = '''
                --f_activity
                delete from mart.f_activity;

                INSERT INTO mart.f_activity (activity_id, date_id, click_number)
                select  ual.action_id,
                        dc.date_id,
                        sum(ual.quantity) as click_number
                from stage.user_activity_log as ual
                left join mart.d_calendar as dc on to_date(ual.date_time::TEXT,'YYYY-MM-DD') = dc.fact_date
                group by ual.action_id, dc.date_id;

                --f_daily_sales
                delete from mart.f_daily_sales;

                INSERT INTO mart.f_daily_sales  (date_id, item_id, customer_id , price , quantity , payment_amount)
                select
                    dc.date_id,
                    uol.item_id,
                    uol.customer_id,
                    avg(uol.payment_amount / quantity) as price,
                    sum(uol.quantity),
                    sum(uol.payment_amount)
                from stage.user_order_log as uol
                left join mart.d_calendar as dc on to_date(uol.date_time::TEXT,'YYYY-MM-DD') = dc.fact_date
                group by dc.date_id,uol.item_id,uol.customer_id;
            '''
            cur.execute(sql_author)

            cur.execute(sql_c_f_activity)
            col_author_activity = cur.description
            r_author_activity = cur.fetchall()

            cur.execute(sql_c_f_daily_sales)
            col_author_daily_sales = cur.description
            r_author_daily_sales = cur.fetchall()

            sql_clear = '''
                delete from mart.f_activity;
                delete from mart.f_daily_sales;
            '''
            cur.execute(sql_clear)

            print('Проверка таблицы mart.f_activity...')

            cmp_res = compare_result(
                r_user_activity,
                col_user_activity,
                r_author_activity,
                col_author_activity,
                False)
            
            if cmp_res[0] == False:
                return False, cmp_res[1]

            print('Проверка таблицы mart.f_daily_sales...')

            cmp_res = compare_result(
                r_user_daily_sales,
                col_user_daily_sales,
                r_author_daily_sales,
                col_author_daily_sales,
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
