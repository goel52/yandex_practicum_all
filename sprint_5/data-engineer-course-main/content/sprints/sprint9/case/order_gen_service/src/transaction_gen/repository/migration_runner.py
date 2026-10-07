from logging import Logger

from order_gen.repository.pg_connect import PgConnect
from psycopg import Cursor
from transaction_gen.repository.currency_repository import \
    CurrencyRawRepository
from transaction_gen.repository.message_queue_repository import \
    MessageQueueRepository
from transaction_gen.repository.transaction_msg_builder import \
    MessageQueueInitializer


class TransactionMigrationRunner:
    def __init__(self, pg: PgConnect, log: Logger) -> None:
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

    def message_queue_create(self, cur: Cursor):
        cur.execute(
            """
                CREATE TABLE IF NOT EXISTS public.message_queue(
                    id INT NOT NULL PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
                    object_id VARCHAR NOT NULL,
                    object_type VARCHAR NOT NULL,
                    msg_dttm TIMESTAMP NOT NULL,
                    payload JSON NOT NULL
                );
                CREATE INDEX IF NOT EXISTS IDX_message_queue__msg_dttm ON message_queue(msg_dttm);
            """,
        )

    def transaction_to_message_queue_create(self, cur: Cursor):
        cur.execute(
            """
                CREATE TABLE IF NOT EXISTS public.transaction_to_message_queue(
                    id INT NOT NULL PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
                    operation_id VARCHAR NOT NULL UNIQUE,
                    operation_dttm TIMESTAMP NOT NULL
                );
                CREATE INDEX IF NOT EXISTS IDX_transaction_to_message_queue__operation_dttm
                    ON transaction_to_message_queue(operation_dttm);

                --INSERT INTO transaction_to_message_queue (operation_id, operation_dttm)
                --SELECT operation_id, min(transaction_dt)
                --FROM transactions t
                --GROUP BY operation_id
                --ORDER BY 2 ASC;
            """,
        )

    def up(self) -> None:
        with self._db.connection() as conn:
            with conn.cursor() as cur:
                self.kafka_settings_create(cur)
                self.message_queue_create(cur)
                self.transaction_to_message_queue_create(cur)


class TransactionDataMigrationRunner:
    def __init__(self, pg: PgConnect, log: Logger) -> None:
        self._db = pg

        self.message_init = MessageQueueInitializer(
            pg,
            CurrencyRawRepository(pg),
            MessageQueueRepository(pg),
            log)

    def run(self) -> None:
        self.message_init.build_currency_queue()
        self.message_init.build_message_queue()
