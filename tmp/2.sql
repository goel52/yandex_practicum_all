/* создание таблицы tmp_sources с данными из всех источников */
DROP TABLE IF EXISTS tmp_sources;
CREATE TEMP TABLE tmp_sources AS
SELECT 	 order_id
	,order_created_date
	,order_completion_date
	,order_status
	,craftsman_id
	,craftsman_name
	,craftsman_address
	,craftsman_birthday
	,craftsman_email
	,product_id
	,product_name
	,product_description
	,product_type
	,product_price
	,customer_id
	,customer_name
	,customer_address
	,customer_birthday
	,customer_email
FROM source1.craft_market_wide cmw
UNION
SELECT
	 cmoc.order_id
	,cmoc.order_created_date
	,cmoc.order_completion_date
	,cmoc.order_status
	,cmmp.craftsman_id
	,cmmp.craftsman_name
	,cmmp.craftsman_address
	,cmmp.craftsman_birthday
	,cmmp.craftsman_email
	,cmmp.product_id
	,cmmp.product_name
	,cmmp.product_description
	,cmmp.product_type
	,cmmp.product_price
	,cmoc.customer_id
	,cmoc.customer_name
	,cmoc.customer_address
	,cmoc.customer_birthday
	,cmoc.customer_email
FROM source2.craft_market_orders_customers cmoc
     INNER JOIN source2.craft_market_masters_products cmmp
	ON cmoc.craftsman_id = cmmp.craftsman_id
	   AND cmoc.product_id = cmmp.product_id
UNION
SELECT
	 cmo.order_id
	,cmo.order_created_date
	,cmo.order_completion_date
	,cmo.order_status
	,cmc.craftsman_id
	,cmc.craftsman_name
	,cmc.craftsman_address
	,cmc.craftsman_birthday
	,cmc.craftsman_email
	,cmo.product_id
	,cmo.product_name
	,cmo.product_description
	,cmo.product_type
	,cmo.product_price
	,cmc_2.customer_id
	,cmc_2.customer_name
	,cmc_2.customer_address
	,cmc_2.customer_birthday
	,cmc_2.customer_email
FROM source3.craft_market_craftsmans cmc
     INNER JOIN source3.craft_market_orders cmo
	ON cmo.craftsman_id = cmc.craftsman_id
     INNER JOIN source3.craft_market_customers cmc_2
        ON cmc_2.customer_id = cmo.customer_id;
   
/* создание таблицы tmp_sources_fact */
DROP TABLE IF EXISTS tmp_sources_fact;
CREATE TEMP TABLE tmp_sources_fact AS
SELECT DISTINCT
	 src.product_id -- идентификатор товара
	,src.craftsman_id  -- идентификатор мастера
	,src.customer_id -- идентификатор заказчика
	,src.order_created_date -- дата создания заказа
	,src.order_completion_date -- дата выполнения заказа
	,src.order_status -- статус выполнения заказа
	,current_timestamp AS load_dttm -- время заполнения таблицы - current_timestamp
FROM tmp_sources src
     INNER JOIN dwh.d_craftsman dc
	ON dc.craftsman_id = src.craftsman_id
     INNER JOIN dwh.d_customer dcust
	ON dcust.customer_id = src.customer_id
     INNER JOIN dwh.d_product dp
	ON dp.product_id = src.product_id;

/* Обновление существующих записей и добавление новых в dwh.f_order */
MERGE INTO dwh.f_order f
USING tmp_sources_fact t
ON f.product_id = t.product_id
   AND f.craftsman_id = t.craftsman_id
   AND f.customer_id = t.customer_id
   AND f.order_created_date = t.order_created_date
WHEN MATCHED THEN
  UPDATE SET
	 order_completion_date = t.order_completion_date
	,order_status = t.order_status
	,load_dttm = current_timestamp
WHEN NOT MATCHED THEN
  INSERT (product_id, craftsman_id, customer_id, order_created_date, order_completion_date, order_status, load_dttm)
  VALUES (t.product_id, t.craftsman_id, t.customer_id, t.order_created_date, t.order_completion_date, t.order_status, current_timestamp);