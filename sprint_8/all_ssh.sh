

#из докера
 kafkacat -b rc1b-2erh7b35n4j4v869.mdb.yandexcloud.net:9091 -L \
-X security.protocol=SASL_SSL \
-X sasl.mechanisms=SCRAM-SHA-512 \
-X sasl.username="de-student" \
-X sasl.password="ltcneltyn"  \
-X ssl.ca.location=/usr/local/share/ca-certificates/Yandex/YandexCA.crt \
-t base \
-K \
-C \
-o beginning





#локально
docker run -it -v "D:/CA.pem:/data/CA.pem" \
 --network=host edenhill/kcat:1.7.1 \
 kcat -b rc1b-2erh7b35n4j4v869.mdb.yandexcloud.net:9091 -L \
-X security.protocol=SASL_SSL \
-X sasl.mechanisms=SCRAM-SHA-512 \
-X sasl.username="de-student" \
-X sasl.password="ltcneltyn" \
-X ssl.ca.location=/data/CA.pem \
-t base \
-K \
-C \
-o beginning





#винда

echo my_key:my_message | docker run -i -v "D:/CA.pem:/data/CA.pem" --network=host edenhill/kcat:1.7.1 kcat -b rc1b-2erh7b35n4j4v869.mdb.yandexcloud.net:9091 -L -X security.protocol=SASL_SSL -X sasl.mechanisms=SCRAM-SHA-512 -X sasl.username="de-student" -X sasl.password="ltcneltyn" -X ssl.ca.location=/data/CA.pem -t base -K: -P



docker run -it -v "D:/CA.pem:/data/CA.pem" --network=host edenhill/kcat:1.7.1 kcat -b rc1b-2erh7b35n4j4v869.mdb.yandexcloud.net:9091 -L -X security.protocol=SASL_SSL -X sasl.mechanisms=SCRAM-SHA-512 -X sasl.username="de-student" -X sasl.password="ltcneltyn" -X ssl.ca.location=/data/CA.pem -t base -K: -C -o beginning





docker run -it -v "/Users/oleg/yandex_pracktikum/sprint_8/CA.pem:/data/CA.pem" \
 --network=host edenhill/kcat:1.7.1 \
 kcat -b rc1a-2i69cqo64qtff1oh.mdb.yandexcloud.net:9091  -L \
-X security.protocol=SASL_SSL \
-X sasl.mechanisms=SCRAM-SHA-512 \
-X sasl.username="producer_consumer" \
-X sasl.password="alexvdO24tmppwd" \
-X ssl.ca.location=/data/CA.pem \
-t base \
-C \
-o beginning


kcat -C -b rc1a-pfsp28idh9gkneos.mdb.yandexcloud.net:9091 -X security.protocol=SASL_SSL -X sasl.mechanisms=SCRAM-SHA-512 -X sasl.username=producer_consumer -X sasl.password="***" -X ssl.ca.location=/home/user/ca-certificates/Yandex/YandexInternalRootCA.crt -t order-service_orders -o beginning -J
{"topic":"order-service_orders","partition":0,"offset":0,"tstype":"create","ts":1741894165567,"broker":1,"key":"key","payload":"test message"}



docker run -it -v "/Users/oleg/yandex_pracktikum/sprint_8/CA.pem:/data/CA.pem" \
 --network=host edenhill/kcat:1.7.1 \
 kcat -b rc1b-2erh7b35n4j4v869.mdb.yandexcloud.net:9091 -L \
-X security.protocol=SASL_SSL \
-X sasl.mechanisms=SCRAM-SHA-512 \
-X sasl.username="de-student" \
-X sasl.password="ltcneltyn" \
-X ssl.ca.location=/data/CA.pem \
-t base \
-K: \
-P
my_key:my_message


echo my_key:my_message | docker run -i -v "D:/CA.pem:/data/CA.pem" --network=host edenhill/kcat:1.7.1 kcat -b rc1b-2erh7b35n4j4v869.mdb.yandexcloud.net:9091 -L -X security.protocol=SASL_SSL -X sasl.mechanisms=SCRAM-SHA-512 -X sasl.username="de-student" -X sasl.password="ltcneltyn" -X ssl.ca.location=/data/CA.pem -t base -K: -P
docker run -it -v "D:/CA.pem:/data/CA.pem" --network=host edenhill/kcat:1.7.1 kcat -b rc1b-2erh7b35n4j4v869.mdb.yandexcloud.net:9091 -L -X security.protocol=SASL_SSL -X sasl.mechanisms=SCRAM-SHA-512 -X sasl.username="de-student" -X sasl.password="ltcneltyn" -X ssl.ca.location=/data/CA.pem -t base -K: -C -o beginning

kafkacat -b rc1b-2erh7b35n4j4v869.mdb.yandexcloud.net:9091 \
-X security.protocol=SASL_SSL \
-X sasl.mechanisms=SCRAM-SHA-512 \
-X sasl.username="ваш_username" \
-X sasl.password="ваш_пароль" \
-X ssl.ca.location=/data/CA.pem \
-t base \
-K: \
-P
my_key:my_message




producer_consumer



docker run -it -v "/Users/oleg/yandex_pracktikum/sprint_8/CA.pem:/data/CA.pem" \
 --network=host edenhill/kcat:1.7.1 \
 kcat -b rc1a-39in61ae96vcfc9b.mdb.yandexcloud.net:9091 -L \
-X security.protocol=SASL_SSL \
-X sasl.mechanisms=SCRAM-SHA-512 \
-X sasl.username="producer_consumer" \
-X sasl.password="producer_consumer" \
-X ssl.ca.location=/data/CA.pem \
-t order-service_orders \
-C \
-o beginning


docker run -it -v "/Users/oleg/yandex_pracktikum/sprint_8/CA.pem:/data/CA.pem" \
 --network=host edenhill/kcat:1.7.1 \
 kcat -b rc1a-39in61ae96vcfc9b.mdb.yandexcloud.net:9091 -L \
-X security.protocol=SASL_SSL \
-X sasl.mechanisms=SCRAM-SHA-512 \
-X sasl.username="producer_consumer" \
-X sasl.password="producer_consumer" \
-X ssl.ca.location=/data/CA.pem \
-t base \
-K: \
-P
my_key:my_message