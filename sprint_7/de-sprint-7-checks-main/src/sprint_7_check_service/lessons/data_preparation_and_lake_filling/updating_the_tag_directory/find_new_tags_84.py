import ast
from typing import Optional, Tuple

from pyspark.sql import SparkSession
from sprint_7_check_service.ast_tools.ast_visitors_custom import NodeQuery


class FindNewTags84:
    RESPONSE_KEY = '8IrkD1toNn'

    def __init__(self) -> None:
        pass

    def check(self,
              student_solution: str,
              spark: SparkSession,
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

        if not tree.node(ast.Expr).exists:
            return False, 'Не найден вызов метода `write.parquet`'

        write_parquet = ast.unparse(tree.node(ast.Expr).all[0])

        if 'write.parquet' not in write_parquet:
            return False, 'Не найден вызов метода `write.parquet`'

        if 'candidates_d84_pyspark' not in write_parquet:
            return False, ('В вызове метода `write.parquet` укажите путь для '
                           'сохранения результата согласно условия задачи: '
                           '`.../candidates_d84_pyspark`')

        return True, None
