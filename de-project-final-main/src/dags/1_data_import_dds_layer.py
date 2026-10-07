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
    'start_date': datetime(2022, 10, 1)
}

with DAG(dag_id = "data_import_dds_layer",
                default_args=default_args,
                schedule_interval=None,
                catchup=False) as dag:

    h_currencies_insert = VerticaOperator(
        task_id         = 'h_currencies_insert',
        dag             = dag,
        vertica_conn_id = vertica_conn_id,
        sql             = '/sql_scripts/dds_h_currencies_insert.sql')

    h_operations_insert = VerticaOperator(
        task_id         = 'h_operations_insert',
        dag             = dag,
        vertica_conn_id = vertica_conn_id,
        sql             = '/sql_scripts/dds_h_operations_insert.sql')

    l_operation_currency_insert = VerticaOperator(
        task_id         = 'l_operation_currency_insert',
        dag             = dag,
        vertica_conn_id = vertica_conn_id,
        sql             = '/sql_scripts/dds_l_operation_currency_insert.sql')

    s_currency_details_insert = VerticaOperator(
        task_id         = 's_currency_details_insert',
        dag             = dag,
        vertica_conn_id = vertica_conn_id,
        sql             = '/sql_scripts/dds_s_currency_details_insert.sql')
        
    s_operation_amounts_insert = VerticaOperator(
        task_id         = 's_operation_amounts_insert',
        dag             = dag,
        vertica_conn_id = vertica_conn_id,
        sql             = '/sql_scripts/dds_s_operation_amounts_insert.sql')

    s_operation_details_insert = VerticaOperator(
        task_id         = 's_operation_details_insert',
        dag             = dag,
        vertica_conn_id = vertica_conn_id,
        sql             = '/sql_scripts/dds_s_operation_details_insert.sql')

    chain([h_currencies_insert, h_operations_insert],
            l_operation_currency_insert,
                [s_currency_details_insert,
                 s_operation_amounts_insert,
                 s_operation_details_insert])
