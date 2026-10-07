from typing import Optional, Tuple


class SparkSubmitPartition:
    RESPONSE_KEY = 'T7XQ44EsDR'

    def __init__(self) -> None:
        pass

    def check(
            self,
            student_solution: str,
            student_file_name: str = 'realization.txt'
            ) -> Tuple[bool, Optional[str]]:

        keys = {
            'spark-submit',
            '--master yarn',
            '--deploy-mode cluster',
            'partition.py',
            '2022-05-31',
        }

        for key in keys:
            if key not in student_solution:
                return False, f'Не найден параметр `{key}`, проверьте решение.'

        return True, None
