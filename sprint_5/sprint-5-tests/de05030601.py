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

    if order_sensitive:
        indexes = list(range(usr_cols))
        for i in range(usr_cols):
            match = False
            max_x = -1
            same_type = False
            for index_pos, j in enumerate(indexes):
                each = True
                for x in range(usr_rows):
                    if usr[x][i] != sol[x][j]:
                        each = False
                        if x > max_x:
                            max_x = x
                            same_type = usr_d[i].type_code == sol_d[j].type_code
                        break
                if each:
                    match = True
                    del indexes[index_pos]
                    break
            if not match:
                print_author_rows_dataset(0, sol_d, sol) #d_platform
                print_user_rows_dataset(0, usr_d, usr) #d_platform
                if same_type:
                    msg1 = 'Не верный результат'
                else:
                    msg1 = 'Не верный результат, проверьте тип'
                msg2 = ' | '.join([str(z) for z in usr[max_x]])
                msg_out = f'{msg1} стр. {max_x+1}, колонка {usr_d[i].name}, {msg2}'
                return False, msg_out

                # return False, (
                #     'Не верный результат' if same_type
                #     else 'Не верный результат, проверьте тип',
                #     max_x+1,
                #     usr_d[i].name,
                #     ' | '.join([str(z) for z in usr[max_x]])
                # )
    elif usr_rows != 0:
        # git difference
        sol_set = [set(x) for x in sol]
        err_conf = None
        all_perms = set()
        for usr_i, row in enumerate(usr):
            maxlen = 0
            very_similar = []
            for i, x in enumerate(sol_set):
                row_set = set(row)
                l = len(row_set & x)
                if l > 0:
                    if l == maxlen:
                        very_similar.append(i)
                    elif l > maxlen:
                        very_similar = [i]
                        maxlen = l
            if maxlen == 0:
                err_conf = (usr_i, 0, True)
                break
            # Convert all very similar to permutations
            permutations = set()
            for i in very_similar:
                permutations.update(
                    best_permutation(row, sol[i], 0,
                                     list(range(usr_cols)), []))
            if all_perms == set():
                all_perms = permutations
            else:
                all_perms &= permutations

            if len(all_perms) == 0:
                err_conf = (usr_i, 0, True)
                break
            if len(all_perms) == 1:
                break

        # Now if we have more than one permutation - they are all equal
        if err_conf is None:
            perm = all_perms.pop()
            # Get solution in right column order
            sol2 = [tuple(
                        [x[perm[i]] for i in range(usr_cols)])
                    for x in sol]
            # Check usr in sol
            for i in range(len(usr)):
                x = usr[i]
                try:
                    i_sol = sol2.index(x)
                except ValueError:
                    max_len = -1
                    max_r = None
                    for r in sol2:
                        l = len(set(x) & set(r))
                        if l > max_len:
                            max_len = l
                            max_r = r
                    for j in range(usr_cols):
                        if x[j] != max_r[j]:
                            same_type = usr_d[j].type_code == sol_d[perm[j]].type_code
                            err_conf = (i, j, same_type)
                            break
                    break
                sol2.pop(i_sol)
        if err_conf is not None:
            i, j, same_type = err_conf
            column = usr_d[j].name,
            row = i,
            data = ' | '.join([str(z) for z in usr[i]]),
            if same_type:
                error_message = f'\nПолученный результат не совпадает с ожидаемым (в частности столбец `{column[0]}`, строка `{row[0]}`\n{data[0]}).\n'
            else:
                error_message = f'\nПолученный результат не совпадает с ожидаемым, проверьте тип (в частности столбец `{column[0]}`, строка `{row[0]}`\n{data[0]}).\n'
            print_author_rows_dataset(row[0], sol_d, sol) #d_platform
            print_user_rows_dataset(row[0], usr_d, usr) #d_platform
            return False, error_message

    return True, None

def clear_comments(query):
    clear_query = ''
    for lines_query in query.splitlines():
        if lines_query.strip() and lines_query.strip()[0:2] != '--':
            clear_query += lines_query + '\n'
    return clear_query

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
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)
    pd.set_option('display.max_colwidth', None)

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

    try:

        with psycopg2.connect(dsn=dsn) as conn:
            conn.autocommit = True
            cur = conn.cursor()

            # подготовка базы для проверки решения
            sql_create_tab = '''
                DROP SCHEMA IF EXISTS tttest CASCADE;
                CREATE SCHEMA tttest;
                CREATE TABLE tttest.dm_settlement_report (
                    id serial not null,
                    restaurant_id varchar not null,
                    restaurant_name varchar not null,
                    settlement_date date not null,
                    orders_count integer not null,
                    orders_total_sum numeric(14, 2) not null,
                    orders_bonus_payment_sum numeric(14, 2) not null,
                    orders_bonus_granted_sum numeric(14, 2) not null,
                    order_processing_fee numeric(14, 2) not null,
                    restaurant_reward_sum numeric(14, 2) not null
                );
            '''
            # cur.execute('CREATE SCHEMA IF NOT EXISTS cdm;')
            # cur.execute('DROP SCHEMA IF EXISTS test CASCADE;')
            # cur.execute('CREATE SCHEMA test;')
            # cur.execute('''
            #     CREATE TABLE test.dm_settlement_report (
            #         id serial not null,
            #         restaurant_id integer not null,
            #         restaurant_name varchar not null,
            #         settlement_year smallint not null,
            #         settlement_month smallint not null,
            #         orders_count integer not null,
            #         orders_total_sum numeric(14, 2) not null,
            #         orders_bonus_payment_sum numeric(14, 2) not null,
            #         orders_bonus_granted_sum numeric(14, 2) not null,
            #         order_processing_fee numeric(14, 2) not null,
            #         restaurant_reward_sum numeric(14, 2) not null
            #     );
            # ''')
            cur.execute(sql_create_tab)
            # проверки
            sql_auth_check = '''
                SELECT
                    column_name,
                    data_type,
                    is_nullable
                FROM
                    information_schema.columns
                WHERE
                    table_name = 'dm_settlement_report' and
                    table_schema = 'tttest';
            '''
            sql_user_check = '''
                SELECT
                    column_name,
                    data_type,
                    is_nullable
                FROM
                    information_schema.columns
                WHERE
                    table_name = 'dm_settlement_report' and
                    table_schema = 'cdm';
            '''

            cur.execute(sql_auth_check)
            col_author = cur.description
            r_author = cur.fetchall()

            sql_drop_auth = '''
                DROP SCHEMA IF EXISTS tttest CASCADE;
            '''
            cur.execute(sql_drop_auth)

            # проверка решения юзера

            sql_file_user = f'{full_lesson_path}/{realization_file}'
            sql_user = open(sql_file_user, 'r').read()

            cur.execute(sql_user)

            cur.execute(sql_user_check)
            col_user = cur.description
            r_user = cur.fetchall()

        cmp_res = compare_result(r_user, col_user, r_author, col_author, False)

    except FileNotFoundError:
        error_message = (f'Не найден файл с решением {realization_file}')
        return False, error_message
    except Exception as e:
        error_message = (str(e))
        return False, error_message
    else:
        flag, err = cmp_res
        return flag, err

if __name__ == '__main__':
    full_less_p = os.path.dirname(os.path.abspath(__file__)).replace(
        'sprint-5-tests',
        's5-lessons/Тема3. Проектирование DWH/6. Проектирование слоя/Задание 1'
    )
    print(de_test(
        full_less_p,
        'realization.sql',
        dsn='postgresql://jovyan:jovyan@localhost:15432/de'
    ))