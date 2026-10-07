from courier_repository import CouriersStgRepository
from delivery_api_connect import DeliveryApiConnect
from pg_connect import PgConnect
from settings_repository import EtlSettingsRepository


class CouriersLoader:
    WF_KEY = "delivery_couriers_origin_to_stg_workflow"
    LAST_LOADED_DT = "last_loaded_dt"

    def __init__(self, delivery_api: DeliveryApiConnect, dwh_connect: PgConnect) -> None:
        self.delivery_api = delivery_api
        self.courier_repository = CouriersStgRepository(dwh_connect)
        self.settings_repository = EtlSettingsRepository(dwh_connect)

    def run(self):
        couriers = []

        idx = 0
        has_items = True
        while has_items:
            page = self.delivery_api.get_couriers(idx)
            couriers.extend(page)
            has_items = len(page) > 0
            idx += 1

        self.courier_repository.insert_couriers(couriers)
