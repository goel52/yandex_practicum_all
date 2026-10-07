from datetime import datetime
from typing import List

from order_gen.repository.pg_connect import PgConnect
from psycopg.rows import class_row
from pydantic import BaseModel


class CurrencyRecord(BaseModel):
    date_update: datetime
    currency_code: int
    currency_code_with: int
    currency_with_div: float


class CurrencyRawRepository:
    def __init__(self, pg: PgConnect) -> None:
        self._db = pg

    def list(self) -> List[CurrencyRecord]:
        with self._db.connection() as conn:
            with conn.cursor(row_factory=class_row(CurrencyRecord)) as cur:
                cur.execute(
                    """
                        SELECT *
                        FROM public.currencies
                        ORDER BY currency_code ASC;
                    """
                )
                objs = cur.fetchall()
                return objs
