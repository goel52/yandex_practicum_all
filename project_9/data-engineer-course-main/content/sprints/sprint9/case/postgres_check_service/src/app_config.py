import os

from pg_check_service import PgConnect


class AppConfig:
    CERTIFICATE_PATH = '/crt/YandexInternalRootCA.crt'

    def __init__(self) -> None:

        self.host = str(os.getenv('DB_CONTROLPLANE_HOST'))
        self.port = int(str(os.getenv('DB_CONTROLPLANE_PORT')))
        self.dbname = str(os.getenv('DB_CONTROLPLANE_DATABASE'))
        self.user = str(os.getenv('DB_CONTROLPLANE_USERNAME'))
        self.password = str(os.getenv('DB_CONTROLPLANE_PASSWORD'))

    def PgConnect(self):
        return PgConnect(self.host, self.port, self.dbname, self.user, self.password)
