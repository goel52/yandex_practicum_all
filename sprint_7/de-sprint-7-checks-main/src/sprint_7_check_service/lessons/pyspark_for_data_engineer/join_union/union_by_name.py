from ..text_output import check_table, expected_output


class UnionByName:
    RESPONSE_KEY = 'rNIfTDPFfu'

    def check(self, student_solution: str, student_file_name: str = 'realization.txt'):
        return check_table(
            student_solution, expected_output('de07040604_union_by_name.txt'))
