from lib.pg import PgConnect
from psycopg import Cursor


class Migrator:
    def __init__(self, db: PgConnect) -> None:
        self._db = db

    def up(self) -> None:

        with self._db.connection() as conn:
            with conn.cursor() as cur:
                self._schema(cur)
                self._order_events_create(cur)

    def _schema(self, cursor: Cursor) -> None:
        cursor.execute(
            """
                CREATE SCHEMA IF NOT EXISTS stg;
            """
        )

    def _order_events_create(self, cursor: Cursor) -> None:
        cursor.execute(
            """
                CREATE TABLE IF NOT EXISTS stg.order_events(
                    id INT NOT NULL PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
                    object_id INT NOT NULL UNIQUE,
                    object_type VARCHAR NOT NULL,
                    sent_dttm TIMESTAMP NOT NULL,
                    payload JSON NOT NULL
                );
            """
        )
