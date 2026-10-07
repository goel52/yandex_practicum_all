from typing import Optional, Tuple


class CacheCheckPoint:
    RESPONSE_KEY = 'einWLzgTYR'

    def __init__(self) -> None:
        pass

    def check(
            self,
            student_solution: str,
            student_file_name: str = 'realization.txt'
            ) -> Tuple[bool, Optional[str]]:

        keys = {
            'Physical Plan',
            'ExistingRDD'
        }

        for key in keys:
            if key not in student_solution:
                return False, f'Не найден параметр `{key}`.'

        return True, None
