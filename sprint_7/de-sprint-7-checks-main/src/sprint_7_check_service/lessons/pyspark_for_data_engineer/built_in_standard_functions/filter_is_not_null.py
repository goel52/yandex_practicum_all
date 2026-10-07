from typing import Optional, Tuple


class FilterIsNotNull:
    RESPONSE_KEY = 'XUdp1wiOxP'

    def __init__(self) -> None:
        pass

    def check(
            self,
            student_solution: str,
            student_file_name: str = 'realization.txt'
            ) -> Tuple[bool, Optional[str]]:

        if '221' not in student_solution:
            return False, 'Ожидается число `221`, проверьте свое решение.'

        return True, None
