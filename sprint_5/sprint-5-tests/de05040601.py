from airflow.models.variable import Variable

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

    try:
        #------------------------------------
        # затем в коде дага получить значения
        cert_path = Variable.get("MONGO_DB_CERTIFICATE_PATH")
        db_user = Variable.get("MONGO_DB_USER")
        db_pw = Variable.get("MONGO_DB_PASSWORD")
        rs = Variable.get("MONGO_DB_REPLICA_SET")
        db = Variable.get("MONGO_DB_DATABASE_NAME")
        hosts = Variable.get("MONGO_DB_HOST")

        cert_path_auth = '/opt/airflow/certificates/PracticumSp5MongoDb.crt'
        db_user_auth = 'student'
        db_pw_auth = 'student1'
        rs_auth = 'rs01'
        hosts_auth = 'rc1a-ba83ae33hvt4pokq.mdb.yandexcloud.net:27018'
        db_auth = 'db-mongo'

        message_start = 'Значение переменной Airflow не соответствует требованиям задания:'

        if cert_path != cert_path_auth:
            return False, f'{message_start} MONGO_DB_CERTIFICATE_PATH != {cert_path_auth}'
        
        if db_user != db_user_auth:
            return False, f'{message_start} MONGO_DB_USER != {db_user_auth}'

        if db_pw != db_pw_auth:
            return False, f'{message_start} MONGO_DB_PASSWORD != {db_pw_auth}'

        if rs != rs_auth:
            return False, f'{message_start} MONGO_DB_REPLICA_SET != {rs_auth}'

        if db != db_auth:
            return False, f'{message_start} MONGO_DB_DATABASE_NAME != {db_auth}'

        if hosts != hosts_auth:
            return False, f'{message_start} MONGO_DB_HOST != {hosts_auth}'

    except Exception as e:
        return False, f'\n{e}\n'

    return True, True


if __name__ == '__main__':
    print(de_test('')[0], de_test('')[1])