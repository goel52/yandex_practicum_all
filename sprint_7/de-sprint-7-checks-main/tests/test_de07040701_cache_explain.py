from tests.test_config import TestConfig


class Test_De07040701_CacheExplain:
    def test_author(self):
        # TODO: add check py file
        author_file = 'de07040701_cache_explain.txt'

        author_code = TestConfig.read_author_solution(author_file)

        response = TestConfig.client.post(
            f'{TestConfig.API_PATH}/de07040701_cache_explain',
            json={
                "student_id": 'student_id',
                "student_solution": author_code
            }
        )

        assert response.status_code == 200
        assert response.json() == {
            'message': 'Задание выполнено. Ваш код: 1sJEyNLn4O',
            'status': 'success'
            }
