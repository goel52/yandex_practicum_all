from datetime import datetime
from typing import List

from bson.objectid import ObjectId


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
        self.date = date
        self.user = user
        self.order_items = items
        self.bonus_payment = bonus_payment
        self.cost = sum(i.price * i.quantity for i in items)
        self.payment = self.cost - self.bonus_payment
        self.bonus_grant = bonus_grant
        self.statuses = status_list
        self.final_status = final_status
        self.update_ts = datetime.utcnow()
