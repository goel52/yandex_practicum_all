from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
from sql.global_metrics_script import fetch_exchange_rates, update_global_metrics

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
    'update_global_metrics',
    default_args=default_args,
    description='Update global metrics in Vertica',
    schedule_interval=timedelta(days=1),
)

fetch_exchange_rates_task = PythonOperator(
    task_id='fetch_exchange_rates',
    provide_context=True,
    python_callable=fetch_exchange_rates,
    dag=dag,
)

update_global_metrics_task = PythonOperator(
    task_id='update_global_metrics',
    provide_context=True,
    python_callable=update_global_metrics,
    dag=dag,
)

fetch_exchange_rates_task >> update_global_metrics_task
