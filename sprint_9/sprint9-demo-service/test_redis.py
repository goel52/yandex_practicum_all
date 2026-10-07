import requests
import json

url = 'https://redis-data-service.sprint9.tgcloudenv.ru/test_redis'
headers = {'Content-Type': 'application/json'}
payload = json.dumps(
    {
    "redis": {
        "host": "c-c9qblc0jhgej30gl7kcb.rw.mdb.yandexcloud.net",
        "port": 6380,
        "password": "XXXXX"
        }
    }
)

response = requests.request('POST', url, headers=headers, data=payload)
print(response.text)