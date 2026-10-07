


curl -X POST https://postgres-check-service.sprint9.tgcloudenv.ru/init_schemas \
-H 'Content-Type: application/json; charset=utf-8' \
--data-binary @- << EOF
{
  "student": "astarshev123",
  "pg_settings": {
    "host": "rc1b-gede6kucnd5jsob0.mdb.yandexcloud.net",
    "port": 6432,
    "dbname": "db",
    "username": "user",
    "password": "password"
  }
}
EOF