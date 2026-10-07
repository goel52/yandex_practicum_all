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
    realization_file='realization.py'
    
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

       
        if 'owner' not in user_py.dag.default_args.keys():
            return False, f'У default_args не найден ключ `owner`'
        
        if  user_py.dag.default_args['owner'] != 'airflow':
            return False, f'default_args[`owner`] != `airflow`'
        
        if user_py.fg1.group_id != 'group1':
            return False, f'fg1.group_id != `group1`'

        if user_py.f1.task_id != 'group1.waiting_for_file_customer_research':
            return False, f'f1.task_id != `waiting_for_file_customer_research`'

        if user_py.f2.task_id != 'group1.waiting_for_file_user_order_log':
            return False, f'f2.task_id != `waiting_for_file_user_order_log`'

        if user_py.f3.task_id != 'group1.waiting_for_file_user_activity_log':
            return False, f'f3.task_id != `waiting_for_file_user_activity_log`'

        if user_py.f1.fs_conn_id != 'fs_local':
            return False, f'f1.fs_conn_id != `fs_local`'

        if user_py.f2.fs_conn_id != 'fs_local':
            return False, f'f2.fs_conn_id != `fs_local`'

        if user_py.f3.fs_conn_id != 'fs_local':
            return False, f'f3.fs_conn_id != `fs_local`'

        # Автор дал свободу, послабляем тест
        # Можно использовать такую конструкцию, чтобы записать имя файла:filepath=str(datetime.now().date())+ "_" + "_customer_research.csv”.  Но можно пользоваться и другой, удобной вам. 
        if 'customer_research.csv' not in user_py.f1.filepath:
            return False, f'f1.filepath не содержит "customer_research.csv"'

        if 'user_order_log.csv' not in user_py.f2.filepath:
            return False, f'f2.filepath не содержит "user_order_log.csv"'

        if 'user_activity_log.csv' not in user_py.f3.filepath:
            return False, f'f3.filepath не содержит "user_activity_log.csv"'

    except Exception as e:
        return False, f'\n{TerminalColors.WARNING}{e.__class__.__name__}\n\n{e}{TerminalColors().ENDC}\n'


    return True, None
    