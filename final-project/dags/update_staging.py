from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
#from airflow.contrib.hooks.vertica_hook import VerticaHook
import logging, datetime, vertica_python, csv

postgres_conn_id = 'pg_conn'

#��������� ��������� ��� vertica �� ����������, ����� ��������� ���������� ���
conn_info = {'host': '51.250.75.20', 
             'port': '5433',
             'user': 'OARTEMOV1976YANDEXRU',       
             'password': '0312hjDnuiLz0FG',
             'database': 'dwh',
             'autocommit': True
}

temp_file_path = '/tmp'
args = {
    'owner': 'oartemov',
    'email': ['oartemov1976@yandex.ru'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 0
}
log = logging.getLogger(__name__)

# ������� ��������� ������ �� �������� ��� �� ������ PostgreSQL � CSV, ����� �������� �� CSV � �� Vertica
# date_from - ���� ������ 
# date_to - ���� ��������� (������� <, �.�. ��� ������ - timestamp)
# table_name - ��� �������
# date_field - ����, ���������� ����
def get_increment(date_from, date_to, table_name, date_field):
    postgres_hook = PostgresHook(postgres_conn_id)
    conn = postgres_hook.get_conn()
    cursor = conn.cursor()
    date_from = date_from.strftime('%Y-%m-%d')
    date_to = date_to.strftime('%Y-%m-%d')
    sql = f'select * from {table_name} where {date_field} >= \'{date_from}\' and {date_field} < \'{date_to}\''
    log.info(sql)
    cursor.execute(sql)
    result = cursor.fetchall()
    
    filename = f'{temp_file_path}/{table_name}.csv'
    csv_file = open(filename, 'w')
    csv_writer = csv.writer(csv_file)
    fields = [i[0] for i in cursor.description]
    #csv_writer.writerow(fields)
    csv_writer.writerows(result)
    log.info('%s rows fetched' % len(result))

    with vertica_python.connect(**conn_info) as conn:
        cur = conn.cursor()
        cur.execute(f'TRUNCATE TABLE __STAGING.{table_name}')
        copy_stmt = f'''COPY __STAGING.{table_name} ({','.join(fields)} )
        FROM LOCAL '{filename}'
        DELIMITER ','
        REJECTED DATA AS TABLE __STAGING.{table_name}_rej;'''
        log.info(copy_stmt)
        cur.execute(copy_stmt)

with DAG(
        'update_staging',
        default_args=args,
        description='DAG for final project',
        catchup=True,
        start_date=datetime.datetime.today() - datetime.timedelta(days=1),
        end_date=datetime.datetime.today() + datetime.timedelta(days=1),
        schedule_interval='@daily'
) as dag:    

    # ����� �����
    get_currencies = PythonOperator(
        task_id='get_currencies',
        python_callable=get_increment,
        op_kwargs={'date_from': datetime.datetime.today() - datetime.timedelta(days=1),
                   'date_to': datetime.datetime.today(),
                   'table_name': 'currencies',
                   'date_field': 'date_update'
                  }
        )
    
    # ����������
    get_transactions = PythonOperator(
        task_id='get_transactions',
        python_callable=get_increment,
        op_kwargs={'date_from': datetime.datetime.today() - datetime.timedelta(days=1),
                   'date_to': datetime.datetime.today(),
                   'table_name': 'transactions',
                   'date_field': 'transaction_dt'
                  }
        )

    get_currencies >> get_transactions