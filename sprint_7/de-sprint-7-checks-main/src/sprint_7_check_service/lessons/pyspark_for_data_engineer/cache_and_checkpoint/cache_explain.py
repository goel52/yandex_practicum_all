from typing import Optional, Tuple


class CacheExplain:
    RESPONSE_KEY = '1sJEyNLn4O'

    def __init__(self) -> None:
        pass

    def check(
            self,
            student_solution: str,
            student_file_name: str = 'realization.txt'
            ) -> Tuple[bool, Optional[str]]:

        keys = {
            'InMemoryTableScan',
            'InMemoryRelation',
            'Project',
            'SortMergeJoin',
            'Sort',
            'Exchange hashpartitioning',
            'Filter isnotnull'
        }

        for key in keys:
            if key not in student_solution:
                return False, f'Не найден параметр `{key}`.'

        return True, None
