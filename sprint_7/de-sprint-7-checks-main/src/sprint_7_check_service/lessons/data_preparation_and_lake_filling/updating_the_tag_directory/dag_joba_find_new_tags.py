import ast
from typing import Optional, Tuple

from sprint_7_check_service.ast_tools.ast_visitors_custom import NodeQuery


class DagJobBashOperator:
    RESPONSE_KEY = 'tWPYxsMDWU'

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

        if not next((_ for _ in assigns if 'verified_tags_candidates.py' in _), None):  # noqa
            return (False,
                    "Не найдено объявление SparkSubmitOperator c указанием application='.../verified_tags_candidates.py'")  # noqa

        # TODO: add checks

        return True, None
