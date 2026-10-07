curl -X POST https://redis-data-service.sprint9.tgcloudenv.ru/load_users \
-H 'Content-Type: application/json; charset=utf-8' \
--data-binary @- << EOF
{
    "redis":{
        "host": "hostname.rw.mdb.yandexcloud.net",
        "port": 6380,
        "password": "pass$$password"
    }
}
EOF