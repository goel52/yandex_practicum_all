-- идемпотентность
DELETE FROM test_dds.fct_deliveries
WHERE order_ts::date BETWEEN '{{yesterday_ds}}' AND '{{ds}}';

-- вставка данных
INSERT INTO test_dds.fct_deliveries
(order_id_dwh, delivery_id_dwh, courier_id_dwh, order_ts, delivery_ts, address, rate, tip_sum, total_sum)
SELECT 
	ddo.order_id_dwh AS order_id_dwh,
	dd.delivery_id_dwh AS delivery_id_dwh,
	dc.courier_id_dwh AS courier_id_dwh,
	sd.order_ts AS order_ts,
	sd.delivery_ts AS delivery_ts,
	sd.address AS address,
	sd.rate AS rate,
	sd.tip_sum AS tip_sum,
	sd.sum AS total_sum
FROM 
	test_stg.deliveries AS sd
JOIN
	test_dds.dm_orders AS ddo 	
		ON sd.order_id = ddo.order_id_source 
JOIN 	
	test_dds.dm_deliveries AS dd
		ON sd.delivery_id = dd.delivery_id_source 
JOIN 
	test_dds.dm_couriers AS dc 
		ON sd.courier_id = dc.courier_id_source
WHERE 
	sd.order_ts::date BETWEEN '{{yesterday_ds}}' AND '{{ds}}' 