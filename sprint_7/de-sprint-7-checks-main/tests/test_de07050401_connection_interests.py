import json

import pytest

from tests.test_config import TestConfig

PATH = f'{TestConfig.API_PATH}/de07050401_connection_interests/'


def author_files():
    return {
        'connection_interests.py': TestConfig.read_author_solution('de07050401_connections_interests.py'),
        'run_jobs.sh': TestConfig.read_author_solution('de07050401_run_jobs.sh'),
        'dag.py': TestConfig.read_author_solution('de07050401_airflow_dag.py'),
    }


def check(files):
    return TestConfig.client.post(PATH, json={
        'student_id': 'student_id', 'student_solution': json.dumps(files)},
        follow_redirects=False)


def test_author():
    response = check(author_files())
    assert response.status_code == 200
    assert response.json() == {
        'status': 'success', 'message': 'Задание выполнено. Ваш код: qHZKWImPxO'}


@pytest.mark.parametrize('mutation', ['direct_rank', 'subscription_count', 'inner_join', 'period',
                                     'history', 'future', 'unverified', 'outgoing_only'])
def test_structural_errors(mutation):
    files = author_files()
    job = files['connection_interests.py']
    if mutation == 'direct_rank':
        job = job.replace("F.desc('tag_count'), F.desc('tag')", "F.desc('tag'), F.desc('tag_count')")
    elif mutation == 'subscription_count':
        job = job.replace('F.count("*")', 'F.countDistinct("*")')
    elif mutation == 'inner_join':
        job = job.replace('"full_outer"', '"inner"')
    elif mutation == 'period':
        job = job.replace('range(int(depth))', 'range(1)')
    elif mutation == 'history':
        job = job.replace('sql.read.parquet(events_base_path)',
                          'sql.read.option("basePath", events_base_path).parquet(*input_event_paths(events_base_path, date, days_count))')
    elif mutation == 'future':
        job = job.replace(" and date <= '{date}'", '')
    elif mutation == 'unverified':
        job = job.replace(".join(verified_tags, 'tag', 'left_semi')", '')
    elif mutation == 'outgoing_only':
        job = job.replace('F.col("event.message_from"),\n                F.col("event.message_to")))',
                          'F.col("event.message_from")))')
    assert job != files['connection_interests.py']
    files['connection_interests.py'] = job
    response = check(files)
    assert response.status_code == 200
    assert response.json()['status'] == 'error'
    assert 'Статическая проверка:' in response.json()['message']


@pytest.mark.parametrize('files', [{}, [], {'connection_interests.py': 'pass'}])
def test_incomplete_bundle(files):
    response = check(files)
    assert response.status_code == 200
    assert response.json()['status'] == 'error'


def test_raw_source_is_not_a_bundle():
    response = TestConfig.client.post(PATH, json={
        'student_id': 'student_id', 'student_solution': 'print(1)'})
    assert response.status_code == 200
    assert response.json()['status'] == 'error'


@pytest.mark.parametrize('old,new', [
    ('output_base_path = sys.argv[6]', 'output_base_path = sys.argv[5]'),
    ('{output_base_path}/date={date}', '{output_base_path}/wrong={date}'),
    ('def get_contacts(', 'def other_contacts('),
])
def test_parameters_paths_and_template(old, new):
    files = author_files()
    files['connection_interests.py'] = files['connection_interests.py'].replace(old, new)
    response = check(files)
    assert response.status_code == 200
    assert response.json()['status'] == 'error'


def test_comments_do_not_replace_real_aggregation():
    files = author_files()
    files['connection_interests.py'] = files['connection_interests.py'].replace(
        'F.count("*")', 'F.countDistinct("*")') + '\n# F.count("*")\n'
    assert check(files).json()['status'] == 'error'


def test_endpoint_starts_no_process(monkeypatch):
    import subprocess

    def forbidden(*args, **kwargs):
        raise AssertionError('Static checks must not start Python or JVM processes')

    monkeypatch.setattr(subprocess, 'Popen', forbidden)
    assert check(author_files()).json()['status'] == 'success'
