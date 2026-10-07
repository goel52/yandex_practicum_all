from tests.test_config import TestConfig


class Test_De07050302_ReactionTagTops:
    def test_author(self):
        author_file = 'de07050302_reaction_tag_tops.py'

        author_code = TestConfig.read_author_solution(author_file)

        response = TestConfig.client.post(
            f'{TestConfig.API_PATH}/de07050302_reaction_tag_tops',
            json={
                "student_id": 'student_id',
                "student_solution": author_code
            }
        )

        assert response.status_code == 200
        assert response.json() == {
            'message': 'Задание выполнено. Ваш код: gvWFf0D782',
            'status': 'success'
            }
