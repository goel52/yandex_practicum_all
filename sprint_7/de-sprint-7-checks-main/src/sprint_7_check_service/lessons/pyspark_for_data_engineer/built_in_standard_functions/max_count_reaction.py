from typing import Optional, Tuple


class MaxCountReaction:
    RESPONSE_KEY = 'lXFKRx00xQ'

    def __init__(self) -> None:
        pass

    def check(
            self,
            student_solution: str,
            student_file_name: str = 'realization.txt'
            ) -> Tuple[bool, Optional[str]]:

        if '11' not in student_solution:
            return False, 'Ожидается число `11`, проверьте свое решение.'

        return True, None
