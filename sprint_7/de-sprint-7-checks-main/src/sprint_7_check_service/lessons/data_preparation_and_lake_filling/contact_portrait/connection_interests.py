"""Static checks only: no Spark, imports of student modules, exec or subprocess."""
import json

from .artifacts import FILES, check_commands, check_dag
from .job_ast import check_job


class ConnectionInterests:
    RESPONSE_KEY = 'qHZKWImPxO'

    def check(self, student_solution):
        try:
            files = json.loads(student_solution)
            if (not isinstance(files, dict) or set(files) != set(FILES)
                    or any(not isinstance(files[name], str) or not files[name].strip()
                           for name in FILES)):
                raise ValueError('Отправьте три непустых файла: connection_interests.py, run_jobs.sh, dag.py.')
            check_commands(files['run_jobs.sh'])
            check_dag(files['dag.py'])
            check_job(files['connection_interests.py'])
        except (ValueError, SyntaxError, TypeError, KeyError, RecursionError) as exc:
            return False, f'Статическая проверка: {exc}'
        return True, None
