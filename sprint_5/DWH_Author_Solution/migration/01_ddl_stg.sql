CREATE TABLE IF NOT EXISTS test_stg.couriers(
	id serial PRIMARY KEY,
	courier_id varchar(30),
	name varchar 
);

CREATE TABLE IF NOT EXISTS test_stg.deliveries(
	id serial PRIMARY KEY,
	order_id varchar(30),
	order_ts timestamp,
	delivery_id varchar(30),
	courier_id 	varchar(30),
	address varchar,
	delivery_ts timestamp,
	rate integer,
	sum numeric (14, 2),
	tip_sum numeric (14, 2)
);