curl -X POST https://valkey-data-service.de.education-services.ru/load_users \
-H 'Content-Type: application/json; charset=utf-8' \
--data-binary @- << EOF
{
    "valkey":{
        "host": "c-c9q0lnuqmed164aq3qev.rw.mdb.yandexcloud.net",
        "port": 6380,
        "password": "password"
    }
}
EOF

curl -X POST -H "Content-Type: application/json; charset=utf-8" -d "{\"redis\": {\"host\": \"c-c9q0lnuqmed164aq3qev.rw.mdb.yandexcloud.net\",\"port\": 6380, \"password\": \"password\"}}"  https://redis-data-service.sprint9.tgcloudenv.ru/test_redis


curl -X POST -H "Content-Type: application/json" -d "{\"student\":\"goel52\"}"  https://order-gen-service.sprint9.tgcloudenv.ru/delete_kafka




https://valkey-data-service.sprint9.tgcloudenv.ru/load_users


curl -X POST -H "Content-Type: application/json; charset=utf-8" -d "{\"redis\": {\"host\": \"c-c9q0lnuqmed164aq3qev.rw.mdb.yandexcloud.net\",\"port\": 6380, \"password\": \"password\"}}"  https://valkey-data-service.de.education-services.ru/load_users


curl -X POST https://valkey-data-service.de.education-services.ru/load_users -H 'Content-Type: application/json; charset=utf-8' --data-binary @- << EOF
{
    "valkey":{
        "host": "c-c9q0lnuqmed164aq3qev.rw.mdb.yandexcloud.net",
        "port": 6380,
        "password": "password"
    }
}
EOF
