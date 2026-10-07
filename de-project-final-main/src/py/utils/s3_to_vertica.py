import os
import logging

import boto3
import vertica_python

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("s3_to_vertica")

def upload_to_vertica(table, filepath, vertica_conn):
    """Universal vertica uploader"""

    vertica_conn_params = {
        'host': vertica_conn.host,
        'port': vertica_conn.port,
        'user': vertica_conn.login,
        'password': vertica_conn.password,
        'database': vertica_conn.schema,
        'autocommit': True}

    with vertica_python.connect(**vertica_conn_params) as conn:
        cur = conn.cursor()
        cur.execute(f'''
                    COPY MIKEPAFYANDEXRU__STAGING.{table}
                    FROM LOCAL '{filepath}'
                    DELIMITER ','
                    REJECTED DATA AS TABLE {table}_rejected           
                    ''')

                    
def s3_to_vertica(s3_conn, vertica_conn):
    """Main function"""
    session = boto3.session.Session()
    s3_client = session.client(
        service_name='s3',
        endpoint_url=s3_conn.host,
        aws_access_key_id=s3_conn.extra_dejson.get('aws_access_key_id'),
        aws_secret_access_key=s3_conn.extra_dejson.get('aws_secret_access_key')
        )
    bucket = s3_conn.schema

    for object in s3_client.list_objects(Bucket=bucket)['Contents']:
        filename = object['Key']
        if filename.endswith('.csv'):
            log.info(f'Downloading: {filename}')
            s3_folder = 's3_stg'
            if not os.path.exists(s3_folder):
                os.makedirs(s3_folder)
            filepath = os.path.join(s3_folder, filename)

            s3_client.download_file(
                Bucket=bucket,
                Key=filename,
                Filename=filepath
            )
            log.info(f'Saved at: {filepath}')

            # Filling transactions temporary table
            if filename.startswith('transactions'):
                log.info(f'{filename} defined as transactions')
                upload_to_vertica('transactions_tmp_s3', filepath, vertica_conn)
            elif filename.startswith('currencies'):
                log.info(f'{filename} defined as currencies')
                upload_to_vertica('currencies_tmp_s3', filepath, vertica_conn)

            # Removing extracted file to avoid duplicates
            if os.path.exists(filepath):
                os.remove(filepath)
            log.info('File removed')
