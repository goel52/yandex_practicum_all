import sys

from airflow.hooks.base_hook import BaseHook

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


    try:
        with open('/dev/null', 'w') as f:
            sys.stdout = f
            pg_conn = BaseHook.get_connection("pg_connection")
    except Exception as e:
        return False, f'\n{e}\n'
    finally:
        sys.stdout = sys.__stdout__

    auth_host = 'localhost'
    auth_port = 5432
    auth_login = 'jovyan'
    auth_password = 'jovyan'

    if pg_conn.host != auth_host:
        return False, f'\n{TerminalColors.WARNING}Укажите хост `{auth_host}` {TerminalColors().ENDC}\n'
    
    if pg_conn.port != auth_port:
        return False, f'\n{TerminalColors.WARNING}Укажите порт `{auth_port}` {TerminalColors().ENDC}\n'
    
    if pg_conn.login != auth_login:
        return False, f'\n{TerminalColors.WARNING}Укажите логин `{auth_login}` {TerminalColors().ENDC}\n'
    
    if pg_conn.password != auth_password:
        return False, f'\n{TerminalColors.WARNING}Укажите пароль `{auth_password}` {TerminalColors().ENDC}\n'
    
    return True, True