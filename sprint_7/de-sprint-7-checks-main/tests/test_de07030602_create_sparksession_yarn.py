
from tests.test_config import TestConfig


class Test_De07030602_CreateSparksessionCreateSparkSessionYarn:
    def test_author(self):
        author_file = 'de07030602_create_sparksession_yarn.py'

        author_code = TestConfig.read_author_solution(author_file)

        response = TestConfig.client.post(
            f'{TestConfig.API_PATH}/de07030602_create_sparksession_yarn',
            json={
                "student_id": 'student_id',
                "student_solution": author_code
            }
        )

        assert response.status_code == 200
        assert response.json() == {
            'message': 'Задание выполнено. Ваш код: kMCwkWEe1W',
            'status': 'success'
            }
