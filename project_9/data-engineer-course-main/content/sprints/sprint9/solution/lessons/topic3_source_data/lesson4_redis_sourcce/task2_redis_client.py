
import redis


REDIS_HOST = "c-c9q737dl43ueouamgq57.rw.mdb.yandexcloud.net"
REDIS_PORT = 6380
REDIS_PASSWORD = "Sp9-Redis-Pass"


def main():
    # указываем параметры, которые необходимы для подключения
    host = REDIS_HOST
    port = REDIS_PORT
    password = REDIS_PASSWORD
    ca_path = "/usr/local/share/ca-certificates/Yandex/YandexInternalRootCA.crt"

# инициализируем клиент, с помощью которого будем подключаться к Redis
    client = redis.StrictRedis(
        host=host,
        port=port,
        password=password,
        ssl=True,
        ssl_ca_certs=ca_path)

# просто подключиться недостаточно, да и неинтересно: нужно же ещё и поработать с хранилищем

# получим значение ключа с помощью команды get
    result = client.get("a51e4e31ae4602047ec52534")
    if not result:
        print("No value found for the key")
        return

    result = result.decode("utf-8")
    print(result)


if __name__ == '__main__':
    main()
