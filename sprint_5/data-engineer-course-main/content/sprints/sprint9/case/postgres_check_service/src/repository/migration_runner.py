from datetime import datetime, timedelta

from pg_check_service import PgConnect
from psycopg import Cursor


class MigrationRunner:
    LOG_TTL_DAYS = 30

    def __init__(self, pg: PgConnect) -> None:
        self._db = pg

    def schema_create(self, cur: Cursor):
        cur.execute(
            """
                CREATE SCHEMA IF NOT EXISTS pgcheck;
            """,
        )

    def query_log_create(self, cur: Cursor):
        cur.execute(
            """
                CREATE TABLE IF NOT EXISTS pgcheck.query_log(
                    id int NOT NULL PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
                    dttm TIMESTAMP NOT NULL,
                    student VARCHAR NOT NULL,
                    test VARCHAR NOT NULL,
                    resolution VARCHAR NOT NULL,
                    info VARCHAR NULL
                );

                CREATE INDEX IF NOT EXISTS IDX_query_log__dttm ON pgcheck.query_log (dttm);
                CREATE INDEX IF NOT EXISTS IDX_query_log__student_dttm ON pgcheck.query_log (student, dttm);
                CREATE INDEX IF NOT EXISTS IDX_query_log__student_dttm ON pgcheck.query_log (test, dttm);
            """,
        )

    def file_locks_create(self, cur: Cursor):
        cur.execute(
            """
                CREATE TABLE IF NOT EXISTS pgcheck.file_locks(
                    id int NOT NULL PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
                    target VARCHAR NOT NULL UNIQUE,
                    session_id UUID NOT NULL,
                    lock_ttl TIMESTAMP NOT NULL
                );

                CREATE INDEX IF NOT EXISTS IDX_file_locks__session_id ON pgcheck.file_locks (session_id);
                CREATE INDEX IF NOT EXISTS IDX_file_locks__lock_ttl ON pgcheck.file_locks (lock_ttl);
            """,
        )

    def query_log_ttl(self, cur: Cursor):
        cur.execute(
            """
                DELETE FROM pgcheck.query_log
                WHERE dttm < %(threshold)s
            """,
            {
                "threshold": datetime.utcnow() - timedelta(days=self.LOG_TTL_DAYS)
            },
        )

    def up(self) -> None:
        with self._db.connection() as conn:
            with conn.cursor() as cur:
                self.schema_create(cur)
                self.query_log_create(cur)
                self.query_log_ttl(cur)
                self.file_locks_create(cur)
            conn.commit()
