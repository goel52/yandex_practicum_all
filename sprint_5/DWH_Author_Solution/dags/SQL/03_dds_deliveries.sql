INSERT INTO test_dds.dm_deliveries
(delivery_id_source)
SELECT 
	sd.delivery_id AS delivery_id
FROM 
	test_stg.deliveries AS sd
LEFT JOIN
	test_dds.dm_deliveries AS dd
		ON sd.delivery_id  =  dd.delivery_id_source 
WHERE 
	sd.order_ts::date BETWEEN '{{yesterday_ds}}' AND '{{ds}}'
	AND dd.delivery_id_source IS NULL;