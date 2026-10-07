-- for test
DROP SCHEMA IF EXISTS stage CASCADE;
CREATE SCHEMA stage;

--clear
-- DROP TABLE IF EXISTS stage.user_activity_log;
-- DROP TABLE IF EXISTS stage.user_order_log;
-- DROP TABLE IF EXISTS stage.customer_research;


--user activity log
CREATE TABLE stage.user_activity_log(
   ID serial ,
   date_time          TIMESTAMP ,
   action_id             BIGINT ,
   customer_id             BIGINT ,
   quantity             BIGINT ,
   PRIMARY KEY (ID)
);

CREATE INDEX main1 ON stage.user_activity_log (customer_id);

--user order log
CREATE TABLE stage.user_order_log(
   ID serial ,
   date_time          TIMESTAMP ,
   city_id integer,
   city_name varchar (100),
   customer_id             BIGINT ,
   first_name varchar (100),
   last_name varchar (100),
   item_id integer,
   item_name    varchar(100),
   quantity             BIGINT ,
   payment_amount numeric(14,2),

   PRIMARY KEY (ID)
);

CREATE INDEX main2 ON stage.user_order_log (customer_id);


--customer research
CREATE TABLE stage.customer_research(
   ID serial,
   date_id          TIMESTAMP ,
   category_id integer,
   geo_id   integer,
   sales_qty    integer,
   sales_amt numeric(14,2),


   PRIMARY KEY (ID)
);

CREATE INDEX main3 ON stage.customer_research (category_id);