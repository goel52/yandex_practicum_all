import os
from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

os.environ['HADOOP_CONF_DIR'] = '/etc/hadoop/conf'
os.environ['YARN_CONF_DIR'] = '/etc/hadoop/conf'
os.environ['JAVA_HOME']='/usr'
os.environ['SPARK_HOME'] ='/usr/lib/spark'
os.environ['PYTHONPATH'] ='/usr/local/lib/python3.8'


# базовые аргументы
default_args = {
    'start_date':datetime(2020, 1, 1),
    'owner': 'airflow'
}

# вызываем даг
dag = DAG("dag_bash",
          schedule_interval=None,
          default_args=default_args
          )

# задача с bash-командой, которая распечатывает дату
t1 = BashOperator(
    task_id='print_date',
    bash_command="spark-submit --master yarn --deploy-mode cluster /home/amdubovoy/partition.py 2022-05-31 /user/master/data/events, /user/username/analitics/events",
    retries=3,
    dag=dag
)

t1
