import sys

from airflow.hooks.base import BaseHook

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

    auth_host_1 = 'rc1a-1kn18k47wuzaks6h.mdb.yandexcloud.net'
    auth_port_1 = 6432
    auth_extra_1 = '{"sslmode": "require"}'
    auth_conn_type_1 = 'postgres'
    auth_schema_1 = 'de-public'
    auth_login_1 = 'student'
    auth_password_1 = 'student1'

    auth_host_2 = 'localhost'
    auth_port_2 = 5432
    auth_conn_type_2 = 'postgres'
    auth_schema_2 = 'de'
    auth_login_2 = 'jovyan'
    auth_password_2 = 'jovyan'

    try:
        with open('/dev/null', 'w') as f:
            sys.stdout = f
            c_1 = BaseHook.get_connection('PG_ORIGIN_BONUS_SYSTEM_CONNECTION')
            c_2 = BaseHook.get_connection('PG_WAREHOUSE_CONNECTION')
    except Exception as e:
        return False, f'\n{e}\n'
    finally:
        sys.stdout = sys.__stdout__

    if c_1.host != auth_host_1:
        return False, f'\n{TerminalColors.WARNING}Хост {c_1.conn_id} указан не верно, укажите {auth_host_1}.{TerminalColors().ENDC}\n'

    if c_2.host != auth_host_2:
        return False, f'\n{TerminalColors.WARNING}Хост {c_2.conn_id} указан не верно, укажите {auth_host_2}.{TerminalColors().ENDC}\n'

    if c_1.port != auth_port_1:
        return False, f'\n{TerminalColors.WARNING}Порт {c_1.conn_id} указан не верно, укажите {auth_port_1}.{TerminalColors().ENDC}\n'

    if c_2.port != auth_port_2:
        return False, f'\n{TerminalColors.WARNING}Порт {c_2.conn_id} указан не верно, укажите {auth_port_2}{TerminalColors().ENDC}\n'

    if c_1.extra != auth_extra_1:
        return False, f'\n{TerminalColors.WARNING}Параметры `extra` для {c_1.conn_id} указаны не верно, укажите {auth_extra_1}.{TerminalColors().ENDC}\n'
    
    if c_1.conn_type != auth_conn_type_1:
        return False, f'\n{TerminalColors.WARNING}Параметр `Connection Type` для {c_1.conn_id} указан не верно, укажите {auth_conn_type_1}.{TerminalColors().ENDC}\n'

    if c_2.conn_type != auth_conn_type_2:
        return False, f'\n{TerminalColors.WARNING}Параметр `Connection Type` для {c_2.conn_id} указан не верно, укажите {auth_conn_type_2}.{TerminalColors().ENDC}\n'

    if c_1.schema != auth_schema_1:
        return False, f'\n{TerminalColors.WARNING}Параметр `Schema`для {c_1.conn_id} указан не верно, укажите {auth_schema_1}.{TerminalColors().ENDC}\n'
 
    if c_2.schema != auth_schema_2:
        return False, f'\n{TerminalColors.WARNING}Параметр `Schema`для {c_2.conn_id}  указан не верно, укажите {auth_schema_2}.{TerminalColors().ENDC}\n'

    if c_1.login != auth_login_1:
        return False, f'\n{TerminalColors.WARNING}Логин для {c_1.conn_id} указан не верно, укажите {auth_login_1}.{TerminalColors().ENDC}\n'
    
    if c_2.login != auth_login_2:
        return False, f'\n{TerminalColors.WARNING}Логин для {c_2.conn_id} указан не верно, укажите {auth_login_2}.{TerminalColors().ENDC}\n'

    if c_1.password != auth_password_1:
        return False, f'\n{TerminalColors.WARNING}Пароль для {c_1.conn_id} указан не верно, укажите {auth_password_1}.{TerminalColors().ENDC}\n'
    
    if c_2.password != auth_password_2:
        return False, f'\n{TerminalColors.WARNING}Пароль для {c_2.conn_id} указан не верно, укажите {auth_password_2}.{TerminalColors().ENDC}\n'

    return True, None
    
if __name__ == '__main__':
    print(de_test('')[0], de_test('')[1])