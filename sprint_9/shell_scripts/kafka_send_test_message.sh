curl -X POST https://order-gen-service.de.education-services.ru/test_kafka \
-H 'Content-Type: application/json; charset=utf-8' \
--data-binary @- << EOF
{
    "student": "goel52",
    "kafka_connect":{
        "host": "rc1a-dd82uurs138urmau.mdb.yandexcloud.net",
        "port": 9091,
        "topic": "stg",
        "producer_name": "user",
        "producer_password": "password"
    }
}
EOF



