from tests.test_config import TestConfig


class Test_De07050205_DagJobaFindNewTags:
    def test_author(self):
        author_file = 'de07050205_dag_joba_find_new_tags.py'

        author_code = TestConfig.read_author_solution(author_file)

        response = TestConfig.client.post(
            f'{TestConfig.API_PATH}/de07050205_dag_joba_find_new_tags',
            json={
                "student_id": 'student_id',
                "student_solution": author_code
            }
        )

        assert response.status_code == 200
        assert response.json() == {
            'message': 'Задание выполнено. Ваш код: tWPYxsMDWU',
            'status': 'success'
            }
