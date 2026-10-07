import json
from datetime import date
from typing import Dict, List

from pg_connect import PgConnect


class CouriersStgRepository:
    def __init__(self, pg: PgConnect) -> None:
        self._db = pg

    def insert_couriers(self, couriers: List[Dict]) -> None:
        with self._db.client() as conn:
            with conn.cursor() as cur:
                for c in couriers:
                    cur.execute(
                        """
                            INSERT INTO stg.deliverysystem_couriers(courier_id, courier_json, load_dt)
                            VALUES (%(c_id)s, %(c_json)s, %(dt)s)
                            ON CONFLICT (courier_id) DO UPDATE
                            SET
                                courier_json = EXCLUDED.courier_json,
                                load_dt = EXCLUDED.load_dt;
                        """,
                        {
                            "c_id": c["_id"],
                            "c_json": json.dumps(c),
                            "dt": date.today()
                        },
                    )
                conn.commit()
