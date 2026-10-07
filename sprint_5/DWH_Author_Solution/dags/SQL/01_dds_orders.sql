INSERT INTO test_dds.dm_orders
(order_id_source)
SELECT 
	sd.order_id AS order_id
FROM 
	test_stg.deliveries AS sd
LEFT JOIN
	test_dds.dm_orders AS ddo
		ON sd.order_id = ddo.order_id_source 
WHERE 
	sd.order_ts::date BETWEEN '{{yesterday_ds}}' AND '{{ds}}'
	AND ddo.order_id_source IS NULL;