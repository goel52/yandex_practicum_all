"""Parse Spark text output without executing student code or starting a JVM."""
from functools import lru_cache
from pathlib import Path
import re


@lru_cache(maxsize=None)
def expected_output(filename):
    return (Path(__file__).with_name('expected_outputs') / filename).read_text()


def parse_table(text):
    rows = []
    for line in text.splitlines():
        line = line.strip()
        if not line or re.fullmatch(r'\+(?:-+\+)+', line):
            continue
        if re.fullmatch(r'only showing top \d+ rows', line):
            continue
        if not (line.startswith('|') and line.endswith('|')):
            raise ValueError('Сохраните табличный вывод show() без кода и пояснений.')
        rows.append([cell.strip() for cell in line[1:-1].split('|')])
    if len(rows) < 2:
        raise ValueError('Ожидается таблица с заголовком и строками данных.')
    columns, *values = rows
    if len(set(columns)) != len(columns) or any(not name for name in columns):
        raise ValueError('В заголовке таблицы повторяются или отсутствуют имена колонок.')
    if any(len(row) != len(columns) for row in values):
        raise ValueError('Количество значений в строке не совпадает с заголовком.')
    return columns, [dict(zip(columns, row)) for row in values]


def cell_matches(actual, expected):
    # show() truncates long strings; also accept their untruncated form.
    return actual == expected or (
        expected.endswith('...') and not actual.endswith('...')
        and actual.startswith(expected[:-3]))


def check_table(text, reference, *, ordered=False, compare_columns=None):
    try:
        columns, rows = parse_table(text)
    except ValueError as error:
        return False, str(error)
    expected_columns, expected_rows = parse_table(reference)
    if set(columns) != set(expected_columns):
        return False, 'Ожидаются колонки: ' + ', '.join(expected_columns)
    if len(rows) != len(expected_rows):
        return False, f'Ожидается {len(expected_rows)} строк, получено {len(rows)}.'
    fields = compare_columns or expected_columns

    def matches(row, expected):
        return all(cell_matches(row[field], expected[field]) for field in fields)

    if ordered:
        if any(not matches(row, expected) for row, expected in zip(rows, expected_rows)):
            return False, ('Проверьте значения колонок ' + ', '.join(fields)
                           + ' и сортировку строк по условию задания.')
    else:
        remaining = list(expected_rows)
        for row in rows:
            index = next((i for i, expected in enumerate(remaining)
                          if matches(row, expected)), None)
            if index is None:
                return False, ('В таблице неверные значения или повторяющиеся строки. '
                               'Проверьте соответствие значений колонок в каждой строке.')
            remaining.pop(index)
    return True, None


def parse_schema(text):
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if not lines or lines[0] != 'root':
        raise ValueError('Сохраните полный вывод printSchema(), начиная с root.')
    fields = {}
    parents = []
    for line in lines[1:]:
        match = re.fullmatch(
            r'(?P<prefix>(?:\|\s*)*)\|--\s*(?P<name>\w+):\s*'
            r'(?P<type>\w+)\s*\(\s*(?P<flag>nullable|containsNull)'
            r'\s*=\s*(?P<null>true|false)\s*\)', line)
        if not match:
            raise ValueError('Некорректная строка схемы: ' + line)
        depth = match['prefix'].count('|')
        if depth > len(parents):
            raise ValueError('Нарушена вложенность полей схемы.')
        parents = parents[:depth]
        path = tuple(parents + [match['name']])
        if path in fields:
            raise ValueError('Повторяется поле схемы: ' + '.'.join(path))
        fields[path] = (match['type'], match['flag'], match['null'])
        parents.append(match['name'])
    return fields
