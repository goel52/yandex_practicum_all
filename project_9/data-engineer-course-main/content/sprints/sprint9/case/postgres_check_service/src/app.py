import logging
from typing import Dict, Optional, Tuple

from app_config import AppConfig
from flask import Flask, request
from pg_check_service import PgService, RequestParser
from pg_check_service.pg_service import ColumnDefinition, ForeignKeyConstraint
from repository import LockRepository, MigrationRunner, PgLogging
from stg_loader_test_service import FileCoordinator, StgLoaderCheckService
from ast_tools.ast_visitors_custom import NodeQuery


app = Flask(__name__)

config = AppConfig()


@app.get('/health')
def hello_world():
    return 'healthy'


def error(message: str) -> Dict:
    return {
        "response": {
            "status": "Error",
            "payload": {
                "message": message
            }
        }
    }


def ok(message: Dict) -> Dict:
    return {
        "response": {
            "status": "OK",
            "payload": message
        }
    }


def pg_service() -> Tuple[Optional[PgService], Optional[str]]:
    try:
        req: Dict = request.get_json()  # type: ignore
    except Exception:
        return (None, "Тело запроса не получается преобразовать в JSON.")

    parser = RequestParser(req)

    (student, err) = parser.student()
    if not student:
        return (None, err)

    (pg_client, err) = parser.pg_setting()
    if not pg_client:
        return (None, err)

    pg = PgService(pg_client, student)
    if not pg.ping():
        return (None, "База данных недоступна, либо были переданы некорректные параметры подключения.")

    return (pg, None)


@app.post('/init_schemas')
def init_schemas():
    pg, err_msg = pg_service()
    if not pg:
        return error(err_msg or "Cannot create PG Client.")
    with PgLogging.query_log(config.PgConnect(), pg._student, "init_schemas", request.get_json()):
        resp = pg.init_schemas()
    return ok(resp)


# Задание 1 - Создание схемы cdm
@app.post('/de09050201_check_schema_cdm')
def check_schema_cdm():
    pg, err_msg = pg_service()
    if not pg:
        return error(err_msg or "Cannot create PG Client.")

    with PgLogging.query_log(config.PgConnect(), pg._student, "de09050201_check_schema_cdm", request.get_json()):
        resp = pg.check_schema_cdm()

    return ok(resp)


# Задание 2 - Создание таблицы user_product_counters в схеме cdm
# https://www.notion.so/praktikum/2-513fe27eca3f4f13b33d4e1d20c474cb#f2a1e944575a4be088230cc3d39cbb5d
@app.post('/de09050202_check_user_product_counters')
def check_user_product_counters():
    pg, err_msg = pg_service()
    if not pg:
        return error(err_msg or "Cannot create PG Client.")

    with PgLogging.query_log(config.PgConnect(), pg._student, "de09050202_check_user_product_counters", request.get_json()):
        table_name = 'user_product_counters'
        table_schema = 'cdm'

        auth_column = [
            ColumnDefinition(column_name='id', data_type='integer', is_nullable='NO'),
            ColumnDefinition(column_name='order_cnt', data_type='integer', is_nullable='NO'),
            ColumnDefinition(column_name='product_id', data_type='uuid', is_nullable='NO'),
            ColumnDefinition(column_name='product_name', data_type='character varying', is_nullable='NO'),
            ColumnDefinition(column_name='user_id', data_type='uuid', is_nullable='NO')
        ]

        auth_indexes = {
            'user_product_counters_pkey': 'CREATE UNIQUE INDEX user_product_counters_pkey ON cdm.user_product_counters  USING btree (id)',
            'idx_user_product_counters__user_id_product_id': 'CREATE UNIQUE INDEX   idx_user_product_counters__user_id_product_id ON cdm.user_product_counters USING btree (user_id, product_id)',
        }

        result_key = "9qZh4l*Fog#RKB9UZn"
        tup = "Первая витрина создана. На очереди еще одна."

        resp = pg.check_table_and_index(
            table_name,
            table_schema,
            auth_column,
            auth_indexes,
            result_key,
            tup
        )

    return ok(resp)


# Задание 3 - Создание таблицы user_category_counters в схеме cdm
@app.post('/de09050203_check_user_category_counters')
def check_user_category_counters():
    pg, err_msg = pg_service()
    if not pg:
        return error(err_msg or "Cannot create PG Client.")

    with PgLogging.query_log(config.PgConnect(), pg._student, "de09050203_check_user_category_counters", request.get_json()):
        table_name = 'user_category_counters'
        table_schema = 'cdm'

        auth_column = [
            ColumnDefinition(column_name='id', data_type='integer', is_nullable='NO'),
            ColumnDefinition(column_name='order_cnt', data_type='integer', is_nullable='NO'),
            ColumnDefinition(column_name='category_id', data_type='uuid', is_nullable='NO'),
            ColumnDefinition(column_name='category_name', data_type='character varying', is_nullable='NO'),
            ColumnDefinition(column_name='user_id', data_type='uuid', is_nullable='NO'),
        ]

        auth_indexes = {
            'user_category_counters_pkey': 'CREATE UNIQUE INDEX user_category_counters_pkey ON cdm.user_category_counters   USING btree (id)',
            'idx_user_category_counters__user_id_category_id': 'CREATE UNIQUE INDEX     idx_user_category_counters__user_id_category_id ON cdm.user_category_counters USING btree (user_id,     category_id)',
        }

        result_key = "Zv49c755YQflmKIEDC"
        tup = "Вторая витрина создана. Считаем проектирование слоя витрин законченным."

        resp = pg.check_table_and_index(
            table_name,
            table_schema,
            auth_column,
            auth_indexes,
            result_key,
            tup
        )

    return ok(resp)


# Задание 4 - Создание order_events в схеме stg
@app.post('/de09050204_check_order_events')
def check_order_events():
    pg, err_msg = pg_service()
    if not pg:
        return error(err_msg or "Cannot create PG Client.")

    with PgLogging.query_log(config.PgConnect(), pg._student, "de09050204_check_order_events", request.get_json()):
        table_name = 'order_events'
        table_schema = 'stg'

        auth_column = [
            ColumnDefinition(column_name='id', data_type='integer', is_nullable='NO'),
            ColumnDefinition(column_name='object_id', data_type='integer', is_nullable='NO'),
            ColumnDefinition(column_name='object_type', data_type='character varying', is_nullable='NO'),
            ColumnDefinition(column_name='sent_dttm', data_type='timestamp without time zone', is_nullable='NO'),
            ColumnDefinition(column_name='payload', data_type='json', is_nullable='NO'),
        ]

        auth_indexes = {
            'order_events_pkey': 'CREATE UNIQUE INDEX order_events_pkey ON stg.order_events USING btree (id)',
            'order_events_object_id_key': 'CREATE UNIQUE INDEX order_events_object_id_key ON stg.order_events USING btree   (object_id)',
        }

        result_key = "zMS873hH7%6OFkXHJ5"
        tup = "Слой stg готов. Всего одна таблица. ИЗИ-катка."

        resp = pg.check_table_and_index(
            table_name,
            table_schema,
            auth_column,
            auth_indexes,
            result_key,
            tup
        )

    return ok(resp)


# Задание 5 - Создание таблицы h_users в схеме dds
@app.post('/de09050205_check_h_users')
def check_h_users():
    pg, err_msg = pg_service()
    if not pg:
        return error(err_msg or "Cannot create PG Client.")

    with PgLogging.query_log(config.PgConnect(), pg._student, "de09050205_check_h_users", request.get_json()):
        table_name = 'h_user'
        table_schema = 'dds'

        auth_column = [
            ColumnDefinition(column_name='h_user_pk', data_type='uuid', is_nullable='NO'),
            ColumnDefinition(column_name='user_id', data_type='character varying', is_nullable='NO'),
            ColumnDefinition(column_name='load_dt', data_type='timestamp without time zone', is_nullable='NO'),
            ColumnDefinition(column_name='load_src', data_type='character varying', is_nullable='NO'),
        ]

        auth_indexes = {
            'h_user_pkey': 'CREATE UNIQUE INDEX h_user_pkey ON dds.h_user USING btree (h_user_pk)',
        }

        result_key = "Rd83HQkR@@W1Jqg~#d"
        tup = "Таблица-хаб для сохранения пользователей готова. Впереди еще много работы."

        resp = pg.check_table_and_index(
            table_name,
            table_schema,
            auth_column,
            auth_indexes,
            result_key,
            tup
        )

    return ok(resp)


# Задание 6 - Создание таблицы h_product в схеме dds
@app.post('/de09050206_check_h_product')
def check_h_product():
    pg, err_msg = pg_service()
    if not pg:
        return error(err_msg or "Cannot create PG Client.")

    with PgLogging.query_log(config.PgConnect(), pg._student, "de09050206_check_h_product", request.get_json()):
        table_name = 'h_product'
        table_schema = 'dds'

        auth_column = [
            ColumnDefinition(column_name='h_product_pk', data_type='uuid', is_nullable='NO'),
            ColumnDefinition(column_name='product_id', data_type='character varying', is_nullable='NO'),
            ColumnDefinition(column_name='load_dt', data_type='timestamp without time zone', is_nullable='NO'),
            ColumnDefinition(column_name='load_src', data_type='character varying', is_nullable='NO'),
        ]

        auth_indexes = {
            'h_product_pkey': 'CREATE UNIQUE INDEX h_product_pkey ON dds.h_product USING btree (h_product_pk)',
        }

        result_key = "tK9TN8dFjXO8T2gI8w"
        tup = "Таблица-хаб для сохранения продуктов готова. Впереди еще много работы."

        resp = pg.check_table_and_index(
            table_name,
            table_schema,
            auth_column,
            auth_indexes,
            result_key,
            tup
        )

    return ok(resp)


# Задание 7 - Создание таблицы h_category в схеме dds
@app.post('/de09050207_check_h_category')
def check_h_category():
    pg, err_msg = pg_service()
    if not pg:
        return error(err_msg or "Cannot create PG Client.")

    with PgLogging.query_log(config.PgConnect(), pg._student, "de09050207_check_h_category", request.get_json()):
        table_name = 'h_category'
        table_schema = 'dds'

        auth_column = [
            ColumnDefinition(column_name='h_category_pk', data_type='uuid', is_nullable='NO'),
            ColumnDefinition(column_name='category_name', data_type='character varying', is_nullable='NO'),
            ColumnDefinition(column_name='load_dt', data_type='timestamp without time zone', is_nullable='NO'),
            ColumnDefinition(column_name='load_src', data_type='character varying', is_nullable='NO'),
        ]

        auth_indexes = {
            'h_category_pkey': 'CREATE UNIQUE INDEX h_category_pkey ON dds.h_category USING btree (h_category_pk)',
        }

        result_key = "kocZgmyS~IKUVO@5d$"
        tup = "У категории id в принципе нет — только name. Поэтому name используется в качестве id и есть в хабе. \
Таблица-хаб для сохранения категорий готова."

        resp = pg.check_table_and_index(
            table_name,
            table_schema,
            auth_column,
            auth_indexes,
            result_key,
            tup
        )

    return ok(resp)


# Задание 8 - Создание таблицы h_restaurant в схеме dds
@app.post('/de09050208_check_h_restaurant')
def check_h_restaurant():
    pg, err_msg = pg_service()
    if not pg:
        return error(err_msg or "Cannot create PG Client.")

    with PgLogging.query_log(config.PgConnect(), pg._student, "de09050208_check_h_restaurant", request.get_json()):
        table_name = 'h_restaurant'
        table_schema = 'dds'

        auth_column = [
            ColumnDefinition(column_name='h_restaurant_pk', data_type='uuid', is_nullable='NO'),
            ColumnDefinition(column_name='restaurant_id', data_type='character varying', is_nullable='NO'),
            ColumnDefinition(column_name='load_dt', data_type='timestamp without time zone', is_nullable='NO'),
            ColumnDefinition(column_name='load_src', data_type='character varying', is_nullable='NO'),
        ]

        auth_indexes = {
            'h_restaurant_pkey': 'CREATE UNIQUE INDEX h_restaurant_pkey ON dds.h_restaurant USING btree (h_restaurant_pk)   ',
        }

        result_key = "Y8GZJa~bCW%I1e8uZ*"
        tup = "Таблица-хаб для сохранения ресторанов готова. Впереди всё ещё много работы."

        resp = pg.check_table_and_index(
            table_name,
            table_schema,
            auth_column,
            auth_indexes,
            result_key,
            tup
        )

    return ok(resp)


# Задание 9 - Создание таблицы h_order в схеме dds
@app.post('/de09050209_check_h_order')
def check_h_order():
    pg, err_msg = pg_service()
    if not pg:
        return error(err_msg or "Cannot create PG Client.")

    with PgLogging.query_log(config.PgConnect(), pg._student, "de09050209_check_h_order", request.get_json()):
        table_name = 'h_order'
        table_schema = 'dds'

        auth_column = [
            ColumnDefinition(column_name='h_order_pk', data_type='uuid', is_nullable='NO'),
            ColumnDefinition(column_name='order_id', data_type='integer', is_nullable='NO'),
            ColumnDefinition(column_name='order_dt', data_type='timestamp without time zone', is_nullable='NO'),
            ColumnDefinition(column_name='load_dt', data_type='timestamp without time zone', is_nullable='NO'),
            ColumnDefinition(column_name='load_src', data_type='character varying', is_nullable='NO'),
        ]

        auth_indexes = {
            'h_order_pkey': 'CREATE UNIQUE INDEX h_order_pkey ON dds.h_order USING btree (h_order_pk)',
        }

        result_key = "D4n6Hx~trJ3}BxMfId"
        tup = "Таблица-хаб для сохранения заказов готова. На этом завершаем работу над хабами."

        resp = pg.check_table_and_index(
            table_name,
            table_schema,
            auth_column,
            auth_indexes,
            result_key,
            tup
        )

    return ok(resp)


# Задание 10 - Создание таблицы l_order_product в схеме dds
@app.post('/de09050210_check_l_order_product')
def check_l_order_product():
    pg, err_msg = pg_service()
    if not pg:
        return error(err_msg or "Cannot create PG Client.")

    with PgLogging.query_log(config.PgConnect(), pg._student, "de09050210_check_l_order_product", request.get_json()):
        table_name = 'l_order_product'
        table_schema = 'dds'

        auth_column = [
            ColumnDefinition(column_name='hk_order_product_pk', data_type='uuid', is_nullable='NO'),
            ColumnDefinition(column_name='h_order_pk', data_type='uuid', is_nullable='NO'),
            ColumnDefinition(column_name='h_product_pk', data_type='uuid', is_nullable='NO'),
            ColumnDefinition(column_name='load_dt', data_type='timestamp without time zone', is_nullable='NO'),
            ColumnDefinition(column_name='load_src', data_type='character varying', is_nullable='NO'),
        ]

        auth_indexes = {
            'l_order_product_pkey': 'CREATE UNIQUE INDEX l_order_product_pkey ON dds.l_order_product USING btree    (hk_order_product_pk)',  # noqa
        }

        auth_foreign_keys = [
            ForeignKeyConstraint(
                table_schema='dds',
                table_name=table_name,
                column_name='h_order_pk',
                foreign_table_schema='dds',
                foreign_table_name='h_order',
                foreign_column_name='h_order_pk'
            ),
            ForeignKeyConstraint(
                table_schema='dds',
                table_name=table_name,
                column_name='h_product_pk',
                foreign_table_schema='dds',
                foreign_table_name='h_product',
                foreign_column_name='h_product_pk'
            )
        ]

        result_key = "94pB@s5Q$D7b#7NInN"
        tup = "Таблица-линк для сохранения связи между заказами и продуктами. Работаем дальше!"

        resp = pg.check_table_and_index(
            table_name,
            table_schema,
            auth_column,
            auth_indexes,
            result_key,
            tup,
            auth_foreign_keys
        )

    return ok(resp)


# Задание 11 - Создание таблицы l_product_restaurant в схеме dds, которая связывает ресторан и продукт
@app.post('/de09050211_check_l_product_restaurant')
def check_l_product_restaurant():
    pg, err_msg = pg_service()
    if not pg:
        return error(err_msg or "Cannot create PG Client.")

    with PgLogging.query_log(config.PgConnect(), pg._student, "de09050211_check_l_product_restaurant", request.get_json()):
        table_name = 'l_product_restaurant'
        table_schema = 'dds'

        auth_column = [
            ColumnDefinition(column_name='hk_product_restaurant_pk', data_type='uuid', is_nullable='NO'),
            ColumnDefinition(column_name='h_restaurant_pk', data_type='uuid', is_nullable='NO'),
            ColumnDefinition(column_name='h_product_pk', data_type='uuid', is_nullable='NO'),
            ColumnDefinition(column_name='load_dt', data_type='timestamp without time zone', is_nullable='NO'),
            ColumnDefinition(column_name='load_src', data_type='character varying', is_nullable='NO'),
        ]

        auth_foreign_keys = [
            ForeignKeyConstraint(
                table_schema='dds',
                table_name=table_name,
                column_name='h_restaurant_pk',
                foreign_table_schema='dds',
                foreign_table_name='h_restaurant',
                foreign_column_name='h_restaurant_pk'
            ),
            ForeignKeyConstraint(
                table_schema='dds',
                table_name=table_name,
                column_name='h_product_pk',
                foreign_table_schema='dds',
                foreign_table_name='h_product',
                foreign_column_name='h_product_pk'
            )
        ]

        auth_indexes = {
            'l_product_restaurant_pkey': 'CREATE UNIQUE INDEX l_product_restaurant_pkey ON dds.l_product_restaurant USING   btree (hk_product_restaurant_pk)',  # noqa
        }

        result_key = "IGYRGnXAYpxO$QzxrP"
        tup = "Таблица-линк для сохранения связи между ресторанами и продуктами. Работаем дальше!"

        resp = pg.check_table_and_index(
            table_name,
            table_schema,
            auth_column,
            auth_indexes,
            result_key,
            tup,
            auth_foreign_keys
        )

    return ok(resp)


# Задание 12 - Создание таблицы l_product_category в схеме dds, которая связывает категорию и продукт
@app.post('/de09050212_check_l_product_category')
def check_l_product_category():
    pg, err_msg = pg_service()
    if not pg:
        return error(err_msg or "Cannot create PG Client.")

    with PgLogging.query_log(config.PgConnect(), pg._student, "de09050212_check_l_product_category", request.get_json()):
        table_name = 'l_product_category'
        table_schema = 'dds'

        auth_column = [
            ColumnDefinition(column_name='hk_product_category_pk', data_type='uuid', is_nullable='NO'),
            ColumnDefinition(column_name='h_category_pk', data_type='uuid', is_nullable='NO'),
            ColumnDefinition(column_name='h_product_pk', data_type='uuid', is_nullable='NO'),
            ColumnDefinition(column_name='load_dt', data_type='timestamp without time zone', is_nullable='NO'),
            ColumnDefinition(column_name='load_src', data_type='character varying', is_nullable='NO'),
        ]

        auth_indexes = {
            'l_product_category_pkey': 'CREATE UNIQUE INDEX l_product_category_pkey ON dds.l_product_category USING btree   (hk_product_category_pk)',  # noqa
        }

        auth_foreign_keys = [
            ForeignKeyConstraint(
                table_schema='dds',
                table_name=table_name,
                column_name='h_category_pk',
                foreign_table_schema='dds',
                foreign_table_name='h_category',
                foreign_column_name='h_category_pk'
            ),
            ForeignKeyConstraint(
                table_schema='dds',
                table_name=table_name,
                column_name='h_product_pk',
                foreign_table_schema='dds',
                foreign_table_name='h_product',
                foreign_column_name='h_product_pk'
            )
        ]

        result_key = "T%Gk0X{DZAXKEP4GRc"
        tup = "Таблица-линк для сохранения связи между категориями и продуктами. Работаем дальше!"

        resp = pg.check_table_and_index(
            table_name,
            table_schema,
            auth_column,
            auth_indexes,
            result_key,
            tup,
            auth_foreign_keys
        )

    return ok(resp)


# Задание 13 - Создание таблицы l_order_user в схеме dds, которая связывает заказ и пользователя
@app.post('/de09050213_check_l_order_user')
def check_l_order_user():
    pg, err_msg = pg_service()
    if not pg:
        return error(err_msg or "Cannot create PG Client.")

    with PgLogging.query_log(config.PgConnect(), pg._student, "de09050213_check_l_order_user", request.get_json()):
        table_name = 'l_order_user'
        dds_schema = 'dds'

        auth_column = [
            ColumnDefinition(column_name='hk_order_user_pk', data_type='uuid', is_nullable='NO'),
            ColumnDefinition(column_name='h_order_pk', data_type='uuid', is_nullable='NO'),
            ColumnDefinition(column_name='h_user_pk', data_type='uuid', is_nullable='NO'),
            ColumnDefinition(column_name='load_dt', data_type='timestamp without time zone', is_nullable='NO'),
            ColumnDefinition(column_name='load_src', data_type='character varying', is_nullable='NO'),
        ]

        auth_indexes = {
            'l_order_user_pkey': 'CREATE UNIQUE INDEX l_order_user_pkey ON dds.l_order_user USING btree (hk_order_user_pk)  ',
        }

        auth_foreign_keys = [
            ForeignKeyConstraint(
                table_schema=dds_schema,
                table_name=table_name,
                column_name='h_order_pk',
                foreign_table_schema=dds_schema,
                foreign_table_name='h_order',
                foreign_column_name='h_order_pk'
            ),
            ForeignKeyConstraint(
                table_schema=dds_schema,
                table_name=table_name,
                column_name='h_user_pk',
                foreign_table_schema=dds_schema,
                foreign_table_name='h_user',
                foreign_column_name='h_user_pk'
            )
        ]

        result_key = "KhiG}c4xwmvAms~CLF"
        tup = "Таблица-линк для сохранения связи между заказам и пользователями. Переходим к сателлитам!"

        resp = pg.check_table_and_index(
            table_name,
            dds_schema,
            auth_column,
            auth_indexes,
            result_key,
            tup,
            auth_foreign_keys
        )

    return ok(resp)


# Задание 14 - Создание таблицы s_user_names в схеме dds, которая содержит информацию о пользователе
# https://www.notion.so/praktikum/2-9316106063d04e6fb1222111df9427ba#82ad29c7331341d1a4f7a03d53ac48be
@app.post('/de09050214_check_s_user_names')
def check_s_user_names():
    pg, err_msg = pg_service()
    if not pg:
        return error(err_msg or "Cannot create PG Client.")

    with PgLogging.query_log(config.PgConnect(), pg._student, "de09050214_check_s_user_names", request.get_json()):
        table_name = 's_user_names'
        table_schema = 'dds'

        auth_column = [
            ColumnDefinition(column_name='h_user_pk', data_type='uuid', is_nullable='NO'),
            ColumnDefinition(column_name='username', data_type='character varying', is_nullable='NO'),
            ColumnDefinition(column_name='userlogin', data_type='character varying', is_nullable='NO'),
            ColumnDefinition(column_name='load_dt', data_type='timestamp without time zone', is_nullable='NO'),
            ColumnDefinition(column_name='load_src', data_type='character varying', is_nullable='NO'),
            ColumnDefinition(column_name='hk_user_names_hashdiff', data_type='uuid', is_nullable='NO'),
        ]

        auth_indexes = None

        auth_foreign_keys = [
            ForeignKeyConstraint(
                table_schema='dds',
                table_name='s_user_names',
                column_name='h_user_pk',
                foreign_table_schema='dds',
                foreign_table_name='h_user',
                foreign_column_name='h_user_pk'
            )
        ]

        result_key = "48~NF1caX70zeaZf6x"
        tup = "Таблица-сателлит для сохранения атрибутов пользователя готова. Продолжаем!"

        resp = pg.check_table_and_index(
            table_name,
            table_schema,
            auth_column,
            auth_indexes,  # TODO: реализовать проверку
            result_key,
            tup,
            auth_foreign_keys
        )

    return ok(resp)


@app.post('/de09050215_check_s_product_names')
def check_s_product_names():
    pg, err_msg = pg_service()
    if not pg:
        return error(err_msg or "Cannot create PG Client.")

    with PgLogging.query_log(config.PgConnect(), pg._student, "de09050215_check_s_product_names", request.get_json()):
        table_name = 's_product_names'
        table_schema = 'dds'

        auth_column = [
            ColumnDefinition(column_name='h_product_pk', data_type='uuid', is_nullable='NO'),
            ColumnDefinition(column_name='name', data_type='character varying', is_nullable='NO'),
            ColumnDefinition(column_name='load_dt', data_type='timestamp without time zone', is_nullable='NO'),
            ColumnDefinition(column_name='load_src', data_type='character varying', is_nullable='NO'),
            ColumnDefinition(column_name='hk_product_names_hashdiff', data_type='uuid', is_nullable='NO'),
        ]

        auth_indexes = None

        auth_foreign_keys = [
            ForeignKeyConstraint(
                table_schema=table_schema,
                table_name=table_name,
                column_name='h_product_pk',
                foreign_table_schema='dds',
                foreign_table_name='h_product',
                foreign_column_name='h_product_pk'
            )
        ]

        result_key = "DAYVC8HPnPXGtk|Ulh"
        tup = "Таблица-сателлит для сохранения атрибутов продукта готова."

        resp = pg.check_table_and_index(
            table_name,
            table_schema,
            auth_column,
            auth_indexes,
            result_key,
            tup,
            auth_foreign_keys
        )

    return ok(resp)


@app.post('/de09050216_check_s_restaurant_names')
def check_s_restaurant_names():
    pg, err_msg = pg_service()
    if not pg:
        return error(err_msg or "Cannot create PG Client.")

    with PgLogging.query_log(config.PgConnect(), pg._student, "de09050216_check_s_restaurant_names", request.get_json()):
        table_name = 's_restaurant_names'
        table_schema = 'dds'

        auth_column = [
            ColumnDefinition(column_name='h_restaurant_pk', data_type='uuid', is_nullable='NO'),
            ColumnDefinition(column_name='name', data_type='character varying', is_nullable='NO'),
            ColumnDefinition(column_name='load_dt', data_type='timestamp without time zone', is_nullable='NO'),
            ColumnDefinition(column_name='load_src', data_type='character varying', is_nullable='NO'),
            ColumnDefinition(column_name='hk_restaurant_names_hashdiff', data_type='uuid', is_nullable='NO'),
        ]

        auth_indexes = None

        auth_foreign_keys = [
            ForeignKeyConstraint(
                table_schema=table_schema,
                table_name=table_name,
                column_name='h_restaurant_pk',
                foreign_table_schema=table_schema,
                foreign_table_name='h_restaurant',
                foreign_column_name='h_restaurant_pk'
            )
        ]

        result_key = "rNPyEAqBbXBOA7qH#C"
        tup = "Таблица-сателлит для сохранения атрибутов ресторана готова."

        resp = pg.check_table_and_index(
            table_name,
            table_schema,
            auth_column,
            auth_indexes,
            result_key,
            tup,
            auth_foreign_keys
        )

    return ok(resp)


@app.post('/de09050217_check_s_order_cost')
def check_s_order_cost():

    # TODO: добавить проверки CHECK(cost >= 0), CHECK(payment >= 0)

    pg, err_msg = pg_service()
    if not pg:
        return error(err_msg or "Cannot create PG Client.")

    with PgLogging.query_log(config.PgConnect(), pg._student, "de09050217_check_s_order_cost", request.get_json()):
        table_name = 's_order_cost'
        table_schema = 'dds'

        auth_column = [
            ColumnDefinition(column_name='h_order_pk', data_type='uuid', is_nullable='NO'),
            ColumnDefinition(column_name='cost', data_type='numeric', is_nullable='NO'),
            ColumnDefinition(column_name='payment', data_type='numeric', is_nullable='NO'),
            ColumnDefinition(column_name='load_dt', data_type='timestamp without time zone', is_nullable='NO'),
            ColumnDefinition(column_name='load_src', data_type='character varying', is_nullable='NO'),
            ColumnDefinition(column_name='hk_order_cost_hashdiff', data_type='uuid', is_nullable='NO'),
        ]

        auth_indexes = None

        auth_foreign_keys = [
            ForeignKeyConstraint(
                table_schema=table_schema,
                table_name=table_name,
                column_name='h_order_pk',
                foreign_table_schema=table_schema,
                foreign_table_name='h_order',
                foreign_column_name='h_order_pk'
            )
        ]

        result_key = "Ivo8nvJE0yrP96xqpx"
        tup = "Таблица-сателлит для сохранения стоимости заказа готова."

        resp = pg.check_table_and_index(
            table_name,
            table_schema,
            auth_column,
            auth_indexes,
            result_key,
            tup,
            auth_foreign_keys
        )

    return ok(resp)


@app.post('/de09050218_check_s_order_status')
def check_s_order_status():

    pg, err_msg = pg_service()
    if not pg:
        return error(err_msg or "Cannot create PG Client.")

    with PgLogging.query_log(config.PgConnect(), pg._student, "de09050218_check_s_order_status", request.get_json()):
        table_name = 's_order_status'
        table_schema = 'dds'

        auth_column = [
            ColumnDefinition(column_name='h_order_pk', data_type='uuid', is_nullable='NO'),
            ColumnDefinition(column_name='status', data_type='character varying', is_nullable='NO'),
            ColumnDefinition(column_name='load_dt', data_type='timestamp without time zone', is_nullable='NO'),
            ColumnDefinition(column_name='load_src', data_type='character varying', is_nullable='NO'),
            ColumnDefinition(column_name='hk_order_status_hashdiff', data_type='uuid', is_nullable='NO'),
        ]

        auth_indexes = None

        auth_foreign_keys = [
            ForeignKeyConstraint(
                table_schema=table_schema,
                table_name=table_name,
                column_name='h_order_pk',
                foreign_table_schema=table_schema,
                foreign_table_name='h_order',
                foreign_column_name='h_order_pk'
            )
        ]

        result_key = "uqukupWQzwShlLbgrn"
        tup = "Таблица-сателлит для сохранения ствтуса заказа готова. Структура БД создана!"

        resp = pg.check_table_and_index(
            table_name,
            table_schema,
            auth_column,
            auth_indexes,
            result_key,
            tup,
            auth_foreign_keys
        )

    return ok(resp)


@app.post('/de09050601_StgMessageProcessor')
def check_StgMessageProcessor():
    req: Dict = request.get_json()  # type: ignore
    user_code = req['user_stg_message_processor_job']

    if 'StgMessageProcessor' not in user_code:
        return error('Не найден класс StgMessageProcessor')

    return ok({
        "result_key": 'gfuaAVhjGoQ8TiKY5e',
        "message": 'Санитарная работа выполнена. Можно приступать к делу.'
    })


@app.post('/de09050602_stg_repository')
def check_stg_repository():
    req: Dict = request.get_json()  # type: ignore
    user_code = req['stg_repository']

    try:
        fc = FileCoordinator(LockRepository(config.PgConnect(), app.logger), app.logger)
        tester = StgLoaderCheckService(fc, app.logger)
        test_passed, msg = tester.check_order_events_insert("/src", user_code)

        if not test_passed:
            return error(msg)

    except Exception as e:
        return error(str(e))

    return ok({
        "result_key": 'pfTi1J5L9veq0FGkxk',
        "message": 'Теперь у вас есть все необходимые инструменты, чтобы начать реализовывать обработчик сообщений.'
    })


@app.post('/de09050603_StgMessageProcessor')
def check_StgMessageProcessor_init():
    req: Dict = request.get_json()  # type: ignore
    user_code = req['user_stg_message_processor_job']

    try:
        fc = FileCoordinator(LockRepository(config.PgConnect(), app.logger), app.logger)
        tester = StgLoaderCheckService(fc, app.logger)
        test_passed, msg = tester.check_init("/src", user_code)

        if not test_passed:
            return error(msg)

    except Exception as e:
        return error(str(e))

    return ok({
        "result_key": 'mnix8GpQaoZQ6DSrcE',
        "message": 'Шапка класса `StgMessageProcessor` готова. Теперь надо поправить вызов конструктора.'
    })


@app.post('/de09050605_StgMessageProcessor')
def check_StgMessageProcessor_run():
    req: Dict = request.get_json()  # type: ignore
    user_code = req['user_stg_message_processor_job']

    try:

        fc = FileCoordinator(LockRepository(config.PgConnect(), app.logger), app.logger)
        tester = StgLoaderCheckService(fc, app.logger)
        check_passed, msg = tester.check_full_cycle_single("/src", user_code)

        if not check_passed:
            return error(msg)

    except Exception as e:
        return error(str(e))

    return ok({
        "result_key": 'mDGZHdJ3AugTgln93I',
        "message": 'Основная работа выполнена. Осталось чуть-чуть: нужно убедиться, что всё работает.'
    })


if __name__ == '__main__':
    app.logger.setLevel(logging.DEBUG)

    mr = MigrationRunner(config.PgConnect())
    mr.up()
    app.run(debug=True, host='0.0.0.0', use_reloader=False)
