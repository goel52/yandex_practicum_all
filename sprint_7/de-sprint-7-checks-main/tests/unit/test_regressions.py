from pathlib import Path

import pytest

from sprint_7_check_service.lessons.pyspark_for_data_engineer.window_functions.window_orderby_pa import WindowOrderByPA
from sprint_7_check_service.lessons.data_preparation_and_lake_filling.user_portrait.pyspark_job import PySparkJob
from sprint_7_check_service.lessons.data_preparation_and_lake_filling.user_portrait.airflow_dag import AirflowDag
from sprint_7_check_service.lessons.data_preparation_and_lake_filling.updating_the_tag_directory.joba_find_new_tags import JobaFindNewTags

AUTHORS = Path(__file__).resolve().parents[1] / 'author_solutions'


def ranked_rows():
    return (AUTHORS / 'de07040901_window_orderby_pa.txt').read_text()


def test_row_number_allows_equal_amounts_in_another_order():
    solution = ranked_rows().replace(
        '|2021-01-04|   2434|            159|         1|',
        '|2021-01-06|   4342|            159|         1|').replace(
        '|2021-01-06|   4342|            159|         3|',
        '|2021-01-04|   2434|            159|         3|')
    assert WindowOrderByPA().check(solution)[0]


@pytest.mark.parametrize('mutation', ['extra', 'missing', 'same_rank', 'wrong_amount', 'empty'])
def test_row_number_rejects_invalid_results(mutation):
    solution = ranked_rows()
    last = '|2021-01-04|   5677|            499|         8|'
    solution = {
        'extra': solution.replace(last, last + '\n' + last),
        'missing': solution.replace(last, ''),
        'same_rank': solution.replace('         8|', '         7|'),
        'wrong_amount': solution.replace('499', '498'),
        'empty': '',
    }[mutation]
    assert not WindowOrderByPA().check(solution)[0]


@pytest.mark.parametrize('checker,filename', [
    (PySparkJob, 'de07050305_pyspark_job.py'),
    (JobaFindNewTags, 'de07050204_joba_find_new_tags.py'),
])
def test_numeric_command_line_arguments(checker, filename):
    solution = (AUTHORS / filename).read_text().replace(
        'days_count = sys.argv[2]', 'days_count = int(sys.argv[2])').replace(
        'suggested_cutoff = sys.argv[3]', 'suggested_cutoff = int(sys.argv[3])')
    assert checker().check(solution, None)[0]
    wrong = solution.replace('days_count = int(sys.argv[2])', 'days_count = 84')
    assert not checker().check(wrong, None)[0]


def test_dag_without_dependency_expression_returns_error():
    assert not AirflowDag().check("application = '/home/username/user_interests.py'")[0]
