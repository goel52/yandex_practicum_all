import logging

import pendulum
from airflow.decorators import dag, task
from airflow.models.variable import Variable

from config_const import ConfigConst
from couriers_loader import CouriersLoader
from delivery_api_connect import DeliveryApiConnect
from pg_connect import ConnectionBuilder

log = logging.getLogger(__name__)


class DeliveryLoader:
    def __init__(self, v1, v2) -> None:
        pass

    def run(self):
        pass


@dag(
    dag_id='sprint5_project_stg_delivery_system',
    schedule_interval='0/15 * * * *',
    start_date=pendulum.datetime(2022, 5, 5, tz="UTC"),
    catchup=False,
    tags=['sprint5', 'stg', 'origin'],
)
def sprint5_project_stg_delivery_system():
    dwh_pg_connect = ConnectionBuilder.pg_conn(ConfigConst.PG_WAREHOUSE_CONNECTION_CLOUD)

    da_host = Variable.get("DELIVERY_API_HOST")
    da_key = Variable.get("DELIVERY_API_KEY")
    da_nick = Variable.get("DELIVERY_API_NICKNAME")
    da_cohort = Variable.get("DELIVERY_API_COHORT")
    origin_api_connect = DeliveryApiConnect(da_host, da_key, da_nick, da_cohort, log)

    @task()
    def load_couriers():
        courier_loader = CouriersLoader(origin_api_connect, dwh_pg_connect)
        courier_loader.run()

    @task()
    def load_deliveries():
        delivery_loader = DeliveryLoader(origin_api_connect, dwh_pg_connect)
        delivery_loader.run()

    couriers = load_couriers()
    deliveries = load_deliveries()

    couriers  # type: ignore
    deliveries  # type: ignore


stg_delivery_dag = sprint5_project_stg_delivery_system()  # noqa
