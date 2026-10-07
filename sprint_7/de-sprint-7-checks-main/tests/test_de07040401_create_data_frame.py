from tests.test_config import TestConfig


class Test_De07040401_CreateDataFrame:
    def test_author(self):
        # TODO: add check py file
        author_file = 'de07040401_create_data_frame.txt'

        author_code = TestConfig.read_author_solution(author_file)

        response = TestConfig.client.post(
            f'{TestConfig.API_PATH}/de07040401_create_data_frame',
            json={
                "student_id": 'student_id',
                "student_solution": author_code
            }
        )

        assert response.status_code == 200
        assert response.json() == {
            'message': 'Задание выполнено. Ваш код: zZoMQveyrG',
            'status': 'success'
            }
