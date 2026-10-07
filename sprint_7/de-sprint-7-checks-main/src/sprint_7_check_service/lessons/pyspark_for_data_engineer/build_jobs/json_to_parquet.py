from typing import Optional, Tuple


class JsonToParquet:
    RESPONSE_KEY = 'MisYAUZkzJ'

    def __init__(self) -> None:
        pass

    def check(
            self,
            student_solution: str,
            student_file_name: str = 'realization.txt'
            ) -> Tuple[bool, Optional[str]]:

        keys = {
            'event',
            'date',
            'event_type',
            '2022-05-31',
            'message',
            'subscription',
        }

        for key in keys:
            if key not in student_solution:
                return False, f'Не найдено значение `{key}`, проверьте решение'

        return True, None
