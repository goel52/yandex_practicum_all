import os
import random
from datetime import datetime, timedelta
from typing import Dict, List
from urllib.parse import quote_plus as quote

import requests
from bson.objectid import ObjectId
from faker import Faker
from pymongo.mongo_client import MongoClient


class MongoConnect:
    def __init__(self,
                 cert_path: str,
                 user: str,
                 pw: str,
                 hosts: List[str],
                 rs: str,
                 auth_db: str,
                 main_db: str
                 ) -> None:

        self.user = user
        self.pw = pw
        self.hosts = hosts
        self.replica_set = rs
        self.auth_db = auth_db
        self.main_db = main_db
        self.cert_path = cert_path

    def url(self) -> str:
        return 'mongodb://{user}:{pw}@{hosts}/?replicaSet={rs}&authSource={auth_src}'.format(
            user=quote(self.user),
            pw=quote(self.pw),
            hosts=','.join(self.hosts),
            rs=self.replica_set,
            auth_src=self.auth_db)

    def client(self):
        return MongoClient(self.url(), tlsCAFile=self.cert_path)[self.main_db]


class User:
    def __init__(self, id: ObjectId) -> None:
        self.id = id


class Restaurant:
    def __init__(self, id: ObjectId) -> None:
        self.id = id


class StatusLogRecord:
    def __init__(self, status_id: str, dt: datetime) -> None:
        self.status = status_id
        self.dttm = dt.strftime("%Y-%m-%d %H:%M:%S")


class OrderStatus:
    def __init__(self, id: int, key: str) -> None:
        self.id = id
        self.key = key

    def __str__(self) -> str:
        return f"{self.id};{self.key}"


class Product:
    def __init__(self, id, name, price) -> None:
        self.id = id
        self.name = name
        self.price = price

    def __str__(self) -> str:
        return f"{self.id};{self.name};{self.price}"


class OrderItem:
    def __init__(self, id, name: str, price: float, discount: float, quantity: int) -> None:
        self.id = id
        self.name = name
        self.price = price
        self.quantity = quantity


class Order:
    def __init__(self,
                 restaurant: Restaurant,
                 date: datetime,
                 user: User,
                 items: List[OrderItem],
                 bonus_payment: float,
                 bonus_grant: float,
                 status_list: List[StatusLogRecord],
                 final_status: str
                 ) -> None:
        self.restaurant = restaurant
        self.date = date.replace(microsecond=0)
        self.user = user
        self.order_items = items
        self.bonus_payment = bonus_payment
        self.cost = sum(i.price * i.quantity for i in items)
        self.payment = self.cost - self.bonus_payment
        self.bonus_grant = bonus_grant
        self.statuses = status_list
        self.final_status = final_status
        self.update_ts = datetime.utcnow().replace(microsecond=0)


def gen_status_log(order_date: datetime, final_status: str) -> List[StatusLogRecord]:
    st_open = "OPEN"
    st_cooking = "COOKING"
    st_delivering = "DELIVERING"
    st_closed = "CLOSED"
    st_cancelled = 'CANCELLED'

    def random_delta():
        return timedelta(minutes=random.randint(1, 59), seconds=random.randint(1, 59))

    order_status_log: List[StatusLogRecord] = []

    order_status = final_status
    if order_status == st_cancelled:
        order_status_log.append(StatusLogRecord(st_cancelled, order_date))
        order_status_log.append(StatusLogRecord(
            st_open, order_date - random_delta()))
    else:
        order_status_log.append(StatusLogRecord(st_closed, order_date))
        dt_delivering = order_date - random_delta()
        order_status_log.append(StatusLogRecord(st_delivering, dt_delivering))
        dt_cooking = dt_delivering - random_delta()
        order_status_log.append(StatusLogRecord(st_cooking, dt_cooking))
        dt_open = dt_cooking - random_delta()
        order_status_log.append(StatusLogRecord(st_open, dt_open))

    return order_status_log


class BonusPayment:
    def __init__(self, json) -> None:
        self.user_id = json['user_id']
        self.bonus_payment = json['bonus_payment']
        self.bonus_grant = json['bonus_grant']


def pay_bonus(url: str, auth_token: str, order: Order, id: ObjectId) -> BonusPayment:
    headers = {'Authorization': 'Bearer ' + auth_token}

    items = []
    for it in order.order_items:
        items.append({
            "id": str(it.id),
            "name": it.name,
            "price": it.price,
            "quantity": it.quantity
        })

    statuses = []
    for st in order.statuses:
        statuses.append({
            "status_key": st.status,
            "dttm": st.dttm
        })

    body_js = {
        "order_request": {
            "id": str(id),
            "user_id": str(order.user.id),
            "order_ts": order.date.strftime("%Y-%m-%d %H:%M:%S"),
            "cost": order.cost,
            "items": items,
            "status": order.final_status
        }
    }
    r = requests.post(url, json=body_js, headers=headers)
    print(r.json())
    payload = r.json()['event']['body']['bonus_payment_response']
    print(payload)
    return BonusPayment(payload)


def gen_orders(fake: Faker,
               restaurant: Restaurant,
               user: User,
               menu: List[Dict],
               count: int,
               max_items: int,
               max_item_count: int
               ) -> List[Order]:

    order_list: List[Order] = []

    st_closed = "CLOSED"
    st_cancelled = "CANCELLED"

    for _ in range(count):
        order_date = datetime.utcnow().replace(microsecond=0)
        # order_date = fake.past_datetime() # For initial bulk load

        items: List[OrderItem] = []
        for _ in range(random.randint(1, max_items)):
            prod = random.choice(menu)
            item = OrderItem(prod['_id'], prod['name'], prod['price'], 0, random.randint(1, max_item_count))

            existing_item = next((it for it in items if it.name == item.name), None)
            if existing_item:
                existing_item.quantity += item.quantity
            else:
                items.append(item)

        final_status = st_closed if random.randint(0, 99) > 10 else st_cancelled
        status_log = gen_status_log(order_date, final_status)
        order = Order(
            restaurant,
            order_date,
            user,
            items,
            0,
            0,
            status_log,
            final_status
        )

        order_list.append(order)

    return order_list


def to_dict(obj, classkey=None):
    if isinstance(obj, dict):
        data = {}
        for (k, v) in obj.items():
            data[k] = to_dict(v, classkey)
        return data
    elif hasattr(obj, "_ast"):
        return to_dict(obj._ast())
    elif hasattr(obj, "__iter__") and not isinstance(obj, str):
        return [to_dict(v, classkey) for v in obj]
    elif hasattr(obj, "__dict__"):
        data = dict([(key, to_dict(value, classkey))
                     for key, value in obj.__dict__.items()
                     if not callable(value) and not key.startswith('_')])
        if classkey is not None and hasattr(obj, "__class__"):
            data[classkey] = obj.__class__.__name__
        return data
    else:
        return obj


def run(mongo_connect: MongoConnect,
        collection_name: str,
        data_limit: datetime,
        orders_limit,
        bonus_url,
        bonus_auth_token):

    dbs = mongo_connect.client()

    existing = dbs.list_collection_names()
    if collection_name not in existing:
        dbs.create_collection(collection_name)

    del_res = dbs.get_collection(collection_name).delete_many({'date': {'$lt': data_limit}})
    print(f"deleted orders cnt: {del_res.deleted_count}")

    max_unique_items_per_order = 10
    max_count_of_item_in_order = 5

    restaurants = list(dbs.get_collection('restaurants').find())
    print(f"restaurants cnt: {len(restaurants)}")
    restaurant_json = random.choice(restaurants)
    restaurant = Restaurant(restaurant_json['_id'])
    menu = restaurant_json['menu']

    user_limit = dbs.get_collection('users').count_documents({})
    user_skip = random.randint(0, user_limit - 1)
    users = list(dbs.get_collection('users').find(filter={}, skip=user_skip, limit=1))
    print(f"users cnt: {len(users)}")
    user = User(random.choice(users)['_id'])

    fake = Faker('ru_RU')
    orders = gen_orders(fake, restaurant, user, menu, orders_limit,
                        max_unique_items_per_order, max_count_of_item_in_order)

    for order in orders:
        order_d = to_dict(order)
        result = dbs.get_collection(collection_name).insert_one(order_d)  # type: ignore
        bonus_transaction = pay_bonus(bonus_url, bonus_auth_token, order, result.inserted_id)
        filter = {'_id': result.inserted_id}
        update_values = {
            '$set': {
                'bonus_grant': bonus_transaction.bonus_grant,
                'bonus_payment': bonus_transaction.bonus_payment
            }
        }
        dbs.get_collection(collection_name).update_one(filter, update_values)

    cnt = dbs.get_collection(collection_name).count_documents({})

    return {
        'statusCode': 200,
        'body': {
            'deleted_cnt': del_res.deleted_count,
            'current_cnt': cnt
        },
    }


def handler(event, context):
    cert_path = str(os.getenv('MONGO_DB_CERTIFICATE_PATH'))

    db_user = str(os.getenv('MONGO_DB_USER'))
    db_pw = str(os.environ.get('MONGO_DB_PASSWORD'))
    rs = str(os.getenv('MONGO_DB_REPLICA_SET'))
    db = str(os.getenv('MONGO_DB_DATABASE_NAME'))
    hosts = str(os.getenv('MONGO_DB_HOSTS')).split(';')

    bonus_srv_url = str(os.getenv('BONUS_SERVICE_URL'))
    bonus_srv_token = context.token["access_token"]

    delete_threshold = datetime.utcnow() - timedelta(days=32)

    connector = MongoConnect(cert_path, db_user, db_pw, hosts, rs, db, db)
    return run(connector, 'orders', delete_threshold, 1, bonus_srv_url, bonus_srv_token)


# Для отладки.
if __name__ == '__main__':
    class Context:
        token = {}
    context = Context
    context.token["access_token"] = str(os.getenv('BONUS_SERVICE_TOKEN'))

    resp = handler(None, context)
    print(resp)
