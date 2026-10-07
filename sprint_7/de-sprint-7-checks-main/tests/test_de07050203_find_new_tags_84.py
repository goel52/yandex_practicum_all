from tests.test_config import TestConfig


class Test_De07050203_SparkSubmitPyScripts:
    def test_author(self):
        author_file = 'de07050203_find_new_tags_84.py'

        author_code = TestConfig.read_author_solution(author_file)

        response = TestConfig.client.post(
            f'{TestConfig.API_PATH}/de07050203_find_new_tags_84',
            json={
                "student_id": 'student_id',
                "student_solution": author_code
            }
        )

        assert response.status_code == 200
        assert response.json() == {
            'message': 'Задание выполнено. Ваш код: 8IrkD1toNn',
            'status': 'success'
            }
