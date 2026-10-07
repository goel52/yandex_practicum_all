DROP SCHEMA if exists mart CASCADE;
DROP SCHEMA if exists stage CASCADE;
CREATE SCHEMA if not exists mart;
CREATE SCHEMA if not exists stage;


DROP TABLE IF EXISTS mart.d_city;
DROP TABLE IF EXISTS mart.f_daily_sales;
DROP TABLE IF EXISTS mart.f_research;
DROP TABLE IF EXISTS mart.f_activity;
DROP TABLE IF EXISTS mart.d_calendar;
DROP TABLE IF EXISTS mart.d_item;
DROP TABLE IF EXISTS mart.d_customer;

CREATE TABLE mart.d_customer(

   customer_id      INT NOT NULL PRIMARY KEY,
   first_name       varchar(15),
   last_name        varchar(15),
   city_id          INT
);
CREATE INDEX d_cust1  ON mart.d_customer (customer_id);

CREATE TABLE mart.d_city(
   id               SERIAL      PRIMARY KEY,
   city_id          INT,
   city_name        varchar(50)
);
CREATE INDEX d_city1  ON mart.d_city (city_id);

CREATE TABLE mart.d_item(

   item_id          INT         NOT NULL PRIMARY KEY,
   item_name        varchar(50)
);
CREATE INDEX d_item1  ON mart.d_item (item_id);



CREATE TABLE mart.d_calendar(
   date_id          INT,
   fact_date       date ,
   day_num          INT,
   month_num        INT,
   month_name       VARCHAR(8),
   year_num         INT,
  
  PRIMARY KEY(date_id)
);
CREATE INDEX d_calendar1  ON mart.d_calendar (date_id);


CREATE TABLE mart.f_activity(
   activity_id      INT NOT NULL,
   date_id          INT NOT NULL,
   click_number     INT,
   PRIMARY KEY (activity_id, date_id),
  FOREIGN KEY (date_id) REFERENCES mart.d_calendar(date_id) ON UPDATE CASCADE
);
CREATE INDEX f_activity1  ON mart.f_activity (date_id);
CREATE INDEX f_activity2  ON mart.f_activity (activity_id);

CREATE TABLE mart.f_daily_sales(
   date_id          INT NOT NULL,
   item_id          INT NOT NULL,
   customer_id      INT NOT NULL,
   price            decimal(10,2), --цена из прайс листа
   quantity         BIGINT,
   payment_amount   DECIMAL(10,2),
   PRIMARY KEY (date_id, item_id, customer_id),
   FOREIGN KEY (date_id) REFERENCES mart.d_calendar(date_id) ON UPDATE CASCADE,
   FOREIGN KEY (item_id) REFERENCES mart.d_item(item_id) ON UPDATE CASCADE,
   FOREIGN KEY (customer_id) REFERENCES mart.d_customer(customer_id) ON UPDATE CASCADE
);
CREATE INDEX f_ds1  ON mart.f_daily_sales (date_id);
CREATE INDEX f_ds2  ON mart.f_daily_sales (item_id);
CREATE INDEX f_ds3  ON mart.f_daily_sales (customer_id);



CREATE TABLE mart.f_research(
   date_id          INT NOT NULL,
  item_id INT NOT NULL,
  customer_id INT NOT NULL,
   geo_id           INT NOT NULL,
   quantity         BIGINT,
   amount           DECIMAL(10,2),
   PRIMARY KEY (date_id, item_id, customer_id),
   FOREIGN KEY (date_id) REFERENCES mart.d_calendar(date_id) ON UPDATE CASCADE,
   FOREIGN KEY (item_id) REFERENCES mart.d_item(item_id) ON UPDATE CASCADE,
   FOREIGN KEY (customer_id) REFERENCES mart.d_customer(customer_id) ON UPDATE CASCADE
);
CREATE INDEX f_r1  ON mart.f_daily_sales (date_id);
CREATE INDEX f_r2  ON mart.f_daily_sales (item_id);
CREATE INDEX f_r3  ON mart.f_daily_sales (customer_id);