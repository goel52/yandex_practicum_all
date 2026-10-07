import os
import sys
import importlib
import traceback

from template_comparsion.compare_with_template import prepare_code, compare_nodes, STR_TO_REPLACE

STR_TO_REPLACE = [
    'poke_interval=XXX',
]

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
        dsn='postgresql://jovyan:jovyan@localhost:5432/de',
        precod=None):

    # # проверка на нарушение прекода
    # if not precod:
    #     precod = f'{os.path.dirname(os.path.abspath(__file__))}/{__name__}precod.py'
    # # Подготовка темплейта к сравнению и инициализация логера ошибок
    # nodes_template, ErrorLog = prepare_code(precod, str_to_rpl=STR_TO_REPLACE)
    # # Подготовка кода студента к сравнению
    # nodes_user, _ = prepare_code(realization_file, is_template=False, ErrorLog=ErrorLog, str_to_rpl=STR_TO_REPLACE)
    # # Сравнение деревьев темплейта и студента (элементы темплейта должны быть в дереве студента)
    # compare_nodes(nodes_template, nodes_user, ErrorLog)



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
        
        if user_py.waiting_for_file.dag_id != 'Sprin4_Task1':
            return False, f'waiting_for_file.dag_id != `Sprin4_Task1`'

        if user_py.waiting_for_file.dag.schedule_interval != '@daily':
            return False, f'waiting_for_file.dag.schedule_interval != `@daily`'

        if user_py.waiting_for_file.dag.default_args != user_py.dag.default_args:
            return False, f'waiting_for_file.dag.default_args != default_args'

        if user_py.waiting_for_file.dag.catchup != False:
            return False, f'waiting_for_file.dag.catchup != False'

        # if user_py.waiting_for_file.task_id != 'waiting_for_file':
        #     return False, f'waiting_for_file.task_id != `waiting_for_file`'

        if user_py.waiting_for_file.fs_conn_id != 'fs_local':
            return False, f'waiting_for_file.fs_conn_id != `fs_local`'

        if user_py.waiting_for_file.filepath != '/data/test.txt':
            return False, f'waiting_for_file.filepath != `/data/test.txt`'

    except Exception as e:
        return False, f'\n{TerminalColors.WARNING}{e.__class__.__name__}\n\n{e}{TerminalColors().ENDC}\n'


    return True, None
    
