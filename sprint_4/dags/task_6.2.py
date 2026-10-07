from airflow import DAG
from airflow.sensors.filesystem import FileSensor
from datetime import datetime
from airflow.utils.task_group import TaskGroup
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.sql import (
    SQLCheckOperator,
    SQLValueCheckOperator,
)
from airflow.providers.postgres.operators.postgres import PostgresOperator

import pandas as pd



# для таблицы user_order_log первая проверка
def check_success_insert_user_order_log (context):
    insert_dq_checks_results = PostgresOperator(
        task_id="success_insert_user_order_log",
        postgres_conn_id = PostgreSQL_conn_id, 
        sql="""insert into stage.dq_checks_results (Table_name, DQ_check_name, Datetime, DQ_check_result) values ('user_order_log', 'user_order_log_isNull', current_timestamp, 0);"""
    )

def check_failure_insert_user_order_log (context):
    insert_dq_checks_results = PostgresOperator(
        task_id="failure_insert_user_order_log",
        postgres_conn_id = PostgreSQL_conn_id, 
        sql='''
            insert into Stage.dq_checks_results (Table_name, DQ_check_name, Datetime, DQ_check_result)
            values ('user_order_log', 'user_order_log_isNull', current_timestamp, 1)
        '''
    )

# для таблицы user_activity_log первая проверка
def check_success_insert_user_activity_log (context):
	insert_dq_checks_results = PostgresOperator(
        task_id="success_insert_user_activity_log",
        postgres_conn_id = PostgreSQL_conn_id, 
        sql='''
            insert into Stage.dq_checks_results (Table_name, DQ_check_name, Datetime, DQ_check_result)
            values ('user_activity_log', 'user_activity_log_isNull', current_timestamp, 0)
        '''
    )
 
def check_failure_insert_user_activity_log (context):
	insert_dq_checks_results = PostgresOperator(
        task_id="failure_insert_user_activity_log",
        postgres_conn_id = PostgreSQL_conn_id, 
        sql='''
            insert into Stage.dq_checks_results (Table_name, DQ_check_name, Datetime, DQ_check_result)
            values ('user_activity_log', 'user_activity_log_isNull', current_timestamp, 1)
        '''
    )

# для таблицы user_order_log вторая проверка
def check_success_insert_user_order_log2 (context):
	insert_dq_checks_results = PostgresOperator(
        task_id="success_insert_user_order_log2",
        postgres_conn_id = PostgreSQL_conn_id, 
        sql='''
            insert into Stage.dq_checks_results (Table_name, DQ_check_name, Datetime, DQ_check_result)
            values ('user_order_log', 'check_row_count_user_order_log', current_timestamp, 0)
        '''
    )

def check_failure_insert_user_order_log2 (context):
	insert_dq_checks_results = PostgresOperator(
        task_id="failure_insert_user_order_log2",
        postgres_conn_id = PostgreSQL_conn_id, 
        sql='''
            insert into Stage.dq_checks_results (Table_name, DQ_check_name, Datetime, DQ_check_result)
            values ('user_order_log', 'check_row_count_user_order_log', current_timestamp, 1)
        '''
    )

# для таблицы user_activity_log вторая проверка
def check_success_insert_user_activity_log2 (context):
	insert_dq_checks_results = PostgresOperator(
        task_id="success_insert_user_activity_log2",
        postgres_conn_id = PostgreSQL_conn_id, 
        sql='''
            insert into Stage.dq_checks_results (Table_name, DQ_check_name, Datetime, DQ_check_result)
            values ('user_activity_log', 'check_row_count_user_activity_log', current_timestamp, 0)
        '''
    )

def check_failure_insert_user_activity_log2 (context):
    insert_dq_checks_results = PostgresOperator(
        task_id="failure_insert_user_activity_log2",
        postgres_conn_id = PostgreSQL_conn_id, 
        sql='''
            insert into Stage.dq_checks_results (Table_name, DQ_check_name, Datetime, DQ_check_result)
            values ('user_activity_log', 'check_row_count_user_activity_log', current_timestamp, 1)
        '''
    )

default_args = {
    "start_date": datetime(2020, 1, 1),
    "owner": "airflow",
    "conn_id": "postgres_default"
}



with DAG(dag_id="Sprin4_Task61", schedule_interval="@daily", default_args=default_args, catchup=False) as dag:

    begin = DummyOperator(task_id="begin")

    sql_check = SQLCheckOperator(
        task_id="user_order_log_isNull", 
        conn_id = PostgreSQL_conn_id, 
        sql="sql/user_order_log_isNull_check.sql", 
        on_success_callback = check_success_insert_user_order_log, 
        on_failure_callback =  check_failure_insert_user_order_log 
    )

    sql_check2 = SQLCheckOperator(
        task_id="user_activity_log_isNull", # идентификатор задачи
        conn_id = PostgreSQL_conn_id,
        sql="sql/user_activity_log_isNull_check.sql", # имя файла с проверкой
        on_success_callback = check_success_insert_user_activity_log, 
        on_failure_callback =  check_failure_insert_user_activity_log 
    )
    
    sql_check3 = SQLValueCheckOperator(
        task_id="check_row_count_user_order_log", 
        conn_id = PostgreSQL_conn_id,
        sql="Select count(distinct(customer_id)) from user_order_log", 
        pass_value=3,
        on_success_callback = check_success_insert_user_order_log2, 
        on_failure_callback =  check_failure_insert_user_order_log2
        #tolerance=0.01
    ) 

    sql_check4 = SQLValueCheckOperator(
        task_id="check_row_count_user_activity_log", 
        conn_id = PostgreSQL_conn_id,
        sql="Select count(distinct(customer_id)) from user_activity_log", 
        pass_value=3,
        on_success_callback = check_success_insert_user_activity_log2, 
        on_failure_callback =  check_failure_insert_user_activity_log2 
        #tolerance=0.01
    ) 

    end = DummyOperator(task_id="end")

    begin >> [sql_check, sql_check2, sql_check3, sql_check4 ]>> end