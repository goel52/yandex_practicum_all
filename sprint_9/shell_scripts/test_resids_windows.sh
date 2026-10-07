curl -X POST -H 'Content-Type: application/json' -d "{\"redis\": {\"host\": \"c-c9q0lnuqmed164aq3qev.rw.mdb.yandexcloud.net\",\"port\": 6380, \"password\": \"password\"} }"  https://redis-data-service.sprint9.tgcloudenv.ru/test_redis




curl -X POST https://redis-data-service.sprint9.tgcloudenv.ru/test_redis \
-H 'Content-Type: application/json; charset=utf-8' \
--data-binary @- << EOF
{
    "redis":{
        "host": "c-a0d435qpoboucnpnbvnk.rw.mdb.yandexcloud.ru",
        "port": 6380,
        "password": "trret-5Vj-Wfp-1231276"
    }
}
EOF