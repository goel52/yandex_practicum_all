import redis

r = redis.StrictRedis(
    host="c-c9q0lnuqmed164aq3qev.rw.mdb.yandexcloud.net",
    port=6380,
    password="password",
    ssl=True,
    ssl_ca_certs="D:\yandex_pracktikum\sprint_9\YandexInternalRootCA.crt",
)

r.set("foo", "bar")
print(r.get("foo"))