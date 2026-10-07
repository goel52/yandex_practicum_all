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

    
    # импортировать
    sys.path.append(full_lesson_path)

    try:
        user_py = importlib.import_module(realization_file[:-3])
    except Exception as e:
        return False, f'\n{TerminalColors.WARNING}{e.__class__.__name__}\n\n{e}{TerminalColors().ENDC}\n'

    try:
        conn = user_py.conn
    except AttributeError:
            return False, f'\n{TerminalColors.WARNING}Не найдена переменная `conn`{TerminalColors.ENDC}' 
    except Exception as e:
        return False, f'\n{TerminalColors.WARNING}{e}{TerminalColors.ENDC}' 

    try:
        if conn.dsn != 'user=jovyan password=xxx dbname=de host=localhost port=5432':
            return False, f'\n{TerminalColors.WARNING}Параметры подключения должны быть `user=jovyan password=jovyan dbname=de host=localhost port=5432`{TerminalColors.ENDC}'

    except AttributeError:
         traceback.print_exc()

    except Exception as e:
        return False, e

    return True, None
    