import airflow
from datetime import timedelta
from airflow import DAG
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
import os
from datetime import date, datetime

os.environ['HADOOP_CONF_DIR'] = '/etc/hadoop/conf'
os.environ['YARN_CONF_DIR'] = '/etc/hadoop/conf'
os.environ['JAVA_HOME'] = '/usr'
os.environ['SPARK_HOME'] ='/usr/lib/spark'
os.environ['PYTHONPATH'] ='/usr/local/lib/python3.8'

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2020, 1, 1)
}

dag_spark = DAG(
    dag_id = "datalake_hdfs_etl",
    default_args = default_args,
    schedule_interval = None,
)

users_cities = SparkSubmitOperator(
    task_id = 'users_cities',
    dag = dag_spark,
    application ='../scripts/users_cities.py' ,
    conn_id = 'yarn_spark',
    conf = {
        "spark.driver.maxResultSize": "20g"
    },
    executor_cores = 1,
    executor_memory = '1g'
)

events_cities = SparkSubmitOperator(
    task_id = 'events_cities',
    dag = dag_spark,
    application ='../scripts/events_cities.py' ,
    conn_id = 'yarn_spark',
    #conn_id = 'local',
    #application_args = [],
    conf = {
        "spark.driver.maxResultSize": "20g"
    },
    #executor_cores = 1,
    executor_memory = '1g'
)

recommended_friends = SparkSubmitOperator(
    task_id = 'recommended_friends',
    dag = dag_spark,
    application = '../scripts/recommended_friends.py' ,
    #conn_id = 'local',
    conn_id = 'yarn_spark',
    conf={
        "spark.driver.maxResultSize": "20g"
    },
    #Sexecutor_cores = 1,
    executor_memory = '1g'
)

[users_cities, events_cities, recommended_friends]