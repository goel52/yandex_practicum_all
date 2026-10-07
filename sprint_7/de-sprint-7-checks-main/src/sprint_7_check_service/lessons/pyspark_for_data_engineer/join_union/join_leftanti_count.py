from typing import Optional, Tuple


class JoinLeftantiCount:
    RESPONSE_KEY = 'Yxw1oyi5nm'

    def __init__(self) -> None:
        pass

    def check(
            self,
            student_solution: str,
            student_file_name: str = 'realization.txt'
            ) -> Tuple[bool, Optional[str]]:

        if '5' not in student_solution:
            return False, 'Должен получиться результат = 5 книг, проверьте своё решение.'  # noqa

        return True, None
