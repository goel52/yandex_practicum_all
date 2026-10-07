from typing import Optional, Tuple


class JoinTitle:
    RESPONSE_KEY = 'uYBBsdnoBi'

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
            'Nineteen Eighty-Four',
            'Harry Potter and the Goblet of Fire',
            'Jane Eyre'
        }

        for row in rows:
            if row not in student_solution:
                return False, f'Не найдена строка `{row}`'

        return True, None
