from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
from sql.stg_dwh_script import load_to_stg, load_to_dwh

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2022, 10, 2),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'load_to_stg_and_dwh',
    default_args=default_args,
    description='Load data from PostgreSQL to STG and then to DWH in Vertica',
    schedule_interval=timedelta(days=1),
)

load_to_stg_task = PythonOperator(
    task_id='load_to_stg',
    provide_context=True,
    python_callable=load_to_stg,
    dag=dag,
)

load_to_dwh_task = PythonOperator(
    task_id='load_to_dwh',
    provide_context=True,
    python_callable=load_to_dwh,
    dag=dag,
)

load_to_stg_task >> load_to_dwh_task