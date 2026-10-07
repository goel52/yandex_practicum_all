from datetime import datetime
from airflow import DAG
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from airflow.operators.dummy import DummyOperator

default_args = {
    'owner': 'edu-sinergium',
    'start_date': datetime(2023, 1, 19)
}

dag = DAG(
    dag_id = "dm_for_social",
    default_args = default_args,
    schedule_interval = "@daily",
    catchup = False,
)

start = DummyOperator(
    task_id = 'start',
    dag = dag
)

datamart_1 = SparkSubmitOperator(
    task_id = 'dm_1',
    dag = dag,
    application = '/lessons/scripts/dm_1.py',
    conn_id = 'yarn_spark',
    application_args=["{{ds}}"]
)

datamart_2 = SparkSubmitOperator(
    task_id = 'dm_2',
    dag = dag,
    application = '/lessons/scripts/dm_2.py',
    conn_id = 'yarn_spark',
    application_args=["{{ds}}"]
)

datamart_3 = SparkSubmitOperator(
    task_id = 'dm_3',
    dag = dag,
    application = '/lessons/scripts/dm_3.py',
    conn_id = 'yarn_spark',
    application_args=["{{ds}}"]
)

finish = DummyOperator(
    task_id = 'finish',
    dag = dag
)


start >> [ datamart_1, datamart_2, datamart_3 ] >> finish