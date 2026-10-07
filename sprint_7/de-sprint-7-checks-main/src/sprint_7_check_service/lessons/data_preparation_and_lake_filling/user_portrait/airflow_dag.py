import ast
from typing import Optional, Tuple

from sprint_7_check_service.ast_tools.ast_visitors_custom import NodeQuery


class AirflowDag:
    RESPONSE_KEY = 'vVTKqhdLqt'

    def __init__(self) -> None:
        pass

    def check(
            self,
            student_solution: str,
            student_file_name: str = 'realization.py'
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

        assigns = [ast.unparse(_) for _ in tree.node(ast.Assign).all]

        if not next((_ for _ in assigns if 'user_interests.py' in _), None):
            return (False,
                    "Не найдено объявление SparkSubmitOperator"
                    " c указанием application='.../user_interests.py'")

        expressions = tree.node(ast.Expr).all
        if not expressions:
            return False, 'Добавьте зависимости задач в DAG.'
        expr = ast.unparse(expressions[-1])

        if any(['events_partitioned' not in expr,
                'verified_tags_candidates_d7' not in expr,
                'verified_tags_candidates_d84' not in expr,
                'user_interests_d7' not in expr,
                'user_interests_d28' not in expr
                ]):
            return (False,
                    'Дополните выражение events_partitioned >> [...] используя'
                    ' имена функций из прекода.')

        return True, None
