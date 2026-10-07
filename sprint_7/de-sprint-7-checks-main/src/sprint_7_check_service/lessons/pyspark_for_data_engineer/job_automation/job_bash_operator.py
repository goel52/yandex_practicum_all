import ast
from typing import Optional, Tuple

from sprint_7_check_service.ast_tools.ast_visitors_custom import NodeQuery


class JobBashOperator:
    RESPONSE_KEY = 'WPs40lac6U'

    def __init__(self) -> None:
        pass

    def check(
            self,
            student_solution: str,
            student_file_name: str = 'realization.py'
            ) -> Tuple[bool, Optional[str]]:

        def check_bash_operator_variant(
                tree: NodeQuery
                ) -> Tuple[bool, Optional[str]]:

            if 'import os' not in [ast.unparse(_)
                                   for _ in tree.node(ast.Import).all]:
                return (False, 'Не найден `import os`')

            imports_from = [ast.unparse(_)
                            for _ in tree.node(ast.ImportFrom).all]

            if 'from airflow import DAG' not in imports_from:
                return (False, 'Не найден `import DAG`')

            assigns = [ast.unparse(_) for _ in tree.node(ast.Assign).all]

            auth_assigns = (
                "os.environ['HADOOP_CONF_DIR'] = '/etc/hadoop/conf'",
                "os.environ['YARN_CONF_DIR'] = '/etc/hadoop/conf'",
                "os.environ['JAVA_HOME'] = '/usr'",
                "os.environ['SPARK_HOME'] = '/usr/lib/spark'",
                "os.environ['PYTHONPATH'] = '/usr/local/lib/python3.8'",
            )

            for auth_assign in auth_assigns:
                if auth_assign not in assigns:
                    return (False,
                            f"Не найдено `{auth_assign}`")

            if not next((_ for _ in assigns if 'DAG(' in _), None):
                return (False,
                        "Не найдено объявление дага :`dag = DAG('dag_bash', schedule_interval=None, default_args=default_args)`")  # noqa

            if not next((_ for _ in assigns if 'BashOperator' in _), None):
                return (False,
                        "Не найдено объявление BashOperator:`t1 = BashOperator(task_id='print_date', bash_command='spark-submit --master yarn --deploy-mode cluster /home/username/partition.py 2022-05-31 /user/master/data/events, /user/username/analitics/events', retries=3, dag=dag)`")  # noqa
            return True, None

        def check_spark_submit_operator_variant(
                tree: NodeQuery
                ) -> Tuple[bool, Optional[str]]:

            if 'import os' not in [ast.unparse(_)
                                   for _ in tree.node(ast.Import).all]:
                return (False, 'Не найден `import os`')

            imports_from = [ast.unparse(_)
                            for _ in tree.node(ast.ImportFrom).all]

            if 'from airflow import DAG' not in imports_from:
                return (False, 'Не найден `import DAG`')

            assigns = [ast.unparse(_) for _ in tree.node(ast.Assign).all]

            auth_assigns = (
                "os.environ['HADOOP_CONF_DIR'] = '/etc/hadoop/conf'",
                "os.environ['YARN_CONF_DIR'] = '/etc/hadoop/conf'",
                "os.environ['JAVA_HOME'] = '/usr'",
                "os.environ['SPARK_HOME'] = '/usr/lib/spark'",
                "os.environ['PYTHONPATH'] = '/usr/local/lib/python3.8'",
            )

            for auth_assign in auth_assigns:
                if auth_assign not in assigns:
                    return (False,
                            f"Не найдено `{auth_assign}`")

            if not next((_ for _ in assigns if 'DAG(' in _), None):
                return (False,
                        "Не найдено объявление дага:`dag_spark = DAG( dag_id='sparkoperator', default_args=default_args, schedule_interval=None,)`")  # noqa

            if not next((_ for _ in assigns if 'SparkSubmitOperator(' in _), None):  # noqa
                return (False,
                        "Не найдено объявление SparkSubmitOperator: `spark_submit = SparkSubmitOperator(task_id='spark_submit_task', dag=dag_spark, application='/home/username/partition.py', conn_id='yarn_spark', application_args=['2022-05-31', '/user/master/data/events', '/user/username/analitics/events'], conf={'spark.driver.maxResultSize': '20g'}, executor_cores=1, executor_memory='1g')`")  # noqa

            return True, None

        try:
            tree = NodeQuery(ast.parse(
                student_solution,
                student_file_name,
                mode='exec'))

        except Exception as e:
            return (False,
                    'Ваш код нельзя исполнить,'
                    f' ошибка: {type(e)}.\n'
                    f'{str(e)}')

        if 'BashOperator' in student_solution:
            return check_bash_operator_variant(tree)
        else:
            return check_spark_submit_operator_variant(tree)
