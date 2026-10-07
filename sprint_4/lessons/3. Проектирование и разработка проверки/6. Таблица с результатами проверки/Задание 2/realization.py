from airflow import DAG
from airflow.sensors.filesystem import FileSensor
from datetime import datetime
from airflow.utils.task_group import TaskGroup
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.sql import (
    SQLCheckOperator,
    SQLValueCheckOperator,
)


# для таблицы user_order_log первая проверка
def check_success_insert_user_order_log (context):
    insert_dq_checks_results = PostgresOperator(
        task_id="success_insert_user_order_log",
        sql="""
            INSERT INTO dq_checks_results
            values ('user_order_log', 'user_order_log_isNull' ,current_date, 0 )
          """
    )

# def check_failure_insert_user_order_log (context):
	# Допишите код

# для таблицы user_activity_log первая проверка
# def check_success_insert_user_activity_log (context):
	# Допишите код
 
# def check_failure_insert_user_activity_log (context):
	# Допишите код

# для таблицы user_order_log вторая проверка
# def check_success_insert_user_order_log2 (context):
	# Допишите код

# def check_failure_insert_user_order_log2 (context):
	# Допишите код

# для таблицы user_activity_log вторая проверка
# def check_success_insert_user_activity_log2 (context):
	# Допишите код
# def check_failure_insert_user_activity_log2 (context):
	# Допишите код

default_args = {
    "start_date": datetime(2020, 1, 1),
    "owner": "airflow",
    "conn_id": "postgres_default"
}



with DAG(dag_id="Sprin4_Task61", schedule_interval="@daily", default_args=default_args, catchup=False) as dag:

    begin = DummyOperator(task_id="begin")
    sql_check = SQLCheckOperator(task_id="user_order_log_isNull", sql="user_order_log_isNull_check.sql" , on_success_callback = check_success_insert_user_order_log, on_failure_callback =  check_failure_insert_user_order_log )
    sql_check2 = # Допишите код
    sql_check3 = # Допишите код
    sql_check4 = # Допишите код 
    end = DummyOperator(task_id="end")

    begin >> [sql_check, sql_check2, sql_check3, sql_check4 ]>> end