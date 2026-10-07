
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator  # Импортируем оператор

default_args = {
    'owner': 'airflow',
    'concurrency': 1,
    'retries': 2,
    'retry_delay': timedelta(seconds=5),
}


def print_weekday(**kwargs):
    date = kwargs['date']
    day = datetime.strptime(date, '%d.%m.%Y')
    weekday = day.weekday()
    print('current weekday number is: ', weekday)


with DAG('python_operator_example',
         default_args=default_args,
         start_date=datetime(2024, 1, 1),
         max_active_runs=1,
         catchup=True) as dag:  # Создаём объект DAG

    weekday_task = PythonOperator(task_id='weekday_task',
                                  python_callable=print_weekday,
                                  op_kwargs={'date': '01.01.2000'}
                                  # Обратите внимание, что функция не вызывается, а передаётся
                                  )

    weekday_task