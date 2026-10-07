curl -X POST https://postgres-check-service.sprint9.tgcloudenv.ru/init_schemas \
-H 'Content-Type: application/json; charset=utf-8' \
--data-binary @- << EOF
{
  "student": "goel52",
  "pg_settings": {
    "host": "rc1b-o1z57nbcqtbgtcjn.mdb.yandexcloud.net",
    "port": 6432,
    "dbname": "sprint9dwh",
    "username": "db_user",
    "password": "password"
  }
}
EOF