import json
from contextlib import contextmanager
from datetime import datetime
from typing import Generator, Optional

from pg_check_service.pg_connect import PgConnect


class PgLogger:
    def __init__(self, db: PgConnect) -> None:
        self._db = db

    def log(self, student: str, test: str, resolution: str, info: Optional[str] = None):
        with self._db.connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO pgcheck.query_log(dttm, student, test, resolution, info)
                    VALUES(%(dttm)s, %(student)s, %(test)s, %(resolution)s, %(info)s);
                """, {
                    "dttm": datetime.utcnow(),
                    "student": student,
                    "test": test,
                    "resolution": resolution,
                    "info": info
                })


class PgLogging:
    @contextmanager
    @staticmethod
    def query_log(db: PgConnect, student: str, test: str, req) -> Generator[PgLogger, None, None]:
        req_str = json.dumps(req, ensure_ascii=False)
        logger = PgLogger(db)
        try:
            logger.log(student, test, "START", req_str)
            yield logger
        except Exception as e:
            logger.log(student, test, "ERROR", str(e))
            raise e
        finally:
            logger.log(student, test, "FINISH")
