from ..text_output import parse_table


class ReadJson:
    RESPONSE_KEY = 'tSp92pppl6'

    def check(self, student_solution: str, student_file_name: str = 'realization.txt'):
        try:
            columns, rows = parse_table(student_solution)
        except ValueError as error:
            return False, str(error)
        if set(columns) != {'event', 'event_type'}:
            return False, 'Ожидаются колонки event и event_type.'
        if len(rows) != 10:
            return False, 'Выведите ровно 10 строк: events.show(10).'
        # The supplied exercise sample starts with subscription events.
        # Do not freeze their order or the truncated timestamp suffixes.
        for row in rows:
            if row['event_type'] != 'subscription':
                return False, 'В первых 10 строках учебного набора ожидается event_type subscription.'
            if '2022-05-25' not in row['event']:
                return False, 'Прочитайте события за 2022-05-25 и сохраните колонку event.'
        return True, None
