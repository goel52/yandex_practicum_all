curl -X POST https://redis-data-service.sprint9.tgcloudenv.ru/load_users \
-H 'Content-Type: application/json; charset=utf-8' \
--data-binary @- << EOF
{
    "redis":{
        "host": "c-c9qaepo7cngvn5m2thue.rw.mdb.yandexcloud.net",
        "port": 6380,
        "password": "!"
    }
}
EOF


curl -X POST https://redis-data-service.sprint9.tgcloudenv.ru/test_redis -H 'Content-Type: application/json; charset=utf-8' --data-binary @- "redis":{"host": "c-c9qcemf84sfluseedt0j.rw.mdb.yandexcloud.net","port": 6380,"password": "Practicumde29_"}


curl -X POST https://redis-data-service.sprint9.tgcloudenv.ru/load_users -H "Content-Type: application/json; charset=utf-8" --data-binary "{\"redis\":{\"host\":\"c-c9qcemf84sfluseedt0j.rw.mdb.yandexcloud.net\",\"port\":6380,\"password\":\"Practicumde29_\"}}"