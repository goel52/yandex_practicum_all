import json
import uuid
from datetime import datetime, timedelta
from logging import Logger

from order_gen.order_generation_job.kafka_client.kafka_connector import (
    KafkaClient, KafkaConnector)
from order_gen.repository import KafkaSettingsRepository, OrderQueueRepository


class OrderDispatcher:
    BATCH_SIZE = 100

    def __init__(self,
                 order_queue_repository: OrderQueueRepository,
                 kafka_settings_repository: KafkaSettingsRepository,
                 kafka_certificate_path: str,
                 logger: Logger
                 ) -> None:
        self._order_queue_repository = order_queue_repository
        self._kafka_settings_repository = kafka_settings_repository
        self.kafka_certificate_path = kafka_certificate_path
        self._log = logger.getChild("OrderDispatcher")

    def clear_trash(self) -> None:
        delete_kafka_settings_threshold = datetime.utcnow() - timedelta(days=1)
        self._kafka_settings_repository.delete_older(delete_kafka_settings_threshold)

        delete_orders_threshold = datetime.utcnow() - timedelta(days=7)
        self._order_queue_repository.delete_older(delete_orders_threshold)

    def dispatch_order(self) -> None:
        self._log.info(f"{datetime.utcnow()}. Start dispatch session.")

        self.clear_trash()

        session = str(uuid.uuid4())

        ks = self._kafka_settings_repository.occupy(session)
        if not ks:
            self._log.info(f"{datetime.utcnow()}. No kafkas to send orders. Skipping.")
            return

        max_order_id = ks.msg_cursor
        orders = self._order_queue_repository.list(max_order_id, self.BATCH_SIZE)
        connector = KafkaConnector(ks.kafka_host, ks.kafka_port, ks.kafka_username,
                                   ks.kafka_password, ks.kafka_topic, self.kafka_certificate_path)

        self._log.info(f"{datetime.utcnow()}. Found {len(orders)} to dispatch.")
        student_kafka = KafkaClient(connector)

        for order in orders:
            msg = {
                "object_id": order.id,
                "object_type": "order",
                "sent_dttm": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
                "payload": json.loads(order.order_json)
            }

            self._log.info(f"{datetime.utcnow()}. Dispatching {json.dumps(msg)}.")

            student_kafka.send(msg)
            max_order_id = max(max_order_id, order.id)

        self._log.info(f"max_order_id: {max_order_id}.")
        self._kafka_settings_repository.release(ks.id, session, max_order_id)

        self._log.info("end dispatch session.")
