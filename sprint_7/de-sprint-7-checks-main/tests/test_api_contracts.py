import pytest

from tests.test_config import TestConfig

PATHS = sorted(path for path in TestConfig.client.app.openapi()['paths']
               if path.startswith(TestConfig.API_PATH + '/'))


@pytest.mark.parametrize('path', ('/docs', '/redoc', '/openapi.json'))
def test_api_documentation_is_not_public(path):
    assert TestConfig.client.get(path).status_code == 404


@pytest.mark.parametrize('path', PATHS)
def test_check_contract(path):
    """All published routes accept POST JSON and validate both required fields."""
    operation = TestConfig.client.app.openapi()['paths'][path]['post']
    assert path.endswith('/')
    assert operation['requestBody']['content']['application/json']['schema'] == {
        '$ref': '#/components/schemas/CheckRequest'}
    assert operation['responses']['200']['content']['application/json']['schema'] == {
        '$ref': '#/components/schemas/CheckResponse'}
    assert TestConfig.client.get(path, follow_redirects=False).status_code == 405
    for payload in ({}, {'student_id': 'student_id'}, {'student_solution': 'pass'}):
        assert TestConfig.client.post(path, json=payload,
                                      follow_redirects=False).status_code == 422
