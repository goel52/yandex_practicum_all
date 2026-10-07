from tests.test_config import TestConfig


class Test_De07040403_WriteParquet:
    def test_author(self):
        # TODO: add check py file
        author_file = 'de07040403_write_parquet.txt'

        author_code = TestConfig.read_author_solution(author_file)

        response = TestConfig.client.post(
            f'{TestConfig.API_PATH}/de07040403_write_parquet',
            json={
                "student_id": 'student_id',
                "student_solution": author_code
            }
        )

        assert response.status_code == 200
        assert response.json() == {
            'message': 'Задание выполнено. Ваш код: 3TkchiZud0',
            'status': 'success'
            }
