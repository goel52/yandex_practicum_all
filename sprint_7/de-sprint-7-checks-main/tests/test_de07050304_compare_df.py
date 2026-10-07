import pytest

from tests.test_config import TestConfig


class Test_De07050304_CompareDf:
    def test_author(self):
        author_file = 'de07050304_compare_df.py'

        author_code = TestConfig.read_author_solution(author_file)

        response = TestConfig.client.post(
            f'{TestConfig.API_PATH}/de07050304_compare_df',
            json={
                "student_id": 'student_id',
                "student_solution": author_code
            }
        )

        assert response.status_code == 200
        assert response.json() == {
            'message': 'Задание выполнено. Ваш код: apaYcksAK1',
            'status': 'success'
            }


# Separate failure modes from the lesson: columns, values, row order and duplicates.


@pytest.mark.parametrize('body', [
    'return True',
    'return False',
    'return None',
    'return set(left.columns) == set(right.columns)',
    'return left.count() == right.count()',
    'return left.collect() == right.collect()',
    "return (set(left.columns) == set(right.columns)) & (left.count() == right.count() == left.unionByName(right).distinct().count())",
])
def test_incorrect_compare_functions(body):
    response = TestConfig.client.post(
        f'{TestConfig.API_PATH}/de07050304_compare_df/',
        json={'student_id': 'student_id',
              'student_solution': f'def compare_df(left, right):\n    {body}\n'},
        follow_redirects=False,
    )
    assert response.status_code == 200
    assert response.json()['status'] == 'error'
