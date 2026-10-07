from datetime import datetime
from typing import List

from psycopg import Connection
from psycopg.rows import class_row
from pydantic import BaseModel


class TransactionQRecord(BaseModel):
    id: int
    operation_id: str
    operation_dttm: datetime


class Transactions2MsgQueueRepository:
    def __init__(self) -> None:
        pass

    def list(self, conn: Connection, limit: int = 10000) -> List[TransactionQRecord]:
        with conn.cursor(row_factory=class_row(TransactionQRecord)) as cur:
            cur.execute(
                """
                    SELECT *
                    FROM public.transaction_to_message_queue
                    ORDER BY operation_dttm ASC
                    LIMIT %(limit)s;
                """,
                {
                    "limit": limit
                }
            )
            objs = cur.fetchmany(limit)
            return objs

    def delete(self, conn: Connection, operation_id: str) -> None:
        with conn.cursor(row_factory=class_row(TransactionQRecord)) as cur:
            cur.execute(
                """
                    DELETE
                    FROM public.transaction_to_message_queue
                    WHERE operation_id = %(op_id)s;
                """,
                {
                    "op_id": operation_id
                }
            )
