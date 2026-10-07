import ast
import importlib
import inspect
from logging import Logger
from typing import Tuple

import stg_loader.stg_message_processor_job.stg_message_processor_job
from ast_tools.ast_visitors_custom import NodeQuery
from stg_loader_test_service.lib_mocks import (MockKafkaConsumer,
                                               MockKafkaProducer,
                                               MockRedisClient,
                                               MockStgRepository)

from .file_coordinator import FileCoordinator


class StgLoaderCheckService:
    def __init__(self, file_coordinator: FileCoordinator, log: Logger) -> None:
        self._lock = file_coordinator
        self._log = log.getChild("StgLoaderCheckService")

    MESSAGES = [
        {
            "in_msg": {
                "object_id": 326180,
                "object_type": "order",
                "sent_dttm": "2022-11-19 23:44:12",
                "payload": {
                    "restaurant": {"id": "626a81cfefa404208fe9abae"},
                    "date": "2022-11-19 23:44:12",
                    "user": {"id": "626a81ce9a8cd1920641e293"},
                    "order_items": [
                        {"id": "6276e8cd0cf48b4cded0086d", "name": "ГРИЛАТА С КУРИЦЕЙ И ОВОЩАМИ", "price": 60, "quantity": 6},
                        {"id": "6276e8cd0cf48b4cded00876", "name": "МИНИ ПИРОГ КИШ С КУРИЦЕЙ", "price": 120, "quantity": 3},
                        {"id": "6276e8cd0cf48b4cded0086e", "name": "РОЛЛ С ВЕТЧИНОЙ И ОМЛЕТОМ", "price": 120, "quantity": 4},
                        {"id": "6276e8cd0cf48b4cded0087d", "name": "СЭНДВИЧ НА КРУАССАНЕ КУРИЦА", "price": 180, "quantity": 4}
                    ],
                    "bonus_payment": 0,
                    "cost": 1920,
                    "payment": 1920,
                    "bonus_grant": 0,
                    "statuses": [
                        {"status": "CLOSED", "dttm": "2022-11-19 23:44:12"},
                        {"status": "DELIVERING", "dttm": "2022-11-19 23:40:22"},
                        {"status": "COOKING", "dttm": "2022-11-19 23:11:42"},
                        {"status": "OPEN", "dttm": "2022-11-19 22:16:41"}
                    ],
                    "final_status": "CLOSED",
                    "update_ts": "2022-11-19 23:44:12"
                }
            },
            "user": {
                '_id': '626a81ce9a8cd1920641e293',
                'name': 'Комиссарова Акулина Кузьминична',
                'login': 'ukononova',
                'update_ts_utc': '2022-10-17 13:34:32'
            },
            "restaurant": {
                '_id': '626a81cfefa404208fe9abae',
                'name': 'Кофейня №1',
                'menu': [
                    {
                        '_id': '6276e8cd0cf48b4cded0086d',
                        'name': 'ГРИЛАТА С КУРИЦЕЙ И ОВОЩАМИ',
                        'price': 60,
                        'category': 'Закуски'
                    },
                    {
                        '_id': '6276e8cd0cf48b4cded0086e',
                        'name': 'РОЛЛ С ВЕТЧИНОЙ И ОМЛЕТОМ',
                        'price': 120,
                        'category': 'Закуски'
                    },
                    {
                        '_id': '6276e8cd0cf48b4cded00876',
                        'name': 'МИНИ ПИРОГ КИШ С КУРИЦЕЙ',
                        'price': 120,
                        'category': 'Выпечка'
                    },
                    {
                        '_id': '6276e8cd0cf48b4cded0087d',
                        'name': 'СЭНДВИЧ НА КРУАССАНЕ КУРИЦА',
                        'price': 180,
                        'category': 'Выпечка'
                    },
                    {
                        '_id': '6276e8cd0cf48b4cded0087e',
                        'name': 'СЭНДВИЧ С ТУНЦОМ',
                        'price': 180,
                        'category': 'Выпечка'
                    }
                ],
                'update_ts_utc': '2022-10-19 21:30:33'
            },
            "out_msg": {
                "object_id": 326180,
                "object_type": "order",
                "payload": {
                    "id": 326180,
                    "date": "2022-11-19 23:44:12",
                    "cost": 1920,
                    "payment": 1920,
                    "status": "CLOSED",
                    "restaurant": {"id": "626a81cfefa404208fe9abae", "name": "Кофейня №1"},
                    "user": {"id": "626a81ce9a8cd1920641e293", "name": "Комиссарова Акулина Кузьминична"},
                    "products": [
                        {
                            "id": "6276e8cd0cf48b4cded0086d",
                            "price": 60,
                            "quantity": 6,
                            "name": "ГРИЛАТА С КУРИЦЕЙ И ОВОЩАМИ",
                            "category": "Закуски"
                        },
                        {
                            "id": "6276e8cd0cf48b4cded00876",
                            "price": 120,
                            "quantity": 3,
                            "name": "МИНИ ПИРОГ КИШ С КУРИЦЕЙ",
                            "category": "Выпечка"
                        },
                        {
                            "id": "6276e8cd0cf48b4cded0086e",
                            "price": 120,
                            "quantity": 4,
                            "name": "РОЛЛ С ВЕТЧИНОЙ И ОМЛЕТОМ",
                            "category": "Закуски"
                        },
                        {
                            "id": "6276e8cd0cf48b4cded0087d",
                            "price": 180,
                            "quantity": 4,
                            "name": "СЭНДВИЧ НА КРУАССАНЕ КУРИЦА",
                            "category": "Выпечка"
                        }
                    ]
                }
            }
        }
    ]

    def check_init(self, stg_loader_path: str, user_code: str) -> Tuple[bool, str]:
        job_path = f'{stg_loader_path}/stg_loader/stg_message_processor_job/stg_message_processor_job.py'
        auth_path = f'{stg_loader_path}/stg_loader/stg_message_processor_job/stg_message_processor_job_auth.py'

        if 'StgMessageProcessor' not in user_code:
            return (False, 'В вашем коде не найден класс StgMessageProcessor')

        with self._lock.session(job_path, user_code, auth_path) as _:

            importlib.reload(stg_loader.stg_message_processor_job.stg_message_processor_job)

            sg = inspect.signature(stg_loader.stg_message_processor_job.stg_message_processor_job.StgMessageProcessor.__init__)
            if len(sg.parameters) != 7:
                param_str = "self, consumer, producer, redis_client, stg_repository, batch_size, logger"
                return (False, f"У вас в __init__ {len(sg.parameters)} параметров, а должно быть 7: {param_str}")

            producer = MockKafkaProducer()
            consumer = MockKafkaConsumer()
            redis = MockRedisClient()
            pg = MockStgRepository()
            log = self._log.getChild("test_init")

            proc = stg_loader.stg_message_processor_job.stg_message_processor_job.StgMessageProcessor(
                consumer, producer, redis, pg, 100, log)

            if proc._consumer is None:
                return (False, 'Проверьте self._consumer')
            if proc._producer is None:
                return (False, 'Проверьте self._producer')
            if proc._redis is None:
                return (False, 'Проверьте self._redis')
            if proc._stg_repository is None:
                return (False, 'Проверьте self._stg_repository')

            return (True, "")

    def check_order_events_insert(self, stg_loader_path: str, user_code: str) -> Tuple[bool, str]:
        if 'StgRepository' not in user_code:
            return (False, 'В вашем коде не найден класс StgRepository')

        try:
            student_file_name = 'stg_repository.py'
            tree = NodeQuery(ast.parse(
                user_code,
                student_file_name,
                mode='exec'))

        except Exception as e:
            return (False,
                    'Ваш код нельзя исполнить,'
                    f' ошибка: {type(e)}.\n'
                    f'{str(e)}')

        constants = [ast.unparse(_) for _ in tree.node(ast.Constant).all if ast.unparse(_) != 'None']  # noqa
        try:
            student_solution = constants[0]
        except Exception:
            return (False,
                    'Не меняйте структуру прекода. '
                    'Исправьте решение.')
            
        set_parts = {
            'CONFLICT',
            'DO',
            'EXCLUDED',
            'INSERT',
            'INTO',
            'ON',
            'SET',
            'UPDATE',
            'VALUES',
            'object_id',
            'object_type',
            'order_events',
            'sent_dttm',
            'payload',
            'stg'
            }

        for part in set_parts:
            if not part.upper() in student_solution.upper():
                return (
                    False,
                    f"В конструкции запроса отсутствует `{part}`. Исправьте запрос.",  # noqa
                )

        return (True, "")

    def check_consume_empty(self):
        importlib.reload(stg_loader.stg_message_processor_job)

        producer = MockKafkaProducer()
        consumer = MockKafkaConsumer()
        redis = MockRedisClient()
        pg = MockStgRepository()
        log = self._log.getChild("test_consume_empty")

        proc = stg_loader.stg_message_processor_job.stg_message_processor_job.StgMessageProcessor(
            consumer, producer, redis, pg, 100, log)
        proc.run()

        assert consumer.consume_called == 1

    def check_full_cycle_single(self, stg_loader_path: str, user_code: str) -> Tuple[bool, str]:
        log = self._log.getChild("test_full_cycle_single")

        job_path = f'{stg_loader_path}/stg_loader/stg_message_processor_job/stg_message_processor_job.py'
        auth_path = f'{stg_loader_path}/stg_loader/stg_message_processor_job/stg_message_processor_job_auth.py'

        if 'StgMessageProcessor' not in user_code:
            return (False, 'В вашем коде не найден класс StgMessageProcessor')

        with self._lock.session(job_path, user_code, auth_path) as _:
            importlib.reload(stg_loader.stg_message_processor_job.stg_message_processor_job)

            producer = MockKafkaProducer()
            consumer = MockKafkaConsumer()
            redis = MockRedisClient()
            pg = MockStgRepository()

            redis.set(self.MESSAGES[0]["user"]["_id"], self.MESSAGES[0]["user"])
            redis.set(self.MESSAGES[0]["restaurant"]["_id"], self.MESSAGES[0]["restaurant"])

            consumer.add(self.MESSAGES[0]["in_msg"])

            proc = stg_loader.stg_message_processor_job.stg_message_processor_job.StgMessageProcessor(
                consumer, producer, redis, pg, 100, log)
            proc.run()

            if consumer.consume_called == 0:
                return (False, 'Вы не вычитали ни одного сообщения из топика')
            if consumer.consume_called == 1:
                return (False, 'Вы вычитали из топика только одно сообщение и остановились. Необходимо продолжать чтение, пока в топике есть сообщения, либо пока не достигнут limit обработки сообщений')  # noqa
            if consumer.consume_called > 2:
                return (False, 'В топике закончились сообщения, но вы продолжили вычитывать. Необходимо остановить попытки чтения,  если вы вычитали весь топик')  # noqa

            if len(producer.q) == 0:
                return (False, 'Вы не отправили выходное сообщение')
            if len(producer.q) > 1:
                return (False, f'Вы должны отправить одно выходное сообщение на одно входное. А вы отправили {len(producer.q)}')

            result = producer.q.pop()
            expected = self.MESSAGES[0]["out_msg"]

            if "object_id" not in result:
                return (False, 'Ваше выходное сообщение не содержит поля `object_id`')
            if not expected["object_id"] == result["object_id"]:
                return (False, 'Ваше выходное сообщение содержит некорректные данные в поле `object_id`')

            if "object_type" not in result:
                return (False, 'Ваше выходное сообщение не содержит поля `object_type`')
            if not expected["object_type"] == result["object_type"]:
                return (False, 'Ваше выходное сообщение содержит некорректные данные в поле `object_type`')

            if "payload" not in result:
                return (False, 'Ваше выходное сообщение не содержит поля `payload`')
            r_payload = result["payload"]
            e_payload = expected["payload"]

            if not e_payload["id"] == r_payload["id"]:
                return (False, 'Ваше выходное сообщение содержит некорректные данные в поле `id`')

            if not e_payload["date"] == r_payload["date"]:
                return (False, 'Ваше выходное сообщение содержит некорректные данные в поле `date`')

            if not e_payload["cost"] == r_payload["cost"]:
                return (False, 'Ваше выходное сообщение содержит некорректные данные в поле `cost`')

            if not e_payload["payment"] == r_payload["payment"]:
                return (False, 'Ваше выходное сообщение содержит некорректные данные в поле `payment`')

            if not e_payload["status"] == r_payload["status"]:
                return (False, 'Ваше выходное сообщение содержит некорректные данные в поле `status`')

            if not e_payload["restaurant"]["id"] == r_payload["restaurant"]["id"]:
                return (False, 'Ваше выходное сообщение содержит некорректные данные в поле `restaurant.id`')
            if not e_payload["restaurant"]["name"] == r_payload["restaurant"]["name"]:
                return (False, 'Ваше выходное сообщение содержит некорректные данные в поле `restaurant.name`')
            if not e_payload["user"]["id"] == r_payload["user"]["id"]:
                return (False, 'Ваше выходное сообщение содержит некорректные данные в поле `user.id`')
            if not e_payload["user"]["name"] == r_payload["user"]["name"]:
                return (False, 'Ваше выходное сообщение содержит некорректные данные в поле `user.name`')
            if not len(e_payload["products"]) == len(e_payload["products"]):
                return (False, 'Ваше выходное сообщение содержит некорректные данные в поле `products`')

            e_prods = e_payload["products"]
            e_prods.sort(key=lambda x: x["id"])
            r_prods = r_payload["products"]
            r_prods.sort(key=lambda x: x["id"])

            if len(r_prods) != len(e_prods):
                return (False, 'В вашем выходном сообщении должно быть столько же продуктов, сколько и во входном сообщении.')

            for i in range(len(r_prods)):
                if not r_prods[i]["id"] == e_prods[i]["id"]:
                    return (False, 'Ваше выходное сообщение содержит некорректные данные в поле `products.id`')
                if not r_prods[i]["price"] == e_prods[i]["price"]:
                    return (False, 'Ваше выходное сообщение содержит некорректные данные в поле `products.price`')
                if not r_prods[i]["quantity"] == e_prods[i]["quantity"]:
                    return (False, 'Ваше выходное сообщение содержит некорректные данные в поле `products.quantity`')
                if not r_prods[i]["name"] == e_prods[i]["name"]:
                    return (False, 'Ваше выходное сообщение содержит некорректные данные в поле `products.name`')
                if not r_prods[i]["category"] == e_prods[i]["category"]:
                    return (False, 'Ваше выходное сообщение содержит некорректные данные в поле `products.category`')

            return (True, "")
