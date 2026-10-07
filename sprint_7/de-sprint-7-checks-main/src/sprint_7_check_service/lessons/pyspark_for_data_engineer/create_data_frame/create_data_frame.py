from typing import Optional, Tuple


class CreateDataFrame:
    RESPONSE_KEY = 'zZoMQveyrG'

    def __init__(self) -> None:
        pass

    def check(
            self,
            student_solution: str,
            student_file_name: str = 'realization.txt'
            ) -> Tuple[bool, Optional[str]]:

        if 'Name: string (nullable = true)' not in student_solution:
            return False, 'Не найдена колонка `Name` с параметром nullable = true'

        if 'Age: long (nullable = true)' not in student_solution:
            return False, 'Не найдена колонка `Age` с параметром nullable = true'

        return True, None
