import logging
import os
from pathlib import Path

from src.stg_loader_test_service import FileCoordinator, StgLoaderCheckService
from src.stg_loader_test_service.lib_mocks import MutexRepository

log = logging.getLogger(__name__)


def author_solutions_path():
    path = Path(os.path.dirname(os.path.realpath(__file__)))
    return os.path.abspath(path.joinpath("author_solutions"))


def service_file_path():
    path = Path(os.path.dirname(os.path.realpath(__file__)))
    return os.path.abspath(path.parent.absolute().joinpath("src"))


mx = MutexRepository()
log = logging.getLogger("TEST")


class Test_StgLoaderService_Run:

    def test_run_author(self):
        service_path = service_file_path()
        author_file = "de09050605_StgMessageProcessor_run.py"

        with open(os.path.join(author_solutions_path(), author_file), 'r', encoding="utf-8") as fa:
            auth_code = fa.read()

        fc = FileCoordinator(mx, log)
        srv = StgLoaderCheckService(fc, log)
        accepted, err = srv.check_full_cycle_single(service_path, auth_code)

        assert err == ""
        assert accepted
