import logging
import os
from pathlib import Path

from src.stg_loader_test_service import FileCoordinator, StgLoaderCheckService
from src.stg_loader_test_service.lib_mocks import (AlwaysFreeRepository,
                                                   MutexRepository)

log = logging.getLogger(__name__)


def author_solutions_path():
    path = Path(os.path.dirname(os.path.realpath(__file__)))
    return os.path.abspath(path.joinpath("author_solutions"))


def service_file_path():
    path = Path(os.path.dirname(os.path.realpath(__file__)))
    return os.path.abspath(path.parent.absolute().joinpath("src"))


mx = MutexRepository()
log = logging.getLogger("TEST")


class Test_StgLoaderService_Init:

    def test_init_author(self):
        service_path = service_file_path()
        author_file = "de09050603_StgMessageProcessor_Init.py"

        with open(os.path.join(author_solutions_path(), author_file), 'r', encoding="utf-8") as fa:
            auth_code = fa.read()

        fc = FileCoordinator(mx, log)
        srv = StgLoaderCheckService(fc, log)
        accepted, err = srv.check_init(service_path, auth_code)

        assert accepted
        assert err == ""

    def test_init_empty(self):
        service_path = service_file_path()
        fc = FileCoordinator(AlwaysFreeRepository(), log)
        srv = StgLoaderCheckService(fc, log)

        code = ""

        accepted, err = srv.check_init(service_path, code)
        assert not accepted
        assert err == "В вашем коде не найден класс StgMessageProcessor"

    def test_init_less_args(self):
        service_path = service_file_path()
        fc = FileCoordinator(AlwaysFreeRepository(), log)
        srv = StgLoaderCheckService(fc, log)

        code = """
class StgMessageProcessor:
    def __init__(self,
                 consumer,
                 producer,
                 redis_client,
                 logger) -> None:
        self._consumer = consumer
        self._producer = producer
        self._redis = redis_client
        self._logger = logger

    def run(self):
        pass
"""
        accepted, err = srv.check_init(service_path, code)
        assert not accepted
        assert err == "У вас в __init__ 5 параметров, а должно быть 7: self, consumer, producer, redis_client, stg_repository, batch_size, logger"  # noqa

    def test_init_more_args(self):
        service_path = service_file_path()
        fc = FileCoordinator(AlwaysFreeRepository(), log)
        srv = StgLoaderCheckService(fc, log)

        code = """
class StgMessageProcessor:
    def __init__(self,
                 consumer,
                 producer,
                 redis_client,
                 stg_repository,
                 batch_size,
                 redundant_arg,
                 logger) -> None:
        self._consumer = consumer
        self._producer = producer
        self._redis = redis_client
        self._stg_repository = stg_repository
        self._batch_size = batch_size
        self._redundant_arg = redundant_arg
        self._logger = logger

    def run(self):
        pass

"""

        accepted, err = srv.check_init(service_path, code)
        assert not accepted
        assert err == "У вас в __init__ 8 параметров, а должно быть 7: self, consumer, producer, redis_client, stg_repository, batch_size, logger"  # noqa
