import json
import uuid
from datetime import datetime, timedelta
from logging import Logger

from order_gen.order_generation_job.kafka_client.kafka_connector import (
    KafkaClient, KafkaConnector)
from order_gen.repository import KafkaSettingsRepository
from transaction_gen.repository import MessageQueueRepository


class TransactionDispatcher:
    BATCH_SIZE = 1000

    def __init__(self,
                 msg_queue_repository: MessageQueueRepository,
                 kafka_settings_repository: KafkaSettingsRepository,
                 kafka_certificate_path: str,
                 logger: Logger
                 ) -> None:
        self._msg_queue_repository = msg_queue_repository
        self._kafka_settings_repository = kafka_settings_repository
        self.kafka_certificate_path = kafka_certificate_path
        self._log = logger.getChild("TransactionDispatcher")

    def clear_trash(self) -> None:
        delete_kafka_settings_threshold = datetime.utcnow() - timedelta(days=1)
        self._kafka_settings_repository.delete_older(delete_kafka_settings_threshold)

    def dispatch(self) -> None:
        self._log.info(f"{datetime.utcnow()}. Start dispatch session.")

        self.clear_trash()

        session = str(uuid.uuid4())

        ks = self._kafka_settings_repository.occupy(session)
        if not ks:
            self._log.info(f"{datetime.utcnow()}. No kafkas to send orders. Skipping.")
            return

        max_msg_id = ks.msg_cursor
        messages = self._msg_queue_repository.list(max_msg_id, self.BATCH_SIZE)
        connector = KafkaConnector(ks.kafka_host, ks.kafka_port, ks.kafka_username,
                                   ks.kafka_password, ks.kafka_topic, self.kafka_certificate_path)

        self._log.info(f"{datetime.utcnow()}. Found {len(messages)} to dispatch.")
        if len(messages) == 0:
            self._kafka_settings_repository.release(ks.id, session, max_msg_id, ks.attempt_ts or datetime.utcnow())
            self._log.info(f"{datetime.utcnow()}. No messages in q. Quitting.")

        student_kafka = KafkaClient(connector)

        for object in messages:
            msg = {
                "object_id": object.object_id,
                "object_type": object.object_type,
                "sent_dttm": object.msg_dttm.isoformat(),
                "payload": object.payload
            }

            self._log.info(f"{datetime.utcnow()}. Dispatching {json.dumps(msg)}.")

            student_kafka.send(msg)
            max_msg_id = max(max_msg_id, object.id)

        self._log.info(f"{datetime.utcnow()}. max_msg_id: {max_msg_id}.")
        self._kafka_settings_repository.release(ks.id, session, max_msg_id)

        self._log.info(f"{datetime.utcnow()}. End dispatch session.")
