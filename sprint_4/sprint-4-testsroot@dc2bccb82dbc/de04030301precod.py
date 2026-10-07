from airflow.models import DAG
from airflow.sensors.filesystem import FileSensor
from datetime import datetime

default_args = {
    "start_date": datetime(2020, 1, 1),
    "owner": "airflow"
}

with DAG(
    dag_id="Sprin4_Task31",
    schedule_interval="@daily",
    default_args=default_args,
    catchup=False
    ) as dag:
 
    # Вам необходимо заполнить только эту секцию с сенсором
    waiting_for_file = FileSensor(
        task_id="XXX",  # имя задачи
        fs_conn_id="XXX", # имя соединения
        filepath="XXX",  # путь к файлу
        poke_interval=XXX
    )

    waiting_for_file