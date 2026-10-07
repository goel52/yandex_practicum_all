from airflow.models import DAG
from airflow.sensors.filesystem import FileSensor
from airflow.operators.dummy import DummyOperator
from airflow.utils.task_group import TaskGroup
from airflow.operators.sql import SQLCheckOperator, SQLValueCheckOperator
from datetime import datetime

default_args = {
    "start_date": datetime(2020, 1, 1),
    "owner": "airflow",
    "conn_id": "postgres_default"
}

with DAG(
    dag_id="Sprin4_Task1",
    schedule_interval="@daily",
    default_args=default_args,
    catchup=False
) as dag:
 
    # Шаг 1: Start - пустой шаг-заглушка
    start = DummyOperator(
        task_id="Start"
    )
    
    # Шаг 2: Группа из трёх сенсоров
    with TaskGroup(group_id='waiting_for_files') as fg1:
        f1 = FileSensor(
            task_id="waiting_for_file_customer_research", 
            fs_conn_id="fs_local", 
            filepath="customer_research.csv", 
            poke_interval=30
        )
        f2 = FileSensor(
            task_id="waiting_for_file_user_order_log", 
            fs_conn_id="fs_local", 
            filepath="user_order_log.csv", 
            poke_interval=30
        )
        f3 = FileSensor(
            task_id="waiting_for_file_user_activity_log", 
            fs_conn_id="fs_local", 
            filepath="user_activity_log.csv", 
            poke_interval=30
        )
    
    # Проверка № 2
    sql_check = SQLCheckOperator(
        task_id="user_order_log_isNull",
        sql="user_order_log_isNull_check.sql"
    )

    sql_check2 = SQLCheckOperator(
        task_id="user_activity_log_isNull",
        sql="user_activity_log_isNull_check.sql"
    )

    # Проверка № 3
    sql_check3 = SQLValueCheckOperator(
        task_id="check_row_count_user_order_log",
        sql="Select count(distinct(customer_id)) from user_order_log",
        pass_value=3,
        tolerance=0
    )

    sql_check4 = SQLValueCheckOperator(
        task_id="check_row_count_user_activity_log",
        sql="Select count(distinct(customer_id)) from user_activity_log",
        pass_value=3,
        tolerance=0
    )
    
    # Шаг 3: Finish - пустой шаг-заглушка
    finish = DummyOperator(
        task_id="Finish"
    )
    


    # Строка СТРОГО без финиша в конце:
    sql_check >> sql_check2 >> sql_check3 >> sql_check4