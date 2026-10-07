from ..text_output import expected_output, parse_schema


class EventsPrintSchema:
    RESPONSE_KEY = 'ESLk6ckjLB'

    def check(self, student_solution: str, student_file_name: str = 'realization.txt'):
        try:
            actual = parse_schema(student_solution)
        except ValueError as error:
            return False, str(error)
        expected = parse_schema(expected_output('de07040902_events_print_schema.txt'))
        for path, definition in expected.items():
            name = '.'.join(path)
            if path not in actual:
                return False, f'Не найдено поле {name}. Проверьте вложенность схемы.'
            if actual[path] != definition:
                field_type, flag, nullable = definition
                return False, f'Поле {name}: ожидается {field_type} ({flag} = {nullable}).'
        if actual.keys() != expected.keys():
            return False, 'В схеме есть лишние поля. Прочитайте исходную таблицу events.'
        return True, None
