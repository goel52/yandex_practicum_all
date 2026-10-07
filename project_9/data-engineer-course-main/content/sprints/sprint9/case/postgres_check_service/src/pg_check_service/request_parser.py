from typing import Dict, Optional, Tuple
from pg_check_service import PgConnect


class RequestParser:
    STUDENT_KEY = 'student'
    PG_SETTINGS_KEY = 'pg_settings'

    def __init__(self, request: Dict) -> None:
        self.req = request

    def student(self) -> Tuple[Optional[str], Optional[str]]:
        if self.STUDENT_KEY not in self.req:
            return (None, f"No {self.STUDENT_KEY} found in request.")
        return (self.req[self.STUDENT_KEY], None)

    def pg_setting(self) -> Tuple[Optional[PgConnect], Optional[str]]:
        if self.PG_SETTINGS_KEY not in self.req:
            return (None, f"No {self.PG_SETTINGS_KEY} found in request.")

        json = self.req[self.PG_SETTINGS_KEY]

        host = 'host'
        port = 'port'
        db = 'dbname'
        user = 'username'
        password = 'password'

        if host not in json:
            return (None, f"No {host} found in {self.PG_SETTINGS_KEY}.")
        if port not in json:
            return (None, f"No {port} found in {self.PG_SETTINGS_KEY}.")
        if db not in json:
            return (None, f"No {db} found in {self.PG_SETTINGS_KEY}.")
        if user not in json:
            return (None, f"No {user} found in {self.PG_SETTINGS_KEY}.")
        if password not in json:
            return (None, f"No {password} found in {self.PG_SETTINGS_KEY}.")

        pg = PgConnect(json[host], json[port], json[db], json[user], json[password])
        return (pg, None)
