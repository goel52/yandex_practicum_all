CREATE SCHEMA IF NOT EXISTS cdm;

CREATE TABLE IF NOT EXISTS cdm.user_product_counters(
    id INT NOT NULL PRIMARY KEY GENERATED ALWAYS AS IDENTITY,--Можно id SERIAL NOT NULL PRIMARY KEY
    user_id UUID NOT NULL,
    product_id UUID NOT NULL,
    product_name VARCHAR NOT NULL,
    order_cnt INT NOT NULL DEFAULT(0) CHECK(order_cnt >= 0)
);

CREATE UNIQUE INDEX IF NOT EXISTS IDX_user_product_counters__user_id_product_id
ON cdm.user_product_counters (user_id, product_id);


CREATE TABLE IF NOT EXISTS cdm.user_category_counters(
    id INT NOT NULL PRIMARY KEY GENERATED ALWAYS AS IDENTITY,--Можно id SERIAL NOT NULL PRIMARY KEY
    user_id UUID NOT NULL,
    category_id UUID NOT NULL,
    category_name VARCHAR NOT NULL,
    order_cnt INT NOT NULL DEFAULT(0) CHECK(order_cnt >= 0)
);

CREATE UNIQUE INDEX IF NOT EXISTS IDX_user_category_counters__user_id_category_id
ON cdm.user_category_counters (user_id, category_id);



CREATE TABLE IF NOT EXISTS stg.order_events(
    id INT NOT NULL PRIMARY KEY GENERATED ALWAYS AS IDENTITY,--Можно id SERIAL NOT NULL PRIMARY KEY
    object_id INT NOT NULL UNIQUE,
    object_type VARCHAR NOT NULL,
    sent_dttm TIMESTAMP NOT NULL,
    payload JSON NOT NULL
);



CREATE TABLE IF NOT EXISTS dds.h_user(
    h_user_pk UUID NOT NULL PRIMARY KEY,
    user_id VARCHAR NOT NULL,
    load_dt timestamp NOT NULL,
    load_src VARCHAR NOT NULL
);



CREATE TABLE IF NOT EXISTS dds.h_product(
    h_product_pk UUID NOT NULL PRIMARY KEY,
    product_id VARCHAR NOT NULL,
    load_dt timestamp NOT NULL,
    load_src VARCHAR NOT NULL
);



CREATE TABLE IF NOT EXISTS dds.h_category(
    h_category_pk UUID NOT NULL PRIMARY KEY,
    category_name VARCHAR NOT NULL,
    load_dt timestamp NOT NULL,
    load_src VARCHAR NOT NULL
);



CREATE TABLE IF NOT EXISTS dds.h_restaurant(
    h_restaurant_pk UUID NOT NULL PRIMARY KEY,
    restaurant_id VARCHAR NOT NULL,
    load_dt timestamp NOT NULL,
    load_src VARCHAR NOT NULL
);


CREATE TABLE IF NOT EXISTS dds.h_order(
    h_order_pk UUID NOT NULL PRIMARY KEY,
    order_id INT NOT NULL,
    order_dt timestamp NOT NULL,
    load_dt timestamp NOT NULL,
    load_src VARCHAR NOT NULL
);



CREATE TABLE IF NOT EXISTS dds.l_order_product(
    hk_order_product_pk UUID NOT NULL PRIMARY KEY,
    h_order_pk UUID NOT NULL REFERENCES dds.h_order(h_order_pk),
    h_product_pk UUID NOT NULL REFERENCES dds.h_product(h_product_pk),
    load_dt timestamp NOT NULL,
    load_src VARCHAR NOT NULL
);



CREATE TABLE IF NOT EXISTS dds.l_product_restaurant(
    hk_product_restaurant_pk UUID NOT NULL PRIMARY KEY,
    h_restaurant_pk UUID NOT NULL REFERENCES dds.h_restaurant(h_restaurant_pk),
    h_product_pk UUID NOT NULL REFERENCES dds.h_product(h_product_pk),
    load_dt timestamp NOT NULL,
    load_src VARCHAR NOT NULL
);


CREATE TABLE IF NOT EXISTS dds.l_product_category(
    hk_product_category_pk UUID NOT NULL PRIMARY KEY,
    h_category_pk UUID NOT NULL REFERENCES dds.h_category(h_category_pk),
    h_product_pk UUID NOT NULL REFERENCES dds.h_product(h_product_pk),
    load_dt timestamp NOT NULL,
    load_src VARCHAR NOT NULL
);


CREATE TABLE IF NOT EXISTS dds.l_order_user(
    hk_order_user_pk UUID NOT NULL PRIMARY KEY,
    h_order_pk UUID NOT NULL REFERENCES dds.h_order(h_order_pk),
    h_user_pk UUID NOT NULL REFERENCES dds.h_user(h_user_pk),
    load_dt timestamp NOT NULL,
    load_src VARCHAR NOT NULL
);


CREATE TABLE IF NOT EXISTS dds.s_user_names(
    h_user_pk               UUID        NOT NULL REFERENCES dds.h_user(h_user_pk),
    username                VARCHAR     NOT NULL,
    userlogin               VARCHAR     NOT NULL,
    load_dt                 TIMESTAMP   NOT NULL,
    load_src                VARCHAR     NOT NULL,
    hk_user_names_hashdiff  UUID        NOT NULL UNIQUE,
    PRIMARY KEY(h_user_pk, load_dt)
);



CREATE TABLE IF NOT EXISTS dds.s_product_names(
    h_product_pk                UUID        NOT NULL REFERENCES dds.h_product(h_product_pk),
    name                        VARCHAR     NOT NULL,
    load_dt                     TIMESTAMP   NOT NULL,
    load_src                    VARCHAR     NOT NULL,
    hk_product_names_hashdiff   UUID        NOT NULL UNIQUE,
    PRIMARY KEY(h_product_pk, load_dt)
);



CREATE TABLE IF NOT EXISTS dds.s_restaurant_names(
    h_restaurant_pk                 UUID        NOT NULL
                                                REFERENCES dds.h_restaurant(h_restaurant_pk),
    name                            VARCHAR     NOT NULL,
    load_dt                         TIMESTAMP   NOT NULL,
    load_src                        VARCHAR     NOT NULL,
    hk_restaurant_names_hashdiff    UUID        NOT NULL UNIQUE,
    PRIMARY KEY(h_restaurant_pk, load_dt)
);



CREATE TABLE IF NOT EXISTS dds.s_order_cost(
    h_order_pk              UUID            NOT NULL REFERENCES dds.h_order(h_order_pk),
    cost                    DECIMAL(19, 5)  NOT NULL DEFAULT(0) CHECK(cost >= 0),
    payment                 DECIMAL(19, 5)  NOT NULL DEFAULT(0) CHECK(payment >= 0),
    load_dt                 TIMESTAMP       NOT NULL,
    load_src                VARCHAR         NOT NULL,
    hk_order_cost_hashdiff  UUID            NOT NULL UNIQUE,
    PRIMARY KEY(h_order_pk, load_dt)
);



CREATE TABLE IF NOT EXISTS dds.s_order_status(
    h_order_pk                  UUID        NOT NULL REFERENCES dds.h_order(h_order_pk),
    status                      VARCHAR     NOT NULL,
    load_dt                     TIMESTAMP   NOT NULL,
    load_src                    VARCHAR     NOT NULL,
    hk_order_status_hashdiff    UUID        NOT NULL UNIQUE,
    PRIMARY KEY(h_order_pk, load_dt)
);




