curl -X POST https://order-gen-service.de.education-services.ru/register_kafka \
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



docker run -d --rm -p 3000:3000 -p 15432:5432 --name=de-project-sprint-3-server cr.yandex/crp1r8pht0n0gl25aug1/project-sprint-3:latest


