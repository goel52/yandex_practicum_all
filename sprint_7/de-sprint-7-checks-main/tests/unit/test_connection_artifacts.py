from pathlib import Path
import json

import pytest

from sprint_7_check_service.lessons.data_preparation_and_lake_filling.contact_portrait.artifacts import check_commands, check_dag
from sprint_7_check_service.lessons.data_preparation_and_lake_filling.contact_portrait.connection_interests import ConnectionInterests

AUTHORS = Path(__file__).resolve().parents[1] / 'author_solutions'


def bundle():
    return {'connection_interests.py': (AUTHORS / 'de07050401_connections_interests.py').read_text(),
            'run_jobs.sh': (AUTHORS / 'de07050401_run_jobs.sh').read_text(),
            'dag.py': (AUTHORS / 'de07050401_airflow_dag.py').read_text()}


def test_author_artifacts():
    files = bundle()
    check_commands(files['run_jobs.sh'])
    check_dag(files['dag.py'])


@pytest.mark.parametrize('old,new', [
    ('2022-05-25', '2022-05-31'),
    ('2022-05-25 7', '2022-05-25 28'),
    ('/user/prod/', '/user/username/'),
    ('tags_verified/actual', 'tags_verified/date=2022-05-25'),
    ('connection_interests.py', 'other.py'),
    ('/user/prod/data/analytics/connection_interests_d7', ''),
])
def test_wrong_command(old, new):
    with pytest.raises(ValueError):
        check_commands(bundle()['run_jobs.sh'].replace(old, new))


@pytest.mark.parametrize('change', ['no_dependency', 'reverse', 'depth', 'snapshot', 'prod', 'empty', 'syntax'])
def test_wrong_dag(change):
    dag = bundle()['dag.py']
    variants = {
        'no_dependency': dag.replace(' >> connection_interests_d7', ''),
        'reverse': dag.replace(' >> connection_interests_d7', ' << connection_interests_d7'),
        'depth': dag.replace('"2022-05-31", "7"', '"2022-05-31", "28"'),
        'snapshot': dag.replace('tags_verified/actual', 'tags_verified/old'),
        'prod': dag.replace('/user/username/', '/user/prod/'),
        'empty': 'pass',
        'syntax': '(',
    }
    with pytest.raises((ValueError, SyntaxError)):
        check_dag(variants[change])


def test_dag_alternative_dependency_notation():
    dag = bundle()['dag.py'].replace('events_partitioned >> user_interests_d7 >> connection_interests_d7',
                                    'events_partitioned >> user_interests_d7\nconnection_interests_d7.set_upstream(user_interests_d7)')
    check_dag(dag)


@pytest.mark.parametrize('key,value', [('dag.py', ''), ('run_jobs.sh', 123), ('extra.py', 'pass')])
def test_invalid_bundle(key, value):
    files = bundle()
    files[key] = value
    status, message = ConnectionInterests().check(json.dumps(files))
    assert not status
    assert 'три непустых файла' in message


def test_shared_current_snapshot():
    check_commands(bundle()['run_jobs.sh'].replace(
        '/user/prod/data/snapshots', '/user/master/data/snapshots'))


def test_dag_cycle():
    with pytest.raises(ValueError, match='цикл'):
        check_dag(bundle()['dag.py'] + '\nconnection_interests_d7 >> user_interests_d7\n')


def test_static_check_never_executes_student_module(tmp_path):
    files = bundle()
    marker = tmp_path / 'must-not-exist'
    files['connection_interests.py'] += f"\nopen({str(marker)!r}, 'w').write('executed')\nraise RuntimeError('executed')\n"
    assert ConnectionInterests().check(json.dumps(files))[0]
    assert not marker.exists()
