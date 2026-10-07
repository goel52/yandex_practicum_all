import requests
import json
from psycopg2.extras import execute_values
import logging
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.hooks.base import BaseHook
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.utils.task_group import TaskGroup

task_logger = logging.getLogger('airflow.task')

# подключение к ресурсам
api_conn = BaseHook.get_connection('api_conn')
postgres_conn = 'PG_DWH'
dwh_hook = PostgresHook(postgres_conn)

# параметры API
nickname = 'TEST'
cohort = '1'
api_key = json.loads(api_conn.extra)['api_key']
base_url = api_conn.host

headers = {"X-Nickname" : nickname,
         'X-Cohort' : cohort,
         'X-API-KEY' : api_key,
         }
         
def upload_deliveries(pg_schema, pg_table, start_date, end_date):

    conn = dwh_hook.get_conn()
    cursor = conn.cursor()
    
    # параметры фильтрации
    start = f"{start_date} 00:00:00"
    end = f"{end_date} 23:59:59"

    # идемпотентность
    dwh_hook.run(sql = f"DELETE FROM {pg_schema}.{pg_table} WHERE order_ts::date BETWEEN '{start_date}' AND '{end_date}'")

	# получение данных
    offset = 0
    while True:    
        deliver_rep = requests.get(f'https://{base_url}/deliveries/?sort_field=order_ts&sort_direction=asc&from={start}&to={end}&offset={offset}',
                            headers = headers).json()
		
		# останавливаемся, когда данные закончились
        if len(deliver_rep) == 0:
            conn.commit()
            cursor.close()
            conn.close()
            task_logger.info(f'Writting {offset} rows')
            break

        # запись в БД
        columns = ','.join([i for i in deliver_rep[0]])
        values = [[value for value in deliver_rep[i].values()] for i in range(len(deliver_rep))]

        sql = f"INSERT INTO {pg_schema}.{pg_table} ({columns}) VALUES %s"
        execute_values(cursor, sql, values)

        offset += len(deliver_rep)  

def upload_couriers(pg_schema, pg_table):

    conn = dwh_hook.get_conn()
    cursor = conn.cursor()
    
    # идемпотентность
    dwh_hook.run(sql = f"DELETE FROM {pg_schema}.{pg_table}")

   
    offset = 0
    while True:    
        couriers_rep = requests.get(f'https://{base_url}/couriers/?sort_field=_id&sort_direction=asc&offset={offset}',
                            headers = headers).json()

        if len(couriers_rep) == 0:
            conn.commit()
            cursor.close()
            conn.close()
            task_logger.info(f'Writting {offset} rows')
            break

        
        columns = ','.join([i for i in couriers_rep[0]])
        values = [[value for value in couriers_rep[i].values()] for i in range(len(couriers_rep))]

        sql = f"INSERT INTO {pg_schema}.{pg_table} ({columns}) VALUES %s"
        execute_values(cursor, sql, values)

        offset += len(couriers_rep)  


default_args = {
    'owner':'airflow',
    'retries':1,
    'retry_delay': timedelta (seconds = 60)
}


dag = DAG('01_dag_dwh_project',
        start_date=datetime(2022, 10, 15),
        catchup=True,
        schedule_interval='@daily',
        max_active_runs=1,
        default_args=default_args)

with TaskGroup(group_id = 'upload_stg', dag=dag) as upload_stg:

    upload_deliveries = PythonOperator(
                task_id = 'stg_deliveries',
                python_callable = upload_deliveries,
                op_kwargs = {
                    'pg_schema' : 'test_stg',
                    'pg_table' : 'deliveries',
                    'start_date' : '{{yesterday_ds}}',
                    'end_date' : '{{ds}}',
                },
                dag = dag
    )

    upload_couriers = PythonOperator(
                task_id = 'stg_couriers',
                python_callable = upload_couriers,
                op_kwargs = {
                    'pg_schema' : 'test_stg',
                    'pg_table' : 'couriers'
                },
                dag = dag
    )

with TaskGroup(group_id = 'upload_dm_dds', dag=dag) as upload_dm_dds:

    dm_upd = [
        PostgresOperator(
            task_id = f"{task[3:-4]}",
            postgres_conn_id = postgres_conn,
            sql = f"sql/{task}",
            dag = dag
    ) for task in ['01_dds_orders.sql', '02_dds_couriers.sql', '03_dds_deliveries.sql']
    ]

dds_fct_deliviries = PostgresOperator(
            task_id = 'dds_fct_deliviries',
            postgres_conn_id = postgres_conn,
            sql = 'sql/04_dds_fct_deliveries.sql',
            dag = dag
)

cdm_mart = PostgresOperator(
            task_id = 'cdm_mart',
            postgres_conn_id = postgres_conn,
            sql = 'sql/05_cdm_mart.sql',
            dag = dag
)

upload_stg >> upload_dm_dds >> dds_fct_deliviries >> cdm_mart