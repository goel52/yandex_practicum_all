import os
import sys
import importlib
import traceback

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

       
        if 'owner' not in user_py.dag.default_args.keys():
            return False, f'У default_args не найден ключ `owner`'
        
        if  user_py.dag.default_args['owner'] != 'airflow':
            return False, f'default_args[`owner`] != `airflow`'
        
        if  user_py.dag.default_args['conn_id'] != 'postgres_default':
            return False, f'default_args[`conn_id`] != `postgres_default`'
        
        if user_py.sql_check.task_id != 'user_order_log_isNull':
            return False, f'sql_check.task_id != `user_order_log_isNull`'

        if user_py.sql_check.sql != 'user_order_log_isNull_check.sql':
            return False, f'sql_check.sql != `user_order_log_isNull_check.sql`'

        if user_py.sql_check2.task_id != 'user_activity_log_isNull':
            return False, f'sql_check2.task_id != `user_activity_log_isNull`'

        if user_py.sql_check2.sql != 'user_activity_log_isNull_check.sql':
            return False, f'sql_check2.sql != `user_activity_log_isNull_check.sql`'

        if user_py.sql_check2.upstream_task_ids != {'user_order_log_isNull'}:
            return False, f'Добавьте выражение sql_check >> sql_check2'

    except Exception as e:
        return False, f'\n{TerminalColors.WARNING}{e.__class__.__name__}\n\n{e}{TerminalColors().ENDC}\n'

    return True, None
    