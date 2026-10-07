 docker run \
    -it \
    --network=host \
    -v "/Users/oleg/yandex_pracktikum/CA.pem:/data/CA.pem" \
    edenhill/kcat:1.7.1 -b rc1a-39in61ae96vcfc9b.mdb.yandexcloud.net:9091 \
   -X security.protocol=SASL_SSL \
    -X sasl.mechanisms=SCRAM-SHA-512 \
    -X sasl.username=producer_consumer \
    -X sasl.password="producer_consumer" \
    -X ssl.ca.location=/data/CA.pem \
    -t order-service_orders \
    -C \
    -o beginning


/usr/local/share/ca-certificates/Yandex/YandexInternalRootCA.crt


docker run \
    -it \
    --network=host \
    -v "/Users/oleg/yandex_pracktikum/kafka/CA.pem:/data/CA.pem" \
    edenhill/kcat:1.7.1 -b rc1a-sm2hjbo8lu9jlc5u.mdb.yandexcloud.net:9091 \
    -X security.protocol=SASL_SSL \
    -X sasl.mechanisms=SCRAM-SHA-512 \
    -X sasl.username=producer_consumer \
    -X sasl.password="ELL-BvR-tG3-rC5" \
    -X ssl.ca.location=/data/CA.pem \
    -L




curl -X POST https://order-gen-service.de.education-services.ru/test_kafka \
-H 'Content-Type: application/json; charset=utf-8' \
--data-binary @- << EOF
{
    "student": "ваш_логин",
    "kafka_connect":{
        "host": "ваш_хост_kafka",
        "port": 9091,
        "topic": "order-service_orders",
        "producer_name": "producer_consumer",
        "producer_password": "ваш_пароль"
    }
}
EOF