import logging

from app_config import AppConfig
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask
from stg_loader.repository import Migrator, StgRepository
from stg_loader.stg_message_processor_job import StgMessageProcessor

app = Flask(__name__)

config = AppConfig()


@app.get('/health')
def hello_world():
    return 'healthy'


if __name__ == '__main__':
    app.logger.setLevel(logging.DEBUG)

    migrator = Migrator(config.pg_warehouse_db())
    migrator.up()

    proc = StgMessageProcessor(
        config.kafka_consumer(),
        config.kafka_producer(),
        config.redis_client(),
        StgRepository(config.pg_warehouse_db()),
        100,
        app.logger
    )

    scheduler = BackgroundScheduler()
    scheduler.add_job(func=proc.run, trigger="interval", seconds=25)
    scheduler.start()

    app.run(debug=True, host='0.0.0.0', use_reloader=False)

# Тесты через wellknown id пользователя с определенным профилем.
