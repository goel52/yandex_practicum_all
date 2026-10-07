
from tests.test_config import TestConfig


class Test_De07041201_JobBashOperator:
    def test_author_job_bash(self):
        author_file = 'de07041201_job_bash_operator.py'

        author_code = TestConfig.read_author_solution(author_file)

        response = TestConfig.client.post(
            f'{TestConfig.API_PATH}/de07041201_job_bash_or_spark_operator',
            json={
                "student_id": 'student_id',
                "student_solution": author_code
            }
        )

        assert response.status_code == 200
        assert response.json() == {
            'message': 'Задание выполнено. Ваш код: WPs40lac6U',
            'status': 'success'
            }

    def test_author_job_spark(self):
        author_file = 'de07041201_job_spark_submit_operator.py'

        author_code = TestConfig.read_author_solution(author_file)

        response = TestConfig.client.post(
            f'{TestConfig.API_PATH}/de07041201_job_bash_or_spark_operator',
            json={
                "student_id": 'student_id',
                "student_solution": author_code
            }
        )

        assert response.status_code == 200
        assert response.json() == {
            'message': 'Задание выполнено. Ваш код: WPs40lac6U',
            'status': 'success'
            }
