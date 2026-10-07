import json
from airflow.providers.amazon.aws.hooks.s3 import S3Hook

def de_test(
        full_lesson_path: str,
        realization_file='realization.py',
        sql_author=None,
        dsn='postgresql://jovyan:jovyan@localhost:5432/de'):

    try:
        s3client = S3Hook.get_connection(conn_id='conn_s3')

        extra_js = json.loads(s3client.extra)

        if extra_js['aws_access_key_id'] != '<YC_ACCESS_KEY_ID>':
            return False, f'Connection id `{s3client.conn_id}` должен иметь поле extra с параметрами {"aws_access_key_id": "<YC_ACCESS_KEY_ID>", "aws_secret_access_key": "<YC_SECRET_ACCESS_KEY>"}'

        if extra_js['aws_secret_access_key'] != '<YC_SECRET_ACCESS_KEY>':
            return False, f'Connection id `{s3client.conn_id}` должен иметь поле extra с параметрами {"aws_access_key_id": "<YC_ACCESS_KEY_ID>", "aws_secret_access_key": "<YC_SECRET_ACCESS_KEY>"}'



    except Exception as e:
        if "`s3_conn` isn't defined" in str(e):
            return False, f'Не найден Connection id `conn_s3`'

        return False, f'\n{e}\n'

    return True, True