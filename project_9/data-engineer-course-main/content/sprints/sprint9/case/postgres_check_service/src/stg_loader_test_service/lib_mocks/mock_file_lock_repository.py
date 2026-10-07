import threading
from datetime import datetime
from uuid import UUID

from repository import LockRepository


class MutexRepository(LockRepository):
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._t = 0

    def try_lock(self, target_file: str, session_id: UUID, lock_ttl: datetime) -> bool:
        self._lock.acquire()
        self._t += 1
        print(f"{datetime.utcnow()} + {self._t}")
        return True

    def release(self, session_id: UUID) -> None:
        self._t -= 1
        print(f"{datetime.utcnow()} - {self._t}")
        self._lock.release()


class AlwaysFreeRepository(LockRepository):
    def __init__(self) -> None:
        pass

    def try_lock(self, target_file: str, session_id: UUID, lock_ttl: datetime) -> bool:
        return True

    def release(self, session_id: UUID) -> None:
        pass


class AfterNTriesRepository(LockRepository):
    def __init__(self, limit: int) -> None:
        self._limit = limit
        self._cnt = 0

    def try_lock(self, target_file: str, session_id: UUID, lock_ttl: datetime) -> bool:
        self._cnt += 1
        return self._cnt > self._limit

    def release(self, session_id: UUID) -> None:
        pass
