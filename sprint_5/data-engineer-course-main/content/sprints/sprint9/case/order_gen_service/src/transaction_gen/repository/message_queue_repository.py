import json
from datetime import datetime
from typing import Dict, List, Optional

from order_gen.repository.pg_connect import PgConnect
from psycopg import Connection
from psycopg.rows import class_row
from pydantic import BaseModel
from transaction_gen.dict_util import to_dict


class Message:
    def __init__(self, id: int, object_id: str, object_type: str, msg_dttm: datetime, payload: Dict) -> None:
        self.id = id
        self.object_id = object_id
        self.object_type = object_type
        self.msg_dttm = msg_dttm
        self.payload = payload


class MessageRecord(BaseModel):
    id: int
    object_id: str
    object_type: str
    msg_dttm: datetime
    payload: Dict


class MessageBuilder:
    @staticmethod
    def from_dbo(dbo: MessageRecord) -> Message:
        return Message(dbo.id, dbo.object_id, dbo.object_type, dbo.msg_dttm, dbo.payload)

    @staticmethod
    def to_dbo(msg: Message) -> MessageRecord:
        safe_dict: Dict = to_dict(msg.payload)  # type: ignore
        return MessageRecord(id=msg.id,
                             object_id=msg.object_id,
                             object_type=msg.object_type,
                             msg_dttm=msg.msg_dttm,
                             payload=safe_dict
                             )

    @staticmethod
    def build(object_id: str, object_type: str, dttm: datetime, payload: Dict) -> Message:
        return Message(0, object_id, object_type, dttm, payload)


class MessageQueueRepository:
    def __init__(self, pg: PgConnect) -> None:
        self._db = pg

    def save_list(self, conn: Connection, msgs: List[Message]) -> None:
        for msg in msgs:
            self._save(conn, MessageBuilder.to_dbo(msg))

    def _save(self, conn: Connection, msg: MessageRecord) -> None:
        with conn.cursor() as cur:
            cur.execute(
                """
                    INSERT INTO public.message_queue(
                        object_id,
                        object_type,
                        msg_dttm,
                        payload
                    )
                    VALUES (
                        %(object_id)s,
                        %(object_type)s,
                        %(msg_dttm)s,
                        %(payload)s
                    );
                """,
                {
                    "object_id": msg.object_id,
                    "object_type": msg.object_type,
                    "msg_dttm": msg.msg_dttm,
                    "payload": json.dumps(msg.payload)
                }
            )

    def list(self, id_filter: int, limit: int) -> List[Message]:
        with self._db.connection() as conn:
            with conn.cursor(row_factory=class_row(MessageRecord)) as cur:
                cur.execute(
                    """
                        SELECT *
                        FROM public.message_queue
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
                return [MessageBuilder.from_dbo(o) for o in objs]

    def list_with_type(self, type: str, limit: int = 10000) -> List[Message]:
        with self._db.connection() as conn:
            with conn.cursor(row_factory=class_row(MessageRecord)) as cur:
                cur.execute(
                    """
                        SELECT *
                        FROM public.message_queue
                        WHERE object_type = %(type_filter)s
                        LIMIT %(limit)s;
                    """,
                    {
                        "type_filter": type,
                        "limit": limit
                    }
                )
                objs = cur.fetchmany(limit)
                return [MessageBuilder.from_dbo(o) for o in objs]

    def max_id_by_type(self, type: str) -> Optional[Message]:
        with self._db.connection() as conn:
            with conn.cursor(row_factory=class_row(MessageRecord)) as cur:
                cur.execute(
                    """
                        SELECT *
                        FROM public.message_queue
                        WHERE object_id = (
                            SELECT max(object_id)
                            FROM public.message_queue
                            WHERE object_type = %(type_filter)s
                        );
                    """,
                    {
                        "type_filter": type
                    }
                )
                obj = cur.fetchone()
        if not obj:
            return None
        return MessageBuilder.from_dbo(obj)
