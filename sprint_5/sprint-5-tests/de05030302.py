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
                DROP TABLE IF EXISTS clients CASCADE;
                DROP TABLE IF EXISTS products CASCADE;
                DROP TABLE IF EXISTS sales CASCADE;

                CREATE TABLE clients
                (
                    client_id INTEGER NOT NULL
                        CONSTRAINT clients_pk PRIMARY KEY,
                    name      TEXT    NOT NULL,
                    login     TEXT    NOT NULL
                );

                CREATE TABLE products
                (
                    product_id INTEGER        NOT NULL
                        CONSTRAINT products_pk PRIMARY KEY,
                    name       TEXT           NOT NULL,
                    price      NUMERIC(14, 2) NOT NULL
                );

                CREATE TABLE sales
                (
                    client_id  INTEGER        NOT NULL
                        CONSTRAINT sales_clients_client_id_fk REFERENCES clients,
                    product_id INTEGER        NOT NULL
                        CONSTRAINT sales_products_product_id_fk REFERENCES products,
                    amount     INTEGER        NOT NULL,
                    total_sum  NUMERIC(14, 2) NOT NULL,
                    CONSTRAINT sales_pk PRIMARY KEY (client_id, product_id)
                );
            '''
            cur.execute(sql_create_tab)

            sql_check_1 = '''
                SELECT
                    tc.table_name,
                    tc.table_schema,
                    tc.constraint_type,
                    column_default,
                    c.column_name,
                    c.udt_name
                FROM information_schema.table_constraints AS tc
                        JOIN information_schema.key_column_usage AS kcu
                            ON tc.constraint_name = kcu.constraint_name
                                AND tc.table_schema = kcu.table_schema
                        JOIN information_schema.columns AS c
                            ON tc.table_name = c.table_name
                                AND kcu.column_name = c.column_name
                WHERE tc.table_name = 'products'
                AND tc.table_schema = 'public'
                AND tc.constraint_type = 'PRIMARY KEY'
                AND column_default LIKE 'nextval%'
                AND c.column_name = 'id'
                AND c.udt_name = 'int4';

            '''
            sql_check_2 = '''
                SELECT tc.table_name,
                    kcu.column_name,
                    ccu.table_name  AS foreign_table_name,
                    ccu.column_name AS foreign_column_name
                FROM information_schema.table_constraints AS tc
                        JOIN information_schema.key_column_usage AS kcu
                            ON tc.constraint_name = kcu.constraint_name
                                AND tc.table_schema = kcu.table_schema
                        JOIN information_schema.constraint_column_usage AS ccu
                            ON ccu.constraint_name = tc.constraint_name
                                AND ccu.table_schema = tc.table_schema
                WHERE tc.constraint_type = 'FOREIGN KEY'
                AND tc.table_schema = 'public'
                AND ccu.table_schema = 'public'
                AND (
                            tc.table_name = 'clients' OR
                            tc.table_name = 'products' OR
                            tc.table_name = 'sales'
                    );
            '''
            sql_check_3 = '''
                SELECT
                    table_name,
                    table_schema,
                    column_name,
                    udt_name
                FROM information_schema.columns
                WHERE table_name = 'products'
                AND table_schema = 'public'
                AND column_name in ('valid_from', 'valid_to')
                AND udt_name = 'timestamptz';
            
            '''
            # выполнение скрипта студента и проверок
            sql_file_user = f'{full_lesson_path}/{realization_file}'
            sql_user = open(sql_file_user, 'r').read()

            cur.execute(sql_user)

            # проверка 1
            cur.execute(sql_check_1)
            col_user_1 = cur.description
            r_user_1 = cur.fetchall()

            # проверка 2
            cur.execute(sql_check_2)
            col_user_2 = cur.description
            r_user_2 = cur.fetchall()

            # проверка 3
            cur.execute(sql_check_3)
            col_user_3 = cur.description
            r_user_3 = cur.fetchall()

            # пересоздание таблиц и тоже но с авторским решением
            cur.execute(sql_create_tab)

            sql_author = '''
                alter table sales drop constraint sales_products_product_id_fk;

                alter table products drop constraint products_pk;

                alter table products add id serial;

                alter table products add constraint products_pk primary key (id);

                alter table products add valid_from timestamptz;

                alter table products add valid_to timestamptz;

                alter table sales add constraint sales_products_id_fk foreign key (product_id) references products;
            '''
            cur.execute(sql_author)

            # проверка 1
            cur.execute(sql_check_1)
            col_auth_1 = cur.description
            r_auth_1 = cur.fetchall()

            # проверка 2
            cur.execute(sql_check_2)
            col_auth_2 = cur.description
            r_auth_2 = cur.fetchall()

            # проверка 3
            cur.execute(sql_check_3)
            col_auth_3 = cur.description
            r_auth_3 = cur.fetchall()

            cmp_res = compare_result(
                r_user_1,
                col_user_1,
                r_auth_1,
                col_auth_1,
                False
            )
            
            if not cmp_res[0]:
                print('Выполнен проверочный запрос:', sql_check_1)
                return False, f'\nРешение не верное\n'

            cmp_res = compare_result(
                r_user_2,
                col_user_2,
                r_auth_2,
                col_auth_2,
                False
            )
            
            if not cmp_res[0]:
                print('Выполнен проверочный запрос:', sql_check_2)
                return False, f'\nРешение не верное\n'

            cmp_res = compare_result(
                r_user_3,
                col_user_3,
                r_auth_3,
                col_auth_3,
                False
            )
            
            if not cmp_res[0]:
                print('Выполнен проверочный запрос:', sql_check_3)
                return False, f'\nРешение не верное\n'

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
        's5-lessons/Тема3. Проектирование DWH/3. Хранение исторических данных/Задание 2'
    )
    print(de_test(
        full_less_p,
        'realization.sql',
        dsn='postgresql://jovyan:jovyan@localhost:15432/de'
    ))