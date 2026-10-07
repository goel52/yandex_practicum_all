from datetime import datetime
from logging import Logger
from uuid import UUID

from pg_check_service import PgConnect


class LockRepository:
    def __init__(self, db: PgConnect, log: Logger) -> None:
        self._db = db
        self._log = log

    def try_lock(self, target_file: str, session_id: UUID, lock_ttl: datetime) -> bool:
        try:
            with self._db.connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        DELETE FROM pgcheck.file_locks
                        WHERE lock_ttl < %(now)s;
                    """, {
                        "now": datetime.utcnow(),
                    })

                    cur.execute("""
                        INSERT INTO pgcheck.file_locks(target, session_id, lock_ttl)
                        VALUES (%(target)s, %(session_id)s, %(lock_ttl)s);
                    """, {
                        "target": target_file,
                        "session_id": session_id,
                        "lock_ttl": lock_ttl
                    })

            return True

        except Exception as e:
            self._log.info(f"{datetime.utcnow()}. Error: {str(e)}")
            return False

    def release(self, session_id: UUID) -> None:
        with self._db.connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    DELETE FROM pgcheck.file_locks
                    WHERE session_id = %(session_id)s;
                """, {
                    "session_id": session_id
                })
