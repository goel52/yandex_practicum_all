import json

from pg_connect import PgConnect


class PgSaver:
    def __init__(self, connect: PgConnect) -> None:
        self.conn = connect.client()

    def save_object(self, collection_name: str, id: str, val) -> None:

        str_val = json.dumps(val)
        self._upsert_value(collection_name, id, str_val)

    def _upsert_value(self, collection_name: str, id: str, val: str):
        with self.conn.cursor() as cur:
            cur.execute("""
                            INSERT INTO stg.ordersystem_{collection_name}(object_id, object_value)
                            VALUES (%(id)s, %(val)s)
                            ON CONFLICT (object_id) DO UPDATE
                            SET object_value = EXCLUDED.object_value;
                        """.format(collection_name=collection_name),
                        {"id": id, "val": val},
                        )
            self.conn.commit()

    def init_collection(self, collection_name: str) -> None:
        with self.conn.cursor() as cur:
            cur.execute("""
                            CREATE TABLE IF NOT EXISTS stg.ordersystem_{collection_name} (
                                id int NOT NULL PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
                                object_id varchar NOT NULL UNIQUE,
                                object_value text NOT NULL
                            );
                        """.format(collection_name=collection_name)
                        )
            self.conn.commit()
