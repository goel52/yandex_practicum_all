from airflow import DAG
from airflow.providers.http.operators.http import SimpleHttpOperator
from airflow.hooks.base import BaseHook
from airflow.operators.python import PythonOperator

import datetime
import requests
import pandas as pd
import os
import psycopg2, psycopg2.extras

dag = DAG(
    dag_id='583_postgresql_mart_update',
    schedule_interval='0 0 * * *',
    start_date=datetime.datetime(2021, 1, 1),
    catchup=False,
    dagrun_timeout=datetime.timedelta(minutes=60),
    tags=['example', 'example2'],
    params={"example_key": "example_value"},
)
business_dt = {'dt':'2022-05-06'}

###POSTGRESQL settings###
#set postgresql connectionfrom basehook
pg_conn = BaseHook.get_connection('pg_connection')

##init test connection
conn = psycopg2.connect(f"dbname='de' port='{pg_conn.port}' user='{pg_conn.login}' host='{pg_conn.host}' password='{pg_conn.password}'")
cur = conn.cursor()
cur.close()
conn.close()




#3. обновление таблиц d по загруженным данным в staging-слой

def update_mart_d_tables(ti):
    #connection to database
    psql_conn = BaseHook.get_connection('pg_connection')
    conn = psycopg2.connect(f"dbname='de' port='{psql_conn.port}' user='{psql_conn.login}' host='{psql_conn.host}' password='{psql_conn.password}'")
    cur = conn.cursor()

    #d_calendar
    cur.execute(*ваш код здесь*)
    conn.commit()


    #d_customer
    cur.execute(*ваш код здесь*)
    conn.commit()


    #d_item
    cur.execute(*ваш код здесь*)
    conn.commit()

    cur.close()
    conn.close()

    return 200

#4. обновление витрин (таблицы f)
def update_mart_f_tables(ti):
    #connection to database
    psql_conn = BaseHook.get_connection('pg_connection')
    conn = psycopg2.connect(*ваш код здесь*)
    cur = conn.cursor()

    #f_activity
    cur.execute(*ваш код здесь*)
    conn.commit()


    #f_daily_sales
    cur.execute(*ваш код здесь*)
    conn.commit()

    cur.close()
    conn.close()


    return 200


t_update_mart_d_tables = PythonOperator(task_id='update_mart_d_tables',
                                        python_callable=update_mart_d_tables,
                                        dag=dag)


t_update_mart_f_tables = PythonOperator(task_id='update_mart_f_tables',
                                        python_callable=update_mart_f_tables,
                                        dag=dag)


t_update_mart_d_tables >> t_update_mart_f_tables