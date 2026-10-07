from datetime import datetime

from airflow import DAG
from airflow.hooks.base_hook import BaseHook
from airflow.models.baseoperator import chain
from airflow.providers.vertica.operators.vertica import VerticaOperator

vertica_connection = BaseHook.get_connection('vertica_connection')
vertica_conn_id = vertica_connection.conn_id
vertica_user = vertica_connection.login
vertica_pass = vertica_connection.password

default_args = {
    'owner'     : 'mike.panfilov',
    'start_date': datetime(2022, 10, 1),
    'end_date': datetime(2022,10,31)
}

with DAG(dag_id = "data_mart_update",
                default_args=default_args,
                schedule_interval='@daily',
                catchup=True) as dag:

    global_metrics_daily_insert = VerticaOperator(
        task_id         = 'global_metrics_daily_insert',
        dag             = dag,
        vertica_conn_id = vertica_conn_id,
        sql             = '/sql_scripts/cdm_global_metrics_daily_insert.sql',
        params={
            'execution_date': '{{ds}}',
            },
        )