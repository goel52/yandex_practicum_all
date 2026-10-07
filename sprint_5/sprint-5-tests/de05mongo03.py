# для тетсирования
### 1
# https://www.notion.so/praktikum/5-PostgreSQL-a9a441cafd4a454a8cf13912c728951c#1664bb83385f4988a6a607957d87a44a
# airflow connections add 'PG_WAREHOUSE_CONNECTION' \
#     --conn-json '{
#         "conn_type": "postgres",
#         "login": "jovyan",
#         "password": "jovyan",
#         "host": "localhost",
#         "port": 5432,
#         "schema": "de"
#     }'

# airflow connections add 'PG_ORIGIN_BONUS_SYSTEM_CONNECTION' \
#     --conn-json '{
#         "conn_type": "postgres",
#         "login": "student",
#         "password": "student1",
#         "host": "rc1a-1kn18k47wuzaks6h.mdb.yandexcloud.net",
#         "port": 6432,
#         "schema": "de-public",
#         "extra": {
#             "sslmode": "require"
#         }
#     }'
### 2
#  
# {
#     "MONGO_DB_CERTIFICATE_PATH": "/opt/airflow/certificates/PracticumSp5MongoDb.crt",
#     "MONGO_DB_DATABASE_NAME": "db-mongo",
#     "MONGO_DB_HOST": "rc1a-ba83ae33hvt4pokq.mdb.yandexcloud.net:27018",
#     "MONGO_DB_PASSWORD": "student1",
#     "MONGO_DB_REPLICA_SET": "rs01",
#     "MONGO_DB_USER": "student"
# }
#
### 3
# execte sql - /home/hugin/YxTmPr/sprint-5-tests/de05030702auth.sql

# Тема 4. Реализация DWH/6. Забираем данные из MongoDB/Задание 2
# de05040602 
# проверка таблиц ordersystem_orders ordersystem_restaurants ordersystem_users
# проверка аналогична 05030702