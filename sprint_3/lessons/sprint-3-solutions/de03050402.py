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


    test_path = os.path.dirname(os.path.abspath(__file__))
    add_filename = 'de03050402add.py'
    test_filename = 'de03050402test.py'
    with open(f'{test_path}/{add_filename}', 'r') as file_add:
        with open(f'{full_lesson_path}/{realization_file}', 'r') as file_user:
            with open(f'{test_path}/{test_filename}', 'w') as file_test:
                file_test.write(file_add.read())
                file_test.write(file_user.read())

    sys.path.append(test_path)

    try:
        try:
            with open('/dev/null', 'w') as f:
                sys.stdout = f
                user_py = importlib.import_module(test_filename[:-3])
        except Exception as e:
            traceback.print_exc()
            return False, f'\n{e}\n'
        finally:
            sys.stdout = sys.__stdout__

        # user_py.get_files_from_s3('dd-mm-yyy', 's3')

        download_files = os.walk(f'{full_lesson_path}')

        for root, dirs, files in download_files:
            if 'customer_research.csv' not in files:
                return False, f'\n{TerminalColors.WARNING}В каталоге `{root}` не найден файл `customer_research.csv`{TerminalColors.ENDC}'    
            if 'user_activity_log.csv' not in files:
                return False, f'\n{TerminalColors.WARNING}В каталоге `{root}` не найден файл `user_activity_log.csv`{TerminalColors.ENDC}'    
            if 'user_order_log.csv' not in files:
                return False, f'\n{TerminalColors.WARNING}В каталоге `{root}` не найден файл `user_order_log.csv`{TerminalColors.ENDC}'    


    except Exception as e:
        return False, f'\n{TerminalColors.WARNING}{e.__class__.__name__}\n\n{e}{TerminalColors().ENDC}\n'

    return True, None
