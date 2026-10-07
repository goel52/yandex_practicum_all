
from tests.test_config import TestConfig


class Test_De07040901_WindowOrderByPA:
    def test_author(self):
        # TODO: add check py file
        author_file = 'de07040901_window_orderby_pa.txt'

        author_code = TestConfig.read_author_solution(author_file)

        response = TestConfig.client.post(
            f'{TestConfig.API_PATH}/de07040901_window_orderby_pa',
            json={
                "student_id": 'student_id',
                "student_solution": author_code
            }
        )

        assert response.status_code == 200
        assert response.json() == {
            'message': 'Задание выполнено. Ваш код: Zv6vxsDQLo',
            'status': 'success'
            }
