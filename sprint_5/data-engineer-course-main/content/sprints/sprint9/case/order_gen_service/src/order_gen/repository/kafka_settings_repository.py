from datetime import datetime, timedelta
from typing import List, Optional

from order_gen.repository.pg_connect import PgConnect
from psycopg.rows import class_row
from pydantic import BaseModel


class KafkaSettingRecord(BaseModel):
    id: int
    student_id: str
    kafka_host: str
    kafka_port: int
    kafka_username: str
    kafka_password: str
    kafka_topic: str
    msg_cursor: int
    last_success: datetime
    attempt_ts: Optional[datetime]
    attempt_key: Optional[str]


class KafkaSettingsRepository:
    OCCUPATION_LIMIT = 10

    def __init__(self, pg: PgConnect) -> None:
        self._db = pg

    def save(self, student_id, kafka_host, kafka_port, kafka_username, kafka_password, topic) -> None:
        with self._db.connection() as conn:
            with conn.cursor(row_factory=class_row(KafkaSettingRecord)) as cur:
                cur.execute(
                    """
                        INSERT INTO public.kafka_settings(
                            student_id,
                            kafka_host,
                            kafka_port,
                            kafka_username,
                            kafka_password,
                            kafka_topic,
                            last_success
                        )
                        VALUES (
                            %(student_id)s,
                            %(kafka_host)s,
                            %(kafka_port)s,
                            %(kafka_username)s,
                            %(kafka_password)s,
                            %(kafka_topic)s,
                            %(last_success)s
                        )
                        ON CONFLICT (student_id) DO UPDATE
                        SET
                            kafka_host = EXCLUDED.kafka_host,
                            kafka_port = EXCLUDED.kafka_port,
                            kafka_username = EXCLUDED.kafka_username,
                            kafka_password = EXCLUDED.kafka_password,
                            kafka_topic = EXCLUDED.kafka_topic,
                            last_success = EXCLUDED.last_success;
                    """,
                    {
                        "student_id": student_id,
                        "kafka_host": kafka_host,
                        "kafka_port": kafka_port,
                        "kafka_username": kafka_username,
                        "kafka_password": kafka_password,
                        "kafka_topic": topic,
                        "last_success": datetime.utcnow()
                    },
                )
            conn.commit()

    def delete(self, student_key: str) -> None:
        with self._db.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                        DELETE FROM public.kafka_settings
                        WHERE student_id = %(student_id)s
                    """,
                    {
                        "student_id": student_key
                    },
                )

    def delete_older(self, threshold: datetime) -> None:
        with self._db.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                        DELETE FROM public.kafka_settings
                        WHERE last_success < %(threshold)s
                    """,
                    {
                        "threshold": threshold
                    },
                )

    def list(self) -> List[KafkaSettingRecord]:
        with self._db.connection() as conn:
            with conn.cursor(row_factory=class_row(KafkaSettingRecord)) as cur:
                cur.execute(
                    """
                        SELECT *
                        FROM public.kafka_settings;
                    """
                )
                objs = cur.fetchmany()
                return objs

    def get_for_student(self, student: str) -> Optional[KafkaSettingRecord]:
        with self._db.connection() as conn:
            with conn.cursor(row_factory=class_row(KafkaSettingRecord)) as cur:
                cur.execute(
                    """
                        SELECT *
                        FROM public.kafka_settings
                        WHERE student_id = %(student_id)s
                    """,
                    {
                        "student_id": student
                    },
                )
                obj = cur.fetchone()
                return obj

    def occupy(self, session_key: str) -> Optional[KafkaSettingRecord]:
        now = datetime.utcnow()
        occupation_limit = now + timedelta(minutes=self.OCCUPATION_LIMIT)

        with self._db.connection() as conn:
            with conn.cursor(row_factory=class_row(KafkaSettingRecord)) as cur:
                cur.execute(
                    """
                        UPDATE public.kafka_settings
                        SET
                            attempt_key = %(attempt_key)s,
                            attempt_ts = %(occupation_limit)s
                        WHERE
                            id=(
                                SELECT id
                                FROM public.kafka_settings
                                WHERE attempt_ts IS NULL OR attempt_ts < %(now)s
                                ORDER BY msg_cursor ASC
                                LIMIT 1
                            );
                    """,
                    {
                        "attempt_key": session_key,
                        "occupation_limit": occupation_limit,
                        "now": now
                    }
                )

                conn.commit()

                cur.execute(
                    """
                        SELECT *
                        FROM public.kafka_settings
                        WHERE attempt_key = %(attempt_key)s AND attempt_ts > %(now)s
                        LIMIT 1;
                    """,
                    {
                        "attempt_key": session_key,
                        "now": now
                    }
                )
                obj = cur.fetchone()
                return obj

    def release(self, id: int, session_key: str, msg_cursor: int, success_ts=datetime.utcnow()) -> None:

        with self._db.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                        UPDATE public.kafka_settings
                        SET
                            attempt_key = NULL,
                            attempt_ts = NULL,
                            msg_cursor = %(msg_cursor)s,
                            last_success = %(now)s
                        WHERE
                            id = %(id)s
                            AND attempt_key = %(attempt_key)s
                            AND attempt_ts > %(now)s;
                    """,
                    {
                        "msg_cursor": msg_cursor,
                        "id": id,
                        "attempt_key": session_key,
                        "now": success_ts
                    }
                )
