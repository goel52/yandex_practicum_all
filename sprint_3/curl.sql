


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
    hk_user_names_pk UUID NOT NULL PRIMARY KEY,
    h_user_pk UUID NOT NULL REFERENCES dds.h_user(h_user_pk),
    username VARCHAR NOT NULL,
    userlogin VARCHAR NOT NULL,
    load_dt timestamp NOT NULL,
    load_src VARCHAR NOT NULL
);



CREATE TABLE IF NOT EXISTS dds.s_product_names(
    hk_product_names_pk UUID NOT NULL PRIMARY KEY,
    h_product_pk UUID NOT NULL REFERENCES dds.h_product(h_product_pk),
    name VARCHAR NOT NULL,
    load_dt timestamp NOT NULL,
    load_src VARCHAR NOT NULL
);


CREATE TABLE IF NOT EXISTS dds.s_restaurant_names(
    hk_restaurant_names_pk UUID NOT NULL PRIMARY KEY,
    h_restaurant_pk UUID NOT NULL REFERENCES dds.h_restaurant(h_restaurant_pk),
    name VARCHAR NOT NULL,
    load_dt timestamp NOT NULL,
    load_src VARCHAR NOT NULL
);


CREATE TABLE IF NOT EXISTS dds.s_order_cost(
    hk_order_cost_pk UUID NOT NULL PRIMARY KEY,
    h_order_pk UUID NOT NULL REFERENCES dds.h_order(h_order_pk),
    cost decimal(19, 5) NOT NULL DEFAULT(0) CHECK(cost >= 0),
    payment decimal(19, 5) NOT NULL DEFAULT(0) CHECK(payment >= 0),
    load_dt timestamp NOT NULL,
    load_src VARCHAR NOT NULL
);


CREATE TABLE IF NOT EXISTS dds.s_order_status(
    hk_order_status_pk UUID NOT NULL PRIMARY KEY,
    h_order_pk UUID NOT NULL REFERENCES dds.h_order(h_order_pk),
    status VARCHAR NOT NULL,
    load_dt timestamp NOT NULL,
    load_src VARCHAR NOT NULL
);

