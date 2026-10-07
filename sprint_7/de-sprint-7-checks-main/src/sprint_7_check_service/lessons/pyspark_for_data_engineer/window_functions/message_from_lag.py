from typing import Optional, Tuple


class MessageFromLag:
    RESPONSE_KEY = 'tl0Bn1k6Aw'

    def __init__(self) -> None:
        pass

    def check(
            self,
            student_solution: str,
            student_file_name: str = 'realization.txt'
            ) -> Tuple[bool, Optional[str]]:

        columns = {
            'message_from',
            'lag_7',
        }

        for column in columns:
            if column not in student_solution:
                return False, f'Не найдена колонка `{column}`'

        rows = {
            '121581',
            '25843',
            '70776',
        }

        for row in rows:
            if row not in student_solution:
                return (False,
                        f'Не найдено значение `{row}`, проверьте решение.')

        return True, None
