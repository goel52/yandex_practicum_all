import uuid
from datetime import datetime
from logging import Logger
from typing import Any

from order_gen.repository.pg_connect import PgConnect
from transaction_gen.repository import (CurrencyRawRepository, CurrencyRecord,
                                        Message, MessageBuilder,
                                        MessageQueueRepository,
                                        TransactionRecord,
                                        TransactionsRawRepository)
from transaction_gen.repository.transaction_to_msg_queue_repository import \
    Transactions2MsgQueueRepository


class MessageQueueInitializer:
    TRANSACTION = "TRANSACTION"
    CURRENCY = "CURRENCY"

    def __init__(self,
                 db: PgConnect,
                 currency_repository: CurrencyRawRepository,
                 msg_repository: MessageQueueRepository,
                 log: Logger
                 ) -> None:
        self._db = db
        self.transactions_repo = TransactionsRawRepository()
        self.currency_repo = currency_repository
        self.trans_q_repository = Transactions2MsgQueueRepository()
        self.msg_repository = msg_repository
        self._log = log

        self.ns_uuid = uuid.UUID('d4dc5ac0-49c6-49c9-b5f4-5fdc183e9c7a')

    def _uuid(self, obj: Any) -> uuid.UUID:
        return uuid.uuid5(namespace=self.ns_uuid, name=str(obj))

    def _currency_to_msg(self, cur: CurrencyRecord) -> Message:
        msg = {
            "date_update": cur.date_update,
            "currency_code": cur.currency_code,
            "currency_code_with": cur.currency_code_with,
            "currency_with_div": cur.currency_with_div,
        }
        msg_id = self._uuid(f"{cur.date_update.isoformat()}#{cur.currency_code}#{cur.currency_code_with}")
        return MessageBuilder.build(str(msg_id), self.CURRENCY, cur.date_update, msg)

    def _transaction_to_msg(self, tran: TransactionRecord) -> Message:
        msg = {
            "operation_id": tran.operation_id,
            "account_number_from": tran.account_number_from,
            "account_number_to": tran.account_number_to,
            "currency_code": tran.currency_code,
            "country": tran.country,
            "status": tran.status,
            "transaction_type": tran.transaction_type,
            "amount": tran.amount,
            "transaction_dt": tran.transaction_dt
        }
        return MessageBuilder.build(tran.operation_id, self.TRANSACTION, tran.transaction_dt, msg)

    def build_currency_queue(self) -> None:
        currencies = self.currency_repo.list()
        self._log.info(f"{datetime.utcnow()} Found {len(currencies)} currencies in raw storage.")
        currency_msgs = [self._currency_to_msg(c) for c in currencies]

        existing_msgs = self.msg_repository.list_with_type(self.CURRENCY)
        existing_dict = {}
        for existing_msg in existing_msgs:
            existing_dict[existing_msg.object_id] = existing_msg

        load_queue = [c for c in currency_msgs if c.object_id not in existing_dict]
        self._log.info(f"{datetime.utcnow()} Found {len(load_queue)} transactions to queue.")

        with self._db.connection() as conn:
            self.msg_repository.save_list(conn, load_queue)

    def build_message_queue(self) -> None:
        with self._db.connection() as conn:
            trans_q = self.trans_q_repository.list(conn, 1000)
            trans_q.sort(key=lambda x: x.operation_dttm)
            i = 0
            cnt = 0

            self._log.info(f"{datetime.utcnow()} Found {len(trans_q)} transactions to queue.")

            for trans_id in trans_q:
                trans = self.transactions_repo.list(conn, trans_id.operation_id)
                tran_msgs = [self._transaction_to_msg(t) for t in trans]
                tran_msgs.sort(key=lambda x: x.msg_dttm)

                self.msg_repository.save_list(conn, tran_msgs)
                i += 1
                cnt += len(tran_msgs)
                if i % 10 == 0:
                    self._log.info(f"{datetime.utcnow()} Processed {i}. Loaded {cnt}.")

                self.trans_q_repository.delete(conn, trans_id.operation_id)

        self._log.info(f"{datetime.utcnow()} Load finished.")
