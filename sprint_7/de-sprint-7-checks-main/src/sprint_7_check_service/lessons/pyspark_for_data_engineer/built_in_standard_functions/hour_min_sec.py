from ..text_output import check_table, expected_output


class HourMinSec:
    RESPONSE_KEY = '5T3T8hAzm0'

    def check(self, student_solution: str, student_file_name: str = 'realization.txt'):
        # event is truncated by show(); compare the visible derived values and
        # event types, in the datetime-descending order required by the lesson.
        return check_table(
            student_solution, expected_output('de07040801_hour_min_sec.txt'),
            ordered=True, compare_columns=('event_type', 'hour', 'minute', 'second'))
