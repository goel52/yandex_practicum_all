"""Run checkers without importing the application or starting a JVM.

The six checks that execute DataFrame operations remain covered by API tests.
Passing None is limited to legacy signatures whose spark argument is unused.
"""
import ast
import importlib
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
ENDPOINTS = ROOT / 'src/sprint_7_check_service/api/api_v1/endpoints/checks'
SPARK_CHECKS = {'de07050202', 'de07050203', 'de07050301', 'de07050302',
                'de07050303', 'de07050304'}


def author_cases():
    for test in sorted((ROOT / 'tests').glob('test_de*.py')):
        task_id = test.name[5:15]
        if task_id in SPARK_CHECKS:
            continue
        endpoint = next(ENDPOINTS.glob(task_id + '*.py'))
        imports = [node for node in ast.parse(endpoint.read_text()).body
                   if isinstance(node, ast.ImportFrom)
                   and node.module and '.lessons.' in node.module]
        for node in ast.walk(ast.parse(test.read_text())):
            if (isinstance(node, ast.Assign)
                    and any(isinstance(t, ast.Name) and t.id == 'author_file'
                            for t in node.targets)):
                yield pytest.param(imports, node.value.value,
                                   id=node.value.value)


@pytest.mark.parametrize('imports,author_file', list(author_cases()))
def test_author_without_spark(imports, author_file):
    solution = (ROOT / 'tests/author_solutions' / author_file).read_text()
    for entry in imports:
        checker = getattr(importlib.import_module(entry.module),
                          entry.names[0].name)()
        import inspect
        kwargs = {'spark': None} if 'spark' in inspect.signature(checker.check).parameters else {}
        status, message = checker.check(solution, **kwargs)
        assert status, message
