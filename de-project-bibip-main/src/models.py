from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from pydantic import BaseModel
import json


class CarStatus(StrEnum):
    available = "available"
    reserve = "reserve"
    sold = "sold"
    delivery = "delivery"


class Car(BaseModel):
    vin: str
    model: int
    price: Decimal
    date_start: datetime
    status: CarStatus

    def index(self) -> str:
        return self.vin

    def json(self) -> str:
        return json.dumps({
            'vin': self.vin,
            'model': self.model,
            'price': str(self.price),
            'date_start': self.date_start.isoformat(),
            'status': self.status
        })


class Model(BaseModel):
    id: int
    name: str
    brand: str

    def index(self) -> str:
        return str(self.id)

    def json(self) -> str:
        return json.dumps({
            'id': self.id,
            'name': self.name,
            'brand': self.brand
        })


class Sale(BaseModel):
    sales_number: str
    car_vin: str
    sales_date: datetime
    cost: Decimal

    def index(self) -> str:
        return self.car_vin

    def json(self) -> str:
        return json.dumps({
            'sales_number': self.sales_number,
            'car_vin': self.car_vin,
            'sales_date': self.sales_date.isoformat(),
            'cost': str(self.cost)
        })


class CarFullInfo(BaseModel):
    vin: str
    car_model_name: str
    car_model_brand: str
    price: Decimal
    date_start: datetime
    status: CarStatus
    sales_date: datetime | None
    sales_cost: Decimal | None


class ModelSaleStats(BaseModel):
    car_model_name: str
    brand: str
    sales_number: int
