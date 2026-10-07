from typing import Optional, Tuple


class PurchaseAmountMaxMin:
    RESPONSE_KEY = 'B56jrrrxSz'

    def __init__(self) -> None:
        pass

    def check(
            self,
            student_solution: str,
            student_file_name: str = 'realization.txt'
            ) -> Tuple[bool, Optional[str]]:

        columns = {
            'user_id',
            'max',
            'min',
        }

        for column in columns:
            if column not in student_solution:
                return False, f'Не найдена колонка `{column}`'

        rows = {
            '2434|382|159',
            '4342|259|159',
            '5677|499|259',
            '3744|322|159',
        }

        for row in rows:
            if row not in student_solution:
                return (False,
                        f'Не найдено значение `{row}`, проверьте решение.')

        return True, None
