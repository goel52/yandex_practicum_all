import os
from pathlib import Path

from fastapi.testclient import TestClient

from src.sprint_7_check_service.run import app


class TestConfig:

    API_PATH = '/api/v1/checks'

    client = TestClient(app)

    @staticmethod
    def author_solutions_path():
        path = Path(os.path.dirname(os.path.realpath(__file__)))
        return os.path.abspath(path.joinpath("author_solutions"))

    @staticmethod
    def read_author_solution(filename: str) -> str:
        with open(os.path.join(TestConfig.author_solutions_path(),
                               filename), 'r', encoding="utf-8") as fa:
            auth_code = fa.read()
        return auth_code
