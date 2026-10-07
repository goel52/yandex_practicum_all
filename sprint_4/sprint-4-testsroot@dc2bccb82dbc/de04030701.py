import os
import sys
import importlib
import traceback
from datetime import datetime

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
        try:
            with open('/dev/null', 'w') as f:
                sys.stdout = f
                user_py = importlib.import_module(realization_file[:-3])
        except Exception as e:
            traceback.print_exc()
            return False, f'\n{e}\n'
        finally:
            sys.stdout = sys.__stdout__

        pass
       # default_args
        if 'owner' not in user_py.dag.default_args.keys():
            return False, f'У default_args не найден ключ `owner`'
        
        if  user_py.dag.default_args['owner'] != 'airflow':
            return False, f'default_args[`owner`] != `airflow`'
        
        if  user_py.dag.default_args['conn_id'] != 'postgres_default':
            return False, f'default_args[`conn_id`] != `postgres_default`'
        
        if user_py.dag.schedule_interval != '@daily':
            return False, f'Параметр schedule_interval != `@daily`'

        if user_py.dag.catchup != False:
            return False, f'Параметр catchup != False'

        # begin
        if user_py.begin.__class__.__name__ != 'DummyOperator':
            return False, f'begin != DummyOperator(...)'

        if user_py.begin.task_id != 'begin':
            return False, f'begin.task_id != `begin`'

        # f1
        if user_py.f1.task_id != 'group1.waiting_for_file_customer_research':
            return False, f'f1.task_id != `waiting_for_file_customer_research`'

        if user_py.f1.fs_conn_id != 'fs_local':
            return False, f'f1.fs_conn_id != `fs_local`'

        if user_py.f1.filepath != (str(datetime.now().date()) + 'customer_research.csv'):
            return False, f'f1.filepath != str(datetime.now().date()) + "customer_research.csv"'

        if user_py.f1.poke_interval != 5:
            return False, f'f1.poke_interval != 5'

        if user_py.f1.on_success_callback.__name__ != 'check_success_file_customer_research':
            return False, f'f1.on_success_callback != check_success_file_customer_research'

        if user_py.f1.on_failure_callback.__name__ != 'check_failure_file_customer_research':
            return False, f'f1.on_failure_callback != check_failure_file_customer_research'

        # f2
        if user_py.f2.task_id != 'group1.waiting_for_file_user_order_log':
            return False, f'f2.task_id != `waiting_for_file_user_order_log`'

        if user_py.f2.fs_conn_id != 'fs_local':
            return False, f'f2.fs_conn_id != `fs_local`'

        if user_py.f2.filepath != (str(datetime.now().date()) + 'user_order_log.csv'):
            return False, f'f2.filepath != str(datetime.now().date()) + "user_order_log.csv"'

        if user_py.f2.poke_interval != 5:
            return False, f'f2.poke_interval != 5'

        if user_py.f2.on_success_callback.__name__ != 'check_success_file_user_order_log':
            return False, f'f2.on_success_callback != check_success_file_user_order_log'

        if user_py.f2.on_failure_callback.__name__ != 'check_failure_file_user_order_log':
            return False, f'f2.on_failure_callback != check_failure_file_user_order_log'

        # f3
        if user_py.f3.task_id != 'group1.waiting_for_file_user_activity_log':
            return False, f'f3.task_id != `waiting_for_file_user_activity_log`'

        if user_py.f3.fs_conn_id != 'fs_local':
            return False, f'f3.fs_conn_id != `fs_local`'

        if user_py.f3.filepath != (str(datetime.now().date()) + 'user_activity_log.csv'):
            return False, f'f3.filepath != str(datetime.now().date()) + "user_activity_log.csv"'

        if user_py.f3.poke_interval != 5:
            return False, f'f3.poke_interval != 5'

        if user_py.f3.on_success_callback.__name__ != 'check_success_file_user_activity_log':
            return False, f'f3.on_success_callback != check_success_file_user_activity_log'

        if user_py.f3.on_failure_callback.__name__ != 'check_failure_file_user_activity_log':
            return False, f'f3.on_failure_callback != check_failure_file_user_activity_log'


        
        # load_customer_research
        if user_py.load_customer_research.__class__.__name__ != 'PythonOperator':
            return False, f'load_customer_research != PythonOperator(...)'

        if user_py.load_customer_research.task_id != 'group2.load_customer_research':
            return False, f'load_customer_research.task_id != `load_customer_research`'

        if user_py.load_customer_research.python_callable.__name__ != 'load_file_to_pg':
            return False, f'load_customer_research.python_callable != load_file_to_pg'

        if user_py.load_customer_research.op_kwargs['filename'] != str(datetime.now().date()) + "customer_research.csv":
            return False, f'load_customer_research.op_kwargs[`filename`] != str(datetime.now().date()) + "customer_research.csv"'

        if user_py.load_customer_research.op_kwargs['pg_table'] != 'staging.customer_research':
            return False, f'load_customer_research.op_kwargs[`pg_table`] != `staging.customer_research`'

        # load_user_order_log
        if user_py.load_user_order_log.__class__.__name__ != 'PythonOperator':
            return False, f'load_user_order_log != PythonOperator(...)'

        if user_py.load_user_order_log.task_id != 'group2.load_user_order_log':
            return False, f'load_user_order_log.task_id != `load_user_order_log`'

        if user_py.load_user_order_log.python_callable.__name__ != 'load_file_to_pg':
            return False, f'load_user_order_log.python_callable != load_file_to_pg'

        if user_py.load_user_order_log.op_kwargs['filename'] != str(datetime.now().date()) + "user_order_log.csv":
            return False, f'load_user_order_log.op_kwargs[`filename`] != str(datetime.now().date()) + "user_order_log.csv"'

        if user_py.load_user_order_log.op_kwargs['pg_table'] != 'staging.user_order_log':
            return False, f'load_user_order_log.op_kwargs[`pg_table`] != `staging.user_order_log`'

        # load_user_activity_log
        if user_py.load_user_activity_log.__class__.__name__ != 'PythonOperator':
            return False, f'load_user_activity_log != PythonOperator(...)'

        if user_py.load_user_activity_log.task_id != 'group2.load_user_activity_log':
            return False, f'load_user_activity_log.task_id != `load_user_activity_log`'

        if user_py.load_user_activity_log.python_callable.__name__ != 'load_file_to_pg':
            return False, f'load_user_activity_log.python_callable != load_file_to_pg'

        if user_py.load_user_activity_log.op_kwargs['filename'] != str(datetime.now().date()) + "user_activity_log.csv":
            return False, f'load_user_activity_log.op_kwargs[`filename`] != str(datetime.now().date()) + "user_activity_log.csv"'

        if user_py.load_user_activity_log.op_kwargs['pg_table'] != 'staging.user_activity_log':
            return False, f'load_user_activity_log.op_kwargs[`pg_table`] != `staging.user_activity_log`'

        # load_price_log
        if user_py.load_price_log.__class__.__name__ != 'PythonOperator':
            return False, f'load_price_log != PythonOperator(...)'

        if user_py.load_price_log.task_id != 'group2.load_price_log':
            return False, f'load_price_log.task_id != `load_price_log`'

        if user_py.load_price_log.python_callable.__name__ != 'load_file_to_pg':
            return False, f'load_price_log.python_callable != load_file_to_pg'

        if user_py.load_price_log.op_kwargs['filename'] != str(datetime.now().date()) + "price_log.csv":
            return False, f'load_price_log.op_kwargs[`filename`] != str(datetime.now().date()) + "price_log.csv"'

        if user_py.load_price_log.op_kwargs['pg_table'] != 'staging.price_log':
            return False, f'load_price_log.op_kwargs[`pg_table`] != `staging.price_log`'

        

        #sql_check
        if user_py.sql_check.__class__.__name__ != 'SQLCheckOperator':
            return False, f'sql_check != SQLCheckOperator(...)'

        if user_py.sql_check.task_id != 'group2.user_order_log_isNull':
            return False, f'sql_check.task_id != `user_order_log_isNull`'

        if user_py.sql_check.sql != 'user_order_log_isNull_check.sql':
            return False, f'sql_check.sql != `user_order_log_isNull_check.sql`'

        if user_py.sql_check.on_success_callback.__name__ != 'check_success_insert_user_order_log':
            return False, f'sql_check.on_success_callback != check_success_insert_user_order_log'

        if user_py.sql_check.on_failure_callback.__name__ != 'check_failure_insert_user_order_log':
            return False, f'sql_check.on_failure_callback != check_failure_insert_user_order_log'

        #sql_check 2
        if user_py.sql_check2.__class__.__name__ != 'SQLCheckOperator':
            return False, f'sql_check2 != SQLCheckOperator(...)'

        if user_py.sql_check2.task_id != 'group2.user_activity_log_isNull':
            return False, f'sql_check2.task_id != `user_activity_log_isNull`'

        if user_py.sql_check2.sql != 'user_activity_log_isNull_check.sql':
            return False, f'sql_check2.sql != `user_activity_log_isNull_check.sql`'

        if user_py.sql_check2.on_success_callback.__name__ != 'check_success_insert_user_activity_log':
            return False, f'sql_check2.on_success_callback != check_success_insert_user_activity_log'

        if user_py.sql_check2.on_failure_callback.__name__ != 'check_failure_insert_user_activity_log':
            return False, f'sql_check2.on_failure_callback != check_failure_insert_user_activity_log'

        # sql_check 3
        if user_py.sql_check3.__class__.__name__ != 'SQLValueCheckOperator':
            return False, f'sql_check3 != SQLValueCheckOperator(...)'

        if user_py.sql_check3.task_id != 'group2.check_row_count_user_order_log':
            return False, f'sql_check3.task_id != `check_row_count_user_order_log`'

        if ' '.join(user_py.sql_check3.sql.lower().split()) != 'select count(distinct(customer_id)) from user_order_log':
            return False, f'sql_check3.sql != `Select count(distinct(customer_id)) from user_order_log`'

        if user_py.sql_check3.pass_value != '3':
            return False, f'sql_check3.pass_value != 3'
            
        if user_py.sql_check3.on_success_callback.__name__ != 'check_success_insert_user_order_log2':
            return False, f'sql_check3.on_success_callback != check_success_insert_user_order_log2'

        if user_py.sql_check3.on_failure_callback.__name__ != 'check_failure_insert_user_order_log2':
            return False, f'sql_check3.on_failure_callback != check_failure_insert_user_order_log2'

        # # sql_check 4
        if user_py.sql_check4.__class__.__name__ != 'SQLValueCheckOperator':
            return False, f'sql_check4 != SQLValueCheckOperator(...)'

        if user_py.sql_check4.task_id != 'group2.check_row_count_user_activity_log':
            return False, f'sql_check4.task_id != `check_row_count_user_activity_log`'

        if ' '.join(user_py.sql_check4.sql.lower().split()) != 'select count(distinct(customer_id)) from user_activity_log':
            return False, f'sql_check4.sql != `Select count(distinct(customer_id)) from user_activity_log`'

        if user_py.sql_check4.pass_value != '3':
            return False, f'sql_check4.pass_value != 3'

        if user_py.sql_check4.on_success_callback.__name__ != 'check_success_insert_user_activity_log2':
            return False, f'sql_check4.on_success_callback != check_success_insert_user_activity_log2'

        if user_py.sql_check4.on_failure_callback.__name__ != 'check_failure_insert_user_activity_log2':
            return False, f'sql_check4.on_failure_callback != check_failure_insert_user_activity_log2'

        # >>
        if (
            user_py.sql_check.upstream_task_ids == {'group2.load_user_order_log'} and
            user_py.sql_check3.upstream_task_ids == {'group2.load_user_order_log'}
        ) != True:
            return False, f'Добавьте выражение load_user_order_log >> [sql_check , sql_check3 ]'

        if (
            user_py.sql_check2.upstream_task_ids == {'group2.load_user_activity_log'} and
            user_py.sql_check4.upstream_task_ids == {'group2.load_user_activity_log'}
        ) != True:
            return False, f'Добавьте выражение load_user_activity_log >> [sql_check2 , sql_check4 ]'


        # end
        if user_py.end.__class__.__name__ != 'DummyOperator':
            return False, f'end != DummyOperator(...)'

        if user_py.end.task_id != 'end':
            return False, f'end.task_id != `end`'

        # >>
        # if (
        #     user_py.fg1.upstream_task_ids == {'begin'} and
        #     user_py.fg2.upstream_task_ids == {
        #         'group1.waiting_for_file_customer_research',
        #         'group1.waiting_for_file_user_order_log',
        #         'group1.waiting_for_file_user_activity_log',
        #         'group1.waiting_for_file_price_log',
        #     } and
        #     user_py.end.upstream_task_ids == {
        #         'group2.user_order_log_isNull',
        #         'group2.load_customer_research',
        #         'group2.check_row_count_user_activity_log',
        #         'group2.check_row_count_user_order_log',
        #         'group2.user_activity_log_isNull',
        #         'group2.load_price_log',
        #     }
        #     ) != True:
        #     return False, f'Добавьте выражение begin >> fg1 >> fg2 >> end'

    except Exception as e:
        return False, f'\n{TerminalColors.WARNING}{e.__class__.__name__}\n\n{e}{TerminalColors().ENDC}\n'

    return True, None
    