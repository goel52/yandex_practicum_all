from pathlib import Path

import pytest

from sprint_7_check_service.lessons.pyspark_for_data_engineer.create_data_frame.read_json import ReadJson
from sprint_7_check_service.lessons.pyspark_for_data_engineer.join_union.union_by_name import UnionByName
from sprint_7_check_service.lessons.pyspark_for_data_engineer.built_in_standard_functions.hour_min_sec import HourMinSec
from sprint_7_check_service.lessons.pyspark_for_data_engineer.window_functions.events_print_schema import EventsPrintSchema

AUTHORS = Path(__file__).resolve().parents[1] / 'author_solutions'
CASES = [
    (ReadJson, 'de07040402_read_json.txt', 'subscription', 'message'),
    (UnionByName, 'de07040604_union_by_name.txt', '322', '999'),
    (HourMinSec, 'de07040801_hour_min_sec.txt', '|  23|', '|  12|'),
    (EventsPrintSchema, 'de07040902_events_print_schema.txt', 'channel_id: long', 'channel_id: string'),
]


@pytest.mark.parametrize('checker,filename,old,new', CASES)
def test_student_path_false_accept_is_rejected(checker, filename, old, new):
    solution = (AUTHORS / filename).read_text().replace(old, new)
    ok, message = checker().check(solution)
    assert not ok
    assert message


@pytest.mark.parametrize('checker,filename,old,new', CASES)
def test_author_output_with_whitespace_is_accepted(checker, filename, old, new):
    solution = (AUTHORS / filename).read_text()
    solution = '\r\n'.join('  ' + line + '   ' for line in solution.splitlines())
    assert checker().check(solution)[0]


@pytest.mark.parametrize('checker,filename,old,new', CASES)
@pytest.mark.parametrize('solution', ['', 'pass', 'event event_type title author book_id hour minute second root struct channel_id long'])
def test_empty_or_keyword_only_output_is_rejected(checker, filename, old, new, solution):
    assert not checker().check(solution)[0]


def rewrite_table(solution, *, reverse_rows=False, reverse_columns=False):
    lines = [line for line in solution.splitlines() if line.strip().startswith('|')]
    header, *rows = lines
    if reverse_rows:
        rows.reverse()
    if reverse_columns:
        def reverse(line):
            return '|' + '|'.join(reversed(line.strip()[1:-1].split('|'))) + '|'
        header = reverse(header)
        rows = [reverse(row) for row in rows]
    return '\n'.join([header, *rows])


@pytest.mark.parametrize('checker,filename,old,new', CASES[:3])
def test_column_order_and_padding_do_not_change_result(checker, filename, old, new):
    solution = rewrite_table((AUTHORS / filename).read_text(), reverse_columns=True)
    assert checker().check(solution)[0]


@pytest.mark.parametrize('checker,filename,old,new', CASES[:2])
def test_unordered_output_accepts_reversed_rows(checker, filename, old, new):
    solution = rewrite_table((AUTHORS / filename).read_text(), reverse_rows=True)
    assert checker().check(solution)[0]


def test_time_output_must_be_sorted_by_descending_datetime():
    solution = rewrite_table((AUTHORS / 'de07040801_hour_min_sec.txt').read_text(), reverse_rows=True)
    assert not HourMinSec().check(solution)[0]


@pytest.mark.parametrize('old,new', [('57', '56'), ('38', '39'), ('|  23|', '|oops|')])
def test_time_values_are_checked_in_each_row(old, new):
    solution = (AUTHORS / 'de07040801_hour_min_sec.txt').read_text().replace(old, new, 1)
    assert not HourMinSec().check(solution)[0]


@pytest.mark.parametrize('checker,filename,old,new', CASES[:3])
@pytest.mark.parametrize('mutation', ['missing_row', 'extra_row', 'missing_cell', 'duplicate_column'])
def test_invalid_table_structure_is_rejected(checker, filename, old, new, mutation):
    lines = rewrite_table((AUTHORS / filename).read_text()).splitlines()
    if mutation == 'missing_row':
        lines.pop()
    elif mutation == 'extra_row':
        lines.append(lines[-1])
    elif mutation == 'missing_cell':
        cells = lines[-1].split('|')
        cells.pop(1)
        lines[-1] = '|'.join(cells)
    else:
        cells = lines[0].split('|')
        cells[2] = cells[1]
        lines[0] = '|'.join(cells)
    assert not checker().check('\n'.join(lines))[0]


def test_union_cannot_replace_missing_book_with_duplicate():
    lines = rewrite_table((AUTHORS / 'de07040604_union_by_name.txt').read_text()).splitlines()
    lines[-1] = lines[-2]
    assert not UnionByName().check('\n'.join(lines))[0]


def test_union_validates_author_association():
    solution = (AUTHORS / 'de07040604_union_by_name.txt').read_text().replace('J. K. Rowling', 'George Orwell')
    assert not UnionByName().check(solution)[0]


def test_union_accepts_untruncated_title():
    solution = (AUTHORS / 'de07040604_union_by_name.txt').read_text().replace(
        'Harry Potter and ...', 'Harry Potter and the Goblet of Fire')
    assert UnionByName().check(solution)[0]


def test_json_wrong_date_is_rejected():
    solution = (AUTHORS / 'de07040402_read_json.txt').read_text().replace('2022-05-25', '2022-05-26')
    assert not ReadJson().check(solution)[0]


@pytest.mark.parametrize('mutation', ['missing', 'duplicate', 'wrong_parent', 'array_element_type', 'nullable'])
def test_schema_checks_types_and_tree_structure(mutation):
    solution = (AUTHORS / 'de07040902_events_print_schema.txt').read_text()
    field = ' |    |-- channel_id: long (nullable = true)'
    if mutation == 'missing':
        solution = solution.replace(field, '')
    elif mutation == 'duplicate':
        solution = solution.replace(field, field + '\n' + field)
    elif mutation == 'wrong_parent':
        solution = solution.replace(field, ' |-- channel_id: long (nullable = true)')
    elif mutation == 'array_element_type':
        solution = solution.replace('element: long', 'element: string')
    else:
        solution = solution.replace('channel_id: long (nullable = true)', 'channel_id: long (nullable = false)')
    assert not EventsPrintSchema().check(solution)[0]


def test_schema_accepts_reordered_sibling_fields():
    solution = (AUTHORS / 'de07040902_events_print_schema.txt').read_text()
    solution = solution.replace(
        ' |    |-- channel_id: long (nullable = true)\n |    |-- datetime: string (nullable = true)',
        ' |    |-- datetime: string (nullable = true)\n |    |-- channel_id: long (nullable = true)')
    assert EventsPrintSchema().check(solution)[0]


@pytest.mark.parametrize('checker,filename,old,new', CASES)
def test_api_rejects_false_accept_without_platform_code(checker, filename, old, new):
    from fastapi.testclient import TestClient
    from sprint_7_check_service.run import app

    path = '/api/v1/checks/' + filename.removesuffix('.txt') + '/'
    with TestClient(app) as client:
        response = client.post(path, json={
            'student_id': 'regression_student',
            'student_solution': (AUTHORS / filename).read_text().replace(old, new),
        })
    assert response.status_code == 200
    assert response.json()['status'] == 'error'
    assert checker.RESPONSE_KEY not in response.json()['message']
