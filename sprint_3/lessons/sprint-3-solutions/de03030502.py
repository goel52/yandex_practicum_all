import os
import sys
import importlib
import traceback
import time


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

    
    # считать код юзера и добавить в add строки
    test_path = os.path.dirname(os.path.abspath(__file__))
    add_filename = 'de03030502add.py'
    test_filename = 'de03030502test.py'
    with open(f'{test_path}/{add_filename}', 'r') as file_add:
        with open(f'{full_lesson_path}/{realization_file}', 'r') as file_user:
            with open(f'{test_path}/{test_filename}', 'w') as file_test:
                file_test.write(file_add.read())
                file_test.write(file_user.read())

     
    # импортировать
    while os.path.isfile(f'{test_path}/{test_filename}') != True:
        print('.', end='')
        pass

    sys.path.append(test_path)

    try:
        user_py = importlib.import_module(test_filename[:-3])
    except Exception as e:
        traceback.print_exc()
        return False, f'\n{TerminalColors.WARNING}Исправьте ошибки в файле {realization_file}{TerminalColors.ENDC}\n'

    try:
        test = user_py.task
    except AttributeError:
            return False, f'\n{TerminalColors.WARNING}Не найдена переменная `task`{TerminalColors.ENDC}' 
    except Exception as e:
        return False, f'\n{TerminalColors.WARNING}{e}{TerminalColors.ENDC}' 

    try:
        # if user_py.task.task_id != 'whatever':
        #     return False, f'\n{TerminalColors.WARNING}Значение `task_id` != `whatever`{TerminalColors.ENDC}' 

        if user_py.task.http_conn_id != 'create_files_api':
            return False, f'\n{TerminalColors.WARNING}Значение `http_conn_id` != `create_files_api`{TerminalColors.ENDC}' 

        if user_py.task.method != 'POST':
            return False, f'\n{TerminalColors.WARNING}Значение `method` != `POST`{TerminalColors.ENDC}' 

        if user_py.task.data != {'dt': '2022-05-06'}:
            return False, f'\n{TerminalColors.WARNING}Ключ `data` != `business_dt`{TerminalColors.ENDC}' 
    
    except AttributeError:
         traceback.print_exc()

    except Exception as e:
        return False, e

    return True, None
    