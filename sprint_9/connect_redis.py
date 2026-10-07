import redis



def main():
# указываем параметры, которые необходимы для подключения
    host = "c-c9q0lnuqmed164aq3qev.rw.mdb.yandexcloud.net"
    port = 6380
    password = "password"
    ca_path = "YandexInternalRootCA.crt"

# инициализируем клиент, с помощью которого будем подключаться к Redis
    client = redis.StrictRedis(
            host=host,
            port=port,
            password=password,
            ssl=True,
            ssl_ca_certs=ca_path)

# просто подключиться недостаточно, да и неинтересно: нужно же ещё и поработать с хранилищем

# запишем в Redis ключ here_is_the_key и соответствующее ему строковое значение string value
    client.set("here_is_the_key", "string value")

# получим значение ключа с помощью команды get
    result = client.get("here_is_the_key")
    print(result)

if __name__ == '__main__':
    main()