drop SCHEMA "stg" CASCADE;

CREATE SCHEMA "stg"

create table stg.ordersystem_orders
(
    id           serial primary key,
    object_id    varchar not null,
    object_value text    not null,
    update_ts    timestamp not null
);

create table stg.ordersystem_restaurants
(
    id           serial primary key,
    object_id    varchar not null,
    object_value text    not null,
    update_ts    timestamp not null
);

create table stg.ordersystem_users
(
    id           serial primary key,
    object_id    varchar not null,
    object_value text    not null,
    update_ts    timestamp not null
);

-- check
SELECT count(*) -- должно вернуть 3
FROM information_schema.table_constraints tc
         INNER JOIN information_schema.constraint_column_usage ccu
                    ON tc.constraint_name = ccu.constraint_name and tc.constraint_schema = ccu.constraint_schema
WHERE tc.table_schema = 'stg'
  AND tc.table_name IN ('ordersystem_users', 'ordersystem_orders', 'ordersystem_restaurants')
  AND tc.constraint_type = 'UNIQUE'
  AND ccu.column_name = 'object_id';
-- check 2
SELECT * -- должно вернуть 3
FROM information_schema.table_constraints tc
         INNER JOIN information_schema.constraint_column_usage ccu
                    ON tc.constraint_name = ccu.constraint_name and tc.constraint_schema = ccu.constraint_schema
WHERE tc.table_schema = 'stg'
  AND tc.table_name IN ('ordersystem_users', 'ordersystem_orders', 'ordersystem_restaurants')
  AND tc.constraint_type = 'UNIQUE'
  AND ccu.column_name = 'object_id';
-- check 2
SELECT
    tc.constraint_name
FROM information_schema.table_constraints tc
         INNER JOIN information_schema.constraint_column_usage ccu
                    ON tc.constraint_name = ccu.constraint_name and tc.constraint_schema = ccu.constraint_schema
WHERE tc.table_schema = 'stg'
  AND tc.table_name IN ('ordersystem_users', 'ordersystem_orders', 'ordersystem_restaurants')
  AND tc.constraint_type = 'UNIQUE'
  AND ccu.column_name = 'object_id';

1	ordersystem_orders_object_id_uindex
2	ordersystem_users_object_id_uindex
3	ordersystem_restaurants_object_id_uindex

-- 3 

create unique index ordersystem_orders_object_id_uindex
	on stg.ordersystem_orders (object_id);

create unique index ordersystem_users_object_id_uindex
	on stg.ordersystem_users (object_id);

create unique index ordersystem_restaurants_object_id_uindex
	on stg.ordersystem_restaurants (object_id);

-- 3 новое

alter table stg.ordersystem_orders add constraint ordersystem_orders_object_id_uindex
	unique (object_id);

alter table stg.ordersystem_users add constraint ordersystem_users_object_id_uindex
	unique (object_id);

alter table stg.ordersystem_restaurants add constraint ordersystem_restaurants_object_id_uindex
	unique (object_id);

-- debug -
SELECT * -- должно вернуть 3
FROM information_schema.table_constraints tc
WHERE tc.table_schema = 'stg'
  AND tc.table_name IN ('ordersystem_users', 'ordersystem_orders', 'ordersystem_restaurants')
  AND tc.constraint_type = 'UNIQUE'

-- debug2 -
SELECT ccu.column_name -- Должно вернуть 3 строчки - 'restaurant_id', 'settlement_year', 'settlement_month'
FROM information_schema.table_constraints tc
        INNER JOIN information_schema.constraint_column_usage ccu
                    ON tc.constraint_name = ccu.constraint_name and tc.constraint_schema = ccu.constraint_schema
WHERE tc.table_schema = 'stg'
AND tc.table_name IN ('ordersystem_users', 'ordersystem_orders', 'ordersystem_restaurants')
AND tc.constraint_type = 'UNIQUE';