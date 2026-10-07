from datetime import datetime
from typing import List

from psycopg import Connection
from psycopg.rows import class_row
from pydantic import BaseModel


class TransactionRecord(BaseModel):
    operation_id: str
    account_number_from: int
    account_number_to: int
    currency_code: int
    country: str
    status: str
    transaction_type: str
    amount: int
    transaction_dt: datetime


class TransactionsRawRepository:

    def list(self, conn: Connection, operation_id: str, limit: int = 1000) -> List[TransactionRecord]:
        with conn.cursor(row_factory=class_row(TransactionRecord)) as cur:
            cur.execute(
                """
                    SELECT *
                    FROM public.transactions
                    WHERE operation_id = %(operation_filter)s
                    LIMIT %(limit)s;
                """,
                {
                    "operation_filter": operation_id,
                    "limit": limit
                }
            )
            objs = cur.fetchmany(limit)
            return objs
