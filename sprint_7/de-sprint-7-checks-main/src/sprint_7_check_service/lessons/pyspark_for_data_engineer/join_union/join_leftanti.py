from typing import Optional, Tuple


class JoinLeftanti:
    RESPONSE_KEY = 'J2XPUFWhkj'

    def __init__(self) -> None:
        pass

    def check(
            self,
            student_solution: str,
            student_file_name: str = 'realization.txt'
            ) -> Tuple[bool, Optional[str]]:

        if 'title' not in student_solution:
            return False, 'Не найдена колонка `title`'

        rows = {
            'Catch-22',
            'Bad Girls',
            'The Catcher in the Rye',
            'The Mayor of Casterbridge',
            'The Wind in the Willows'
        }

        for row in rows:
            if row not in student_solution:
                return False, f'Не найдена строка `{row}`'

        return True, None
