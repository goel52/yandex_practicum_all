import random
from datetime import datetime, timedelta
from typing import Dict, List

from faker import Faker
from order_gen.order_generation_job.mongo_client import MongoConnect
from order_gen.order_generation_job.order_generator.dict_util import DictUtil
from order_gen.order_generation_job.order_generator.order import (
    Order, OrderItem, Restaurant, StatusLogRecord, User)
from order_gen.repository import OrderQueueRepository


class OrderGenerator:
    def __init__(self,
                 order_queue_repository: OrderQueueRepository,
                 mongo_connect: MongoConnect
                 ) -> None:
        self._order_queue_repository = order_queue_repository
        self.rest_db = mongo_connect

    def gen_status_log(self, order_date: datetime, final_status: str) -> List[StatusLogRecord]:
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

    def new_orders(self,
                   fake: Faker,
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
            order_date = datetime.utcnow()
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
            status_log = self.gen_status_log(order_date, final_status)
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

    def gen_order(self) -> None:

        dbs = self.rest_db.client()

        max_unique_items_per_order = 5
        max_count_of_item_in_order = 5
        orders_limit = 1

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
        orders = self.new_orders(fake, restaurant, user, menu, orders_limit,
                                 max_unique_items_per_order, max_count_of_item_in_order)

        for order in orders:
            self._order_queue_repository.save(DictUtil.to_dict(order))
