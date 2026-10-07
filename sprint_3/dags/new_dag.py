from airflow.models import DAG
from airflow.sensors.filesystem import FileSensor
from airflow.utils.task_group import TaskGroup
from datetime import datetime
from airflow.operators.bash import BashOperator


default_args = {
    "start_date": datetime(2020, 1, 1),
    "owner": "airflow"
}


with DAG(
    dag_id="Sprin4_Task32",
    schedule_interval="@daily",
    default_args=default_args,
    catchup=False
    ) as dag:

    with TaskGroup(group_id='group1') as fg1:
        f1 = BashOperator(task_id="display", bash_command="echo {{ ds }}")
        f2 = BashOperator(task_id=f"display_{{ ds }}", bash_command="echo2 {{ ds }}")
    fg1    
