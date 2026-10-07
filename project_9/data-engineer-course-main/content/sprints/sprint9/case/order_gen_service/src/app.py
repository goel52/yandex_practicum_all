import logging
from typing import Dict

from app_config import AppConfig
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, request
from order_gen import (KafkaClient, KafkaConnector, KafkaSettingParser,
                       KafkaSettingsRepository)
from order_gen.order_generation_job import OrderDispatcher, OrderGenerator
from order_gen.repository.migration_runner import MigrationRunner
from order_gen.repository.order_queue_repository import OrderQueueRepository
from transaction_gen.repository import (MessageQueueRepository,
                                        TransactionDataMigrationRunner,
                                        TransactionMigrationRunner)
from transaction_gen.transaction_dispatcher import TransactionDispatcher

app = Flask(__name__)

config = AppConfig()


@app.get('/health')
def hello_world():
    return 'healthy'


@app.post('/register_kafka')
def register_kafka():
    try:
        req: Dict = request.get_json()  # type: ignore
    except Exception as e:
        app.logger.info(f"User request error: {e}")
        return {
            "response": {
                "status": "Error",
                "message": "Could not parse request as json."
            }
        }

    (ks, err) = KafkaSettingParser.parse_json(req)
    if ks is None:
        return {
            "response": {
                "status": "Error",
                "message": err
            }
        }

    test_obj = {
        "msg_key": "f32a438ea2f37cb7612e5b09",
        "status": "OK",
        "message": "This is test message. Checking that Kafka settings are correct."
    }

    try:
        kafka_client = KafkaConnector(ks.host,
                                      ks.port,
                                      ks.username,
                                      ks.userpass,
                                      ks.topic,
                                      config.CERTIFICATE_PATH)
        repository = KafkaClient(kafka_client)
        repository.send(test_obj)

    except Exception as e:
        app.logger.info(f"User request error: {e}")
        return {
            "response": {
                "status": "Error",
                "message": "Could not send test message to your Kafka. Settings are incorrect."
            }
        }

    repository = KafkaSettingsRepository(config.PgConnect())

    existing_sett = repository.get_for_student(ks.student)
    if existing_sett is not None:
        return {
            "response": {
                "status": "Error",
                "message": f"Kafka settings for sprint-9 for student {existing_sett.student_id} already exist."
            }
        }

    repository.save(ks.student, ks.host, ks.port, ks.username, ks.userpass, ks.topic)
    return {
        "response": {
            "status": "OK",
            "message": "Saved."
        }
    }


@app.post('/delete_kafka')
def delete_kafka():
    req: Dict = request.get_json()  # type: ignore

    student_key = req['student']
    if student_key is None:
        return {
            "error": 'student parameter is empty.'
        }

    repository = KafkaSettingsRepository(config.PgConnect())
    repository.delete(student_key)
    return {
        "response": {
            "status": "OK",
            "message": f"Kafka settings for sprint-9 for for student {student_key} has been deleted."
        }
    }


@app.post('/test_kafka')
def test_kafka():
    try:
        req: Dict = request.get_json()  # type: ignore
    except Exception as e:
        app.logger.info(f"User request error: {e}")
        return {
            "response": {
                "status": "Error",
                "message": "Could not parse request as json."
            }
        }

    (kafka_setting, err) = KafkaSettingParser.parse_json(req)
    if kafka_setting is None:
        return {
            "response": {
                "status": "Error",
                "message": err
            }
        }

    test_obj = {
        "msg_key": "01ec424a9b8b48c3e289a56d",
        "status": "OK"
    }

    try:
        kafka_client = KafkaConnector(kafka_setting.host,
                                      kafka_setting.port,
                                      kafka_setting.username,
                                      kafka_setting.userpass,
                                      kafka_setting.topic,
                                      config.CERTIFICATE_PATH)
        repository = KafkaClient(kafka_client)
        repository.send(test_obj)

    except Exception as e:
        app.logger.info(f"User request error: {e}")
        return {
            "response": {
                "status": "Error",
                "message": "Could not send test message to your Kafka. Settings are incorrect."
            }
        }

    return {
        "response": {
            "status": "OK",
            "message": "Test message sent to your Kafka. Check it."
        }
    }


@app.post('/project/register_kafka')
def project_register_kafka():
    try:
        req: Dict = request.get_json()  # type: ignore
    except Exception as e:
        app.logger.info(f"User request error: {e}")
        return {
            "response": {
                "status": "Error",
                "message": "Could not parse request as json."
            }
        }

    (ks, err) = KafkaSettingParser.parse_json(req)
    if ks is None:
        return {
            "response": {
                "status": "Error",
                "message": err
            }
        }

    test_obj = {
        "msg_key": "20a04725b049318234fc9cbd",
        "status": "OK",
        "message": "This is test message for final project. Checking that Kafka settings are correct."
    }

    try:
        kafka_client = KafkaConnector(ks.host,
                                      ks.port,
                                      ks.username,
                                      ks.userpass,
                                      ks.topic,
                                      config.CERTIFICATE_PATH)
        repository = KafkaClient(kafka_client)
        repository.send(test_obj)

    except Exception as e:
        app.logger.info(f"User request error: {e}")
        return {
            "response": {
                "status": "Error",
                "message": "Could not send test message to your Kafka. Settings are incorrect."
            }
        }

    repository = KafkaSettingsRepository(config.transaction_queue_pg_connect())

    existing_sett = repository.get_for_student(ks.student)
    if existing_sett is not None:
        return {
            "response": {
                "status": "Error",
                "message": f"Kafka settings for final project for for student {existing_sett.student_id} already exist."
            }
        }

    repository.save(ks.student, ks.host, ks.port, ks.username, ks.userpass, ks.topic)
    return {
        "response": {
            "status": "OK",
            "message": "Saved."
        }
    }


@app.post('/project/delete_kafka')
def project_delete_kafka():
    req: Dict = request.get_json()  # type: ignore

    student_key = req['student']
    if student_key is None:
        return {
            "error": 'student parameter is empty.'
        }

    repository = KafkaSettingsRepository(config.transaction_queue_pg_connect())
    repository.delete(student_key)
    return {
        "response": {
            "status": "OK",
            "message": f"Kafka settings for final project for for student {student_key} has been deleted."
        }
    }


@app.post('/project/test_kafka')
def project_test_kafka():
    try:
        req: Dict = request.get_json()  # type: ignore
    except Exception as e:
        app.logger.info(f"User request error: {e}")
        return {
            "response": {
                "status": "Error",
                "message": "Could not parse request as json."
            }
        }

    (kafka_setting, err) = KafkaSettingParser.parse_json(req)
    if kafka_setting is None:
        return {
            "response": {
                "status": "Error",
                "message": err
            }
        }

    test_obj = {
        "msg_key": "01ec424a9b8b48c3e289a56d",
        "status": "OK"
    }

    try:
        kafka_client = KafkaConnector(kafka_setting.host,
                                      kafka_setting.port,
                                      kafka_setting.username,
                                      kafka_setting.userpass,
                                      kafka_setting.topic,
                                      config.CERTIFICATE_PATH)
        repository = KafkaClient(kafka_client)
        repository.send(test_obj)

    except Exception as e:
        app.logger.info(f"User request error: {e}")
        return {
            "response": {
                "status": "Error",
                "message": "Could not send test message to your Kafka. Settings are incorrect."
            }
        }

    return {
        "response": {
            "status": "OK",
            "message": "Test message sent to your Kafka. Check it."
        }
    }


if __name__ == '__main__':
    app.logger.setLevel(logging.DEBUG)

    mr = MigrationRunner(config.PgConnect())
    mr.up()

    trans_mr = TransactionMigrationRunner(config.transaction_queue_pg_connect(), app.logger)
    trans_mr.up()

    ks_repository = KafkaSettingsRepository(config.PgConnect())
    q_repository = OrderQueueRepository(config.PgConnect())
    gen = OrderGenerator(q_repository, config.mongo_connect())
    order_dispatcher = OrderDispatcher(q_repository, ks_repository, config.CERTIFICATE_PATH, app.logger)

    order_scheduler = BackgroundScheduler()
    order_scheduler.add_job(func=gen.gen_order, trigger="interval", seconds=11)
    order_scheduler.add_job(func=order_dispatcher.dispatch_order, trigger="interval", seconds=20)
    order_scheduler.start()

    trans_kafka_settings = KafkaSettingsRepository(config.transaction_queue_pg_connect())
    trans_data_mr = TransactionDataMigrationRunner(config.transaction_queue_pg_connect(), app.logger)
    trans_msg_queue = MessageQueueRepository(config.transaction_queue_pg_connect())
    trans_dispatcher = TransactionDispatcher(trans_msg_queue, trans_kafka_settings, config.CERTIFICATE_PATH, app.logger)
    trans_scheduler = BackgroundScheduler()
    trans_scheduler.add_job(func=trans_dispatcher.dispatch, trigger="interval", seconds=21)
    trans_scheduler.add_job(func=trans_data_mr.run, trigger="interval", seconds=127)
    trans_scheduler.start()

    # Shut down the scheduler when exiting the app
    # atexit.register(lambda: scheduler.shutdown())

    app.run(host='0.0.0.0', use_reloader=False)
