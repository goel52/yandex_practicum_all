import ast
from typing import Optional, Tuple

from sprint_7_check_service.ast_tools.ast_visitors_custom import NodeQuery


class CreateSparkSession:
    RESPONSE_KEY = 'VB433DtP5e'

    def __init__(self) -> None:
        pass

    def check(self,
              student_solution: str,
              student_file_name: str = 'realization.py',
              ) -> Tuple[bool, Optional[str]]:

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

        import_spark_session = tree.node(ast.ImportFrom, module='pyspark.sql')

        import_spark_session_ss = tree.node(
            ast.ImportFrom,
            names__0__name='SparkSession')

        if not import_spark_session.exists:
            return (False,
                    'Не найдено объявление импорта'
                    ' `from pyspark.sql import SparkSession`')

        if not import_spark_session_ss.exists:
            return (False,
                    'Не найдено объявление импорта '
                    '`from pyspark.sql import SparkSession`')

        assign_spark = tree.node(ast.Assign, targets__0__id='spark')

        if not assign_spark.exists:
            return (False, 'Не найдено объявление переменной `spark`')

        attr_spark_session = assign_spark.node(ast.Name, id='SparkSession')

        if not attr_spark_session.exists:
            return (False, 'Не найдено обращение к объекту `SparkSession`')

        attr_builder = assign_spark.node(ast.Attribute, attr='builder')

        if not attr_builder.exists:
            return (False, 'Не найдено обращение к объекту `builder`')

        if not assign_spark.node(value='spark.driver.cores').all:
            return False, f'Не найдено указание config("spark.driver.cores", "2")'  # noqa

        if not assign_spark.node(value='2').all:
            return False, f'Не найдено указание config("spark.driver.cores", "2")'  # noqa

        if not assign_spark.node(value='spark.driver.memory').all:
            return False, f'Не найдено указание config("spark.driver.memory", "1g")'  # noqa

        if not assign_spark.node(value='1g').all:
            return False, f'Не найдено указание config("spark.driver.memory", "1g")'  # noqa

        if not assign_spark.node(value='My first session').all:
            return False, 'Не найдено указание appName("My first session")'

        if 'getOrCreate' not in assign_spark.node('attr').all:
            return False, f'Не найден метод инициализации объекта сессии — `getOrCreate`'  # noqa

        return True, None
