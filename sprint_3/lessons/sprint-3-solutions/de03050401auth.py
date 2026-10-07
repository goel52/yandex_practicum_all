# conn_s3
# Host: storage.yandexcloud.net
# Extra {"aws_access_key_id": "<YC_ACCESS_KEY_ID>", "aws_secret_access_key": "<YC_SECRET_ACCESS_KEY>"}
#
# https://cloud.yandex.ru/docs/storage/s3/?utm_source=console&utm_medium=side-bar-left&utm_campaign=storage
#
#   URL может иметь одну из следующих форм:

# https://storage.yandexcloud.net/<bucket>/<key>?<parameters>
# https://<bucket>.storage.yandexcloud.net/<key>?<parameters>
# Примечание

# Если вы используете AWS SDK для .NET, обращайтесь к хосту s3.yandexcloud.net.

# airflow connections add 'conn_s3' \
#     --conn-json '{
#         "conn_type": "HTTP",
#         "host": "storage.yandexcloud.net",
#         "extra": {
#             "aws_access_key_id": "<YC_ACCESS_KEY_ID>", "aws_secret_access_key": "<YC_SECRET_ACCESS_KEY>"
#         }
#     }'