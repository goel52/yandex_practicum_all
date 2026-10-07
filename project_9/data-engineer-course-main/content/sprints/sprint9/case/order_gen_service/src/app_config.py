import os

from order_gen.order_generation_job.mongo_client import MongoConnect
from order_gen.repository.pg_connect import PgConnect


class AppConfig:
    CERTIFICATE_PATH = '/crt/YandexInternalRootCA.crt'

    def __init__(self) -> None:

        self.host = str(os.getenv('DB_CONTROLPLANE_HOST'))
        self.port = int(str(os.getenv('DB_CONTROLPLANE_PORT')))
        self.dbname = str(os.getenv('DB_CONTROLPLANE_DATABASE'))
        self.user = str(os.getenv('DB_CONTROLPLANE_USERNAME'))
        self.password = str(os.getenv('DB_CONTROLPLANE_PASSWORD'))

        self.rest_db_user = str(os.getenv('REST_DB_MONGO_USER'))
        self.rest_db_pw = str(os.getenv('REST_DB_MONGO_PASSWORD'))
        self.rest_db_host = str(os.getenv('REST_DB_MONGO_HOST'))
        self.rest_db_rs = str(os.getenv('REST_DB_MONGO_REPLICA_SET'))
        self.rest_db_auth_db = str(os.getenv('REST_DB_MONGO_AUTH_DB'))
        self.rest_db_main_db = str(os.getenv('REST_DB_MONGO_MAIN_DB'))

        self.trans_q_host = str(os.getenv('DB_TRANSACTION_QUEUE_HOST'))
        self.trans_q_port = int(str(os.getenv('DB_TRANSACTION_QUEUE_PORT')))
        self.trans_q_dbname = str(os.getenv('DB_TRANSACTION_QUEUE_DATABASE'))
        self.trans_q_user = str(os.getenv('DB_TRANSACTION_QUEUE_USERNAME'))
        self.trans_q_password = str(os.getenv('DB_TRANSACTION_QUEUE_PASSWORD'))

    def PgConnect(self):
        return PgConnect(self.host, self.port, self.dbname, self.user, self.password)

    def transaction_queue_pg_connect(self):
        return PgConnect(self.trans_q_host, self.trans_q_port, self.trans_q_dbname, self.trans_q_user, self.trans_q_password)

    def mongo_connect(self):
        return MongoConnect(
            self.CERTIFICATE_PATH,
            self.rest_db_user,
            self.rest_db_pw,
            [self.rest_db_host],
            self.rest_db_rs,
            self.rest_db_auth_db,
            self.rest_db_main_db
        )
