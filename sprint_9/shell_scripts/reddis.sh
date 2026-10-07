curl -X POST https://redis-data-service.sprint9.tgcloudenv.ru/test_redis -H 'Content-Type: application/json; charset=utf-8' --data '{\"redis\":{\"host\": \"c-c9q0lnuqmed164aq3qev.rw.mdb.yandexcloud.net"\",\"port\": 6380,\"password\": \"Awesomegoal95!\"}}'

curl -X POST https://redis-data-service.sprint9.tgcloudenv.ru/test_redis \
-H 'Content-Type: application/json; charset=utf-8' \
--data-binary @- << EOF
{
    "redis":{
        "host": "c-c9q0lnuqmed164aq3qev.rw.mdb.yandexcloud.net",
        "port": 6380,
        "password": "Awesomegoal95!"
    }
}
EOF
