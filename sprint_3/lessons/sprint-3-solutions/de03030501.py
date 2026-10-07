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
        realization_file='realization.sql',
        sql_author=None,
        dsn='postgresql://jovyan:jovyan@localhost:5432/de'):

    auth_host = 'd5dg1j9kt695d30blp03.apigw.yandexcloud.net'

    try:
        with open('/dev/null', 'w') as f:
            sys.stdout = f
            c = BaseHook.get_connection("create_files_api")
    except Exception as e:
        return False, f'\n{e}\n'
    finally:
        sys.stdout = sys.__stdout__

    if c.host != auth_host:
        return False, f'\n{TerminalColors.WARNING}Укажите хост `{auth_host}` {TerminalColors().ENDC}\n'

    return True, None
    