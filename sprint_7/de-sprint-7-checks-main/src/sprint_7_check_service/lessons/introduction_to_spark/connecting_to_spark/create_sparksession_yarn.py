import ast
from typing import Optional, Tuple

from sprint_7_check_service.ast_tools.ast_visitors_custom import NodeQuery


class CreateSparkSessionYarn:
    RESPONSE_KEY = 'kMCwkWEe1W'

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

        if not assign_spark.node(ast.Attribute, attr='master').exists:
            return (False, 'Не найдено обращение к объекту `master`')

        if not assign_spark.node(ast.Constant, value='yarn').exists:
            return (False, 'В настройке запуска `master` укажите режим `yarn`')

        if not assign_spark.node(value='My second session').all:
            return False, f'Не найдено указание appName("My second session")'

        if 'getOrCreate' not in assign_spark.node('attr').all:
            return False, f'Не найден метод инициализации объекта сессии — `getOrCreate`'


        return True, None
