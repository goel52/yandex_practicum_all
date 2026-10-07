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
    pd.set_option('display.max_colwidth', -1)

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
                DROP SCHEMA IF EXISTS dds_test CASCADE;
                CREATE SCHEMA dds_test;
                create table dds_test.fct_product_sales
                (
                    id            serial primary key,
                    product_id    integer                  not null,
                    order_id      integer                  not null,
                    count         integer        default 0 not null
                        constraint fct_product_sales_count_check
                            check (count >= 0),
                    price         numeric(14, 2) default 0 not null
                        constraint fct_product_sales_price_check
                            check (price >= (0)::numeric),
                    total_sum     numeric(14, 2) default 0 not null
                        constraint fct_product_sales_total_sum_check
                            check (total_sum >= (0)::numeric),
                    bonus_payment numeric(14, 2) default 0 not null
                        constraint fct_product_sales_bonus_payment_check
                            check (bonus_payment >= (0)::numeric),
                    bonus_grant   numeric(14, 2) default 0 not null
                        constraint fct_product_sales_bonus_grant_check
                            check (bonus_grant >= (0)::numeric)
                );

            '''
            cur.execute(sql_create_tab)
            # проверки
            sql_auth_check_t = '''
                SELECT
                    table_name,
                    column_name,
                    data_type
                FROM information_schema.columns
                WHERE table_name = 'fct_product_sales'
                and table_schema = 'dds_test'
                and (column_name = 'id' and udt_name = 'int4' and column_default LIKE 'nextval%' and is_nullable = 'NO'
                    or column_name = 'product_id' and udt_name = 'int4' and is_nullable = 'NO'
                    or column_name = 'order_id' and udt_name = 'int4' and is_nullable = 'NO'
                    or column_name = 'count' and udt_name = 'int4' and is_nullable = 'NO' and column_default = '0'
                    or column_name = 'price' and udt_name = 'numeric' and is_nullable = 'NO' and numeric_precision = 14 and
                    numeric_scale = 2 and column_default = '0'
                    or column_name = 'total_sum' and udt_name = 'numeric' and is_nullable = 'NO' and numeric_precision = 14 and
                    numeric_scale = 2 and column_default = '0'
                    or column_name = 'bonus_payment' and udt_name = 'numeric' and is_nullable = 'NO' and numeric_precision = 14 and
                    numeric_scale = 2 and column_default = '0'
                    or column_name = 'bonus_grant' and udt_name = 'numeric' and is_nullable = 'NO' and numeric_precision = 14 and
                    numeric_scale = 2 and column_default = '0'
                    );
            '''
            sql_auth_check_c = '''
                select
                    cc.constraint_name,
                    check_clause
                from information_schema.check_constraints cc
                        join information_schema.table_constraints tc
                            ON tc.constraint_catalog = cc.constraint_catalog and tc.constraint_schema = cc.constraint_schema and
                                tc.constraint_name = cc.constraint_name
                where tc.table_schema = 'dds_test'
                and tc.table_name = 'fct_product_sales'
                and cc.check_clause in
                    ('((count >= 0))', '((price >= (0)::numeric))', '((total_sum >= (0)::numeric))',
                    '((bonus_payment >= (0)::numeric))', '((bonus_grant >= (0)::numeric))');
            '''
            sql_user_check_t = '''
                SELECT
                    table_name,
                    column_name,
                    data_type
                FROM information_schema.columns
                WHERE table_name = 'fct_product_sales'
                and table_schema = 'dds'
                and (column_name = 'id' and udt_name = 'int4' and column_default LIKE 'nextval%' and is_nullable = 'NO'
                    or column_name = 'product_id' and udt_name = 'int4' and is_nullable = 'NO'
                    or column_name = 'order_id' and udt_name = 'int4' and is_nullable = 'NO'
                    or column_name = 'count' and udt_name = 'int4' and is_nullable = 'NO' and column_default = '0'
                    or column_name = 'price' and udt_name = 'numeric' and is_nullable = 'NO' and numeric_precision = 14 and
                    numeric_scale = 2 and column_default = '0'
                    or column_name = 'total_sum' and udt_name = 'numeric' and is_nullable = 'NO' and numeric_precision = 14 and
                    numeric_scale = 2 and column_default = '0'
                    or column_name = 'bonus_payment' and udt_name = 'numeric' and is_nullable = 'NO' and numeric_precision = 14 and
                    numeric_scale = 2 and column_default = '0'
                    or column_name = 'bonus_grant' and udt_name = 'numeric' and is_nullable = 'NO' and numeric_precision = 14 and
                    numeric_scale = 2 and column_default = '0'
                    );

            '''
            sql_user_check_c = '''
                select
                    cc.constraint_name,
                    check_clause
                from information_schema.check_constraints cc
                        join information_schema.table_constraints tc
                            ON tc.constraint_catalog = cc.constraint_catalog and tc.constraint_schema = cc.constraint_schema and
                                tc.constraint_name = cc.constraint_name
                where tc.table_schema = 'dds'
                and tc.table_name = 'fct_product_sales'
                and cc.check_clause in
                    ('((count >= 0))', '((price >= (0)::numeric))', '((total_sum >= (0)::numeric))',
                    '((bonus_payment >= (0)::numeric))', '((bonus_grant >= (0)::numeric))');
            '''

            cur.execute(sql_auth_check_t)
            col_author = cur.description
            r_author = cur.fetchall()

            # проверка решения юзера

            cur.execute(sql_user_check_t)
            col_user = cur.description
            r_user = cur.fetchall()

            cmp_res = compare_result(r_user, col_user, r_author, col_author, False)

            if cmp_res[0] == False:
                flag, err = cmp_res
                sql_drop_auth = '''
                    DROP SCHEMA IF EXISTS dds_test CASCADE;
                '''
                cur.execute(sql_drop_auth)
                return flag, err

            cur.execute(sql_auth_check_c)
            col_author = cur.description
            r_author = cur.fetchall()
            
            cur.execute(sql_user_check_c)
            col_user = cur.description
            r_user = cur.fetchall()

            cmp_res = compare_result(r_user, col_user, r_author, col_author, False)

            sql_drop_auth = '''
                DROP SCHEMA IF EXISTS dds_test CASCADE;
            '''
            cur.execute(sql_drop_auth)

    except FileNotFoundError:
        error_message = (f'Не найден файл с решением {realization_file}')
        return False, error_message
    except Exception as e:
        error_message = (str(e))
        return False, error_message
    else:
        flag, err = cmp_res
        return flag, err
        # return True, True



if __name__ == '__main__':
    full_less_p = os.path.dirname(os.path.abspath(__file__)).replace(
        'sprint-5-tests',
        's5-lessons/Тема3. Проектирование DWH/8. Проектирование слоя DDS/Задание 9'
    )
    print(de_test(
        full_less_p,
        'realization.sql',
        dsn='postgresql://jovyan:jovyan@localhost:15432/de'
    ))