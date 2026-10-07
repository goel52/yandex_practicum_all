
from tests.test_config import TestConfig


class Test_De07041001_JsonToParquet:
    def test_author(self):
        # TODO: add check py file
        author_file = 'de07041001_json_to_parquet.txt'

        author_code = TestConfig.read_author_solution(author_file)

        response = TestConfig.client.post(
            f'{TestConfig.API_PATH}/de07041001_json_to_parquet',
            json={
                "student_id": 'student_id',
                "student_solution": author_code
            }
        )

        assert response.status_code == 200
        assert response.json() == {
            'message': 'Задание выполнено. Ваш код: MisYAUZkzJ',
            'status': 'success'
            }
