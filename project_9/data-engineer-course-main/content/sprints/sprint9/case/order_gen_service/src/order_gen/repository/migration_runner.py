from order_gen.repository.pg_connect import PgConnect
from psycopg import Cursor


class MigrationRunner:
    def __init__(self, pg: PgConnect) -> None:
        self._db = pg

    def kafka_settings_create(self, cur: Cursor):
        cur.execute(
            """
                CREATE TABLE IF NOT EXISTS public.kafka_settings(
                    id int NOT NULL PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
                    student_id VARCHAR NOT NULL UNIQUE,
                    kafka_host VARCHAR NOT NULL,
                    kafka_port int NOT NULL,
                    kafka_username VARCHAR NOT NULL,
                    kafka_password VARCHAR NOT NULL,
                    kafka_topic VARCHAR NOT NULL,
                    msg_cursor int NOT NULL DEFAULT 0,
                    last_success timestamp NOT NULL DEFAULT NOW(),
                    attempt_ts timestamp NULL,
                    attempt_key VARCHAR NULL
                );

                CREATE INDEX IF NOT EXISTS IDX_kafka_settings__attempt_ts ON kafka_settings (attempt_ts);
            """,
        )

    def order_queue_create(self, cur: Cursor):
        cur.execute(
            """
                CREATE TABLE IF NOT EXISTS public.order_queue(
                    id int NOT NULL PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
                    order_dttm TIMESTAMP NOT NULL,
                    order_json VARCHAR NOT NULL
                );
                CREATE INDEX IF NOT EXISTS IDX_order_queue__order_dttm ON order_queue (order_dttm);
            """,
        )

    def up(self) -> None:
        with self._db.connection() as conn:
            with conn.cursor() as cur:
                self.kafka_settings_create(cur)
                self.order_queue_create(cur)
