from collections import Counter
from typing import Optional, Tuple


class WindowOrderByPA:
    RESPONSE_KEY = 'Zv6vxsDQLo'

    def check(self, student_solution: str,
              student_file_name: str = 'realization.txt'
              ) -> Tuple[bool, Optional[str]]:
        rows = [tuple(cell.strip() for cell in line.strip().strip('|').split('|'))
                for line in student_solution.splitlines()
                if line.strip().startswith('|')]
        header = ('dt', 'user_id', 'purchase_amount', 'row_number')
        expected = Counter([
            ('2021-01-06', '3744', '322'),
            ('2021-01-04', '2434', '382'),
            ('2021-01-04', '2434', '159'),
            ('2021-01-05', '3744', '159'),
            ('2021-01-06', '4342', '159'),
            ('2021-01-05', '4342', '259'),
            ('2021-01-06', '5677', '259'),
            ('2021-01-04', '5677', '499'),
        ])
        if not rows or rows[0] != header:
            return False, 'Ожидаются колонки dt, user_id, purchase_amount, row_number.'
        data = rows[1:]
        if any(len(row) != 4 for row in data) or Counter(row[:3] for row in data) != expected:
            return False, 'Ожидаются восемь строк исходного датафрейма без лишних или пропущенных строк.'
        # ORDER BY purchase_amount leaves the order within equal amounts unspecified.
        amounts = [int(row[2]) for row in data]
        if amounts != sorted(amounts) or [row[3] for row in data] != [str(i) for i in range(1, 9)]:
            return False, 'Суммы должны возрастать, а row_number принимать значения от 1 до 8 без повторов.'
        return True, None
