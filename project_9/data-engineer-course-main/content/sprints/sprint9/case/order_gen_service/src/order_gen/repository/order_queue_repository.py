import json
from datetime import datetime
from typing import Dict, List

from order_gen.repository.pg_connect import PgConnect
from psycopg.rows import class_row
from pydantic import BaseModel


class OrderRecord(BaseModel):
    id: int
    order_dttm: datetime
    order_json: str


class OrderQueueRepository:
    def __init__(self, pg: PgConnect) -> None:
        self._db = pg

    def save(self, order: Dict) -> None:
        with self._db.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                        INSERT INTO public.order_queue(
                            order_dttm,
                            order_json
                        )
                        VALUES (
                            %(order_dttm)s,
                            %(order_json)s
                        )
                    """,
                    {
                        "order_dttm": datetime.utcnow(),
                        "order_json": json.dumps(order)
                    }
                )
            conn.commit()

    def delete_older(self, threshold: datetime) -> None:
        with self._db.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                        DELETE FROM public.order_queue
                        WHERE order_dttm < %(threshold)s;
                    """,
                    {
                        "threshold": threshold
                    },
                )
            conn.commit()

    def list(self, id_filter: int, limit: int) -> List[OrderRecord]:
        with self._db.connection() as conn:
            with conn.cursor(row_factory=class_row(OrderRecord)) as cur:
                cur.execute(
                    """
                        SELECT *
                        FROM public.order_queue
                        WHERE id > %(id_filter)s
                        ORDER BY id ASC
                        LIMIT %(limit)s;
                    """,
                    {
                        "id_filter": id_filter,
                        "limit": limit
                    }
                )
                objs = cur.fetchmany(limit)
                return objs
