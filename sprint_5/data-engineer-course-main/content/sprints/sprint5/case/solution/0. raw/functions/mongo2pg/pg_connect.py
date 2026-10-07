import psycopg


class PgConnect:
    def __init__(self, host: str, port: int, db_name: str, user: str, pw: str) -> None:
        self.host = host
        self.port = port
        self.db_name = db_name
        self.user = user
        self.pw = pw

    def url(self) -> str:
        return """
            host={host}
            port={port}
            dbname={db_name}
            user={user}
            password={pw}
            target_session_attrs=read-write
            sslmode=require
        """.format(
            host=self.host,
            port=self.port,
            db_name=self.db_name,
            user=self.user,
            pw=self.pw)

    def client(self):
        return psycopg.connect(self.url())
