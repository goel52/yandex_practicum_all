from typing import Optional, Tuple


class WriteParquet:
    RESPONSE_KEY = '3TkchiZud0'

    def __init__(self) -> None:
        pass

    def check(
            self,
            student_solution: str,
            student_file_name: str = 'realization.txt'
            ) -> Tuple[bool, Optional[str]]:

        if 'channel_type' not in student_solution:
            return False, 'Не найдена колонка `channel_type`'

        if 'river' not in student_solution:
            return False, 'Не найдено значение `river`'

        if 'channel' not in student_solution:
            return False, 'Не найдено значение `channel`'

        return True, None
