import time
import uuid
from contextlib import contextmanager
from datetime import datetime, timedelta
from logging import Logger
from typing import Generator

from repository import LockRepository


class FileSession:
    def __init__(self, session_id: uuid.UUID) -> None:
        self.id = session_id
        self.ttl = datetime.utcnow() + timedelta(seconds=10)


class FileCoordinator:
    def __init__(self, lr: LockRepository, log: Logger) -> None:
        self._lr = lr
        self._log = log.getChild("FileCoordinator")

    @contextmanager
    def session(self, target_file: str, user_code: str, author_file: str) -> Generator[FileSession, None, None]:
        session = FileSession(uuid.uuid4())

        try:
            try_cnt = 10
            while try_cnt > 0 and not self._lr.try_lock(target_file, session.id, session.ttl):
                try_cnt -= 1
                time.sleep(0.1)
                self._log.info(f"{datetime.utcnow()}. {try_cnt}. Sleeping. {target_file}, {session.id}, {session.ttl}")

            if try_cnt <= 0:
                raise Exception("Infrastructure is busy. Try again in a couple of minutes.")

            with open(target_file, 'w', encoding="utf-8") as f:
                f.write(user_code)

            self._log.info(f"{datetime.utcnow()}. Opened session with id {session.id} and ttl {session.ttl}")

            yield session

        except Exception as e:
            raise e

        finally:
            with open(author_file, 'r', encoding="utf-8") as fa:
                auth_code = fa.read()
            with open(target_file, 'w', encoding="utf-8") as f:
                f.write(auth_code)

            self._log.info(f"{datetime.utcnow()}. Released session with id {session.id} and ttl {session.ttl}")

            self._lr.release(session.id)
