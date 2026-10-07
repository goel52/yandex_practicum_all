
from tests.test_config import TestConfig


class Test_De07041102_SparkSubmitPyScripts:
    def test_author(self):
        author_file = 'de07041102_spark_submit_partition.txt'

        author_code = TestConfig.read_author_solution(author_file)

        response = TestConfig.client.post(
            f'{TestConfig.API_PATH}/de07041102_spark_submit_partition',
            json={
                "student_id": 'student_id',
                "student_solution": author_code
            }
        )

        assert response.status_code == 200
        assert response.json() == {
            'message': 'Задание выполнено. Ваш код: T7XQ44EsDR',
            'status': 'success'
            }
