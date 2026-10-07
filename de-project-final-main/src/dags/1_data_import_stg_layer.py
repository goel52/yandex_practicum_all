from datetime import datetime

from airflow import DAG
from airflow.hooks.base_hook import BaseHook
from airflow.models.baseoperator import chain
from airflow.operators.python import PythonOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from airflow.providers.vertica.operators.vertica import VerticaOperator
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator

from utils import s3_to_vertica

spark_packages = ','.join([
    'org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0,'
    'com.vertica.jdbc:vertica-jdbc:11.0.0-0'])

kafka_connection = BaseHook.get_connection('kafka_connection')
kafka_user = kafka_connection.login
kafka_pass = kafka_connection.password
kafka_topic = 'transaction-service-input'

vertica_connection = BaseHook.get_connection('vertica_connection')
vertica_conn_id = vertica_connection.conn_id
vertica_user = vertica_connection.login
vertica_pass = vertica_connection.password

cosumed_tmp_table = 'MIKEPAFYANDEXRU__STAGING.transactions_input_tmp_kafka'

s3_connection = BaseHook.get_connection('s3_connection')

default_args = {
    'owner'     : 'mike.panfilov',
    'start_date': datetime(2022, 10, 1)
}

with DAG(dag_id = "data_import_stg_layer",
                default_args=default_args,
                schedule_interval='@daily',
                catchup=False) as dag:

    
    truncate_tmp_table = VerticaOperator(
        task_id         = 'truncate_tmp_table',
        dag             = dag,
        vertica_conn_id = vertica_conn_id,
        sql             = '/sql_scripts/stg_truncate_tmp_tables.sql')
    truncate_tmp_table.doc_md = ('Cleaning temporary tables before uploading data: '
                                 'tables will persist given data from kafka and s3 untill the next run')

    consume_transactions = SparkSubmitOperator(
        task_id          = 'consume_transactions',
        dag              = dag,
        application      = '/root/dags/spark_scripts/consume_transactions.py',
        packages         = spark_packages,
        conn_id          = 'spark_local',
        application_args = [kafka_user, kafka_pass, kafka_topic,
                            vertica_user,
                            vertica_pass,
                            cosumed_tmp_table])

    get_data_from_s3    = PythonOperator(
        task_id = 'get_data_from_s3',
        dag=dag,
        python_callable=s3_to_vertica,
        op_args = [s3_connection, vertica_connection]
    )

    merge_transactions_kafka = VerticaOperator(
        task_id         = 'merge_transactions_kafka',
        dag             = dag,
        vertica_conn_id = vertica_conn_id,
        sql             = '/sql_scripts/stg_merge_transactions_kafka.sql')

    merge_currencies_kafka = VerticaOperator(
        task_id         = 'merge_currencies_kafka',
        dag             = dag,
        vertica_conn_id = vertica_conn_id,
        sql             = '/sql_scripts/stg_merge_currencies_kafka.sql')

    merge_transactions = VerticaOperator(
        task_id         = 'merge_transactions',
        dag             = dag,
        vertica_conn_id = vertica_conn_id,
        sql             = '/sql_scripts/stg_merge_transactions.sql')

    merge_currencies = VerticaOperator(
        task_id         = 'merge_currencies',
        dag             = dag,
        vertica_conn_id = vertica_conn_id,
        sql             = '/sql_scripts/stg_merge_currencies.sql')

    trigger_dds_pipeline = TriggerDagRunOperator(
        task_id             = 'trigger_dds_pipeline',
        dag                 = dag,
        trigger_dag_id      = 'data_import_dds_layer',
        wait_for_completion = False,
        retries             = 0)

    chain(truncate_tmp_table,
            consume_transactions,
                get_data_from_s3,
                    [merge_transactions_kafka, merge_currencies_kafka],
                        [merge_transactions, merge_currencies],
                            trigger_dds_pipeline)