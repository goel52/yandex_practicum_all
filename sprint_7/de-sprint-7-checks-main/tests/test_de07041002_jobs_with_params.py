
from tests.test_config import TestConfig


class Test_De07041002_JobsWithParams:
    def test_author(self):
        author_file = 'de07041002_jobs_with_params.py'

        author_code = TestConfig.read_author_solution(author_file)

        response = TestConfig.client.post(
            f'{TestConfig.API_PATH}/de07041002_jobs_with_params',
            json={
                "student_id": 'student_id',
                "student_solution": author_code
            }
        )

        assert response.status_code == 200
        assert response.json() == {
            'message': 'Задание выполнено. Ваш код: DJhlUTi6G5',
            'status': 'success'
            }
