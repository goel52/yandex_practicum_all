INSERT INTO test_cdm.couriers_pay_mart
(courier_id, courier_name, settlement_year, settlement_month, orders_count,
orders_total_sum, rate_avg, order_processing_fee, courier_order_sum, courier_tips_sum, courier_reward_sum)

-- считаем средний рейтинг за период
WITH couriers_rate AS
	(SELECT 
		fd.courier_id_dwh AS courier_id,
		date_part('YEAR', fd.order_ts) AS settlement_year,
		date_part('MONTH', fd.order_ts) AS settlement_month,
		avg(fd.rate) AS rate_avg
	FROM 
		test_dds.fct_deliveries AS fd
	GROUP BY 1, 2, 3),
-- расчет курьеру за каждый заказ
courier_sum AS
	(SELECT 
		cr.courier_id,
		cr.settlement_year,
		cr.settlement_month,
		CASE 
			WHEN cr.rate_avg < 4 THEN CASE WHEN fd.total_sum * 0.05 < 100 THEN 100 ELSE fd.total_sum * 0.05 END
			WHEN cr.rate_avg >= 4 AND cr.rate_avg < 4.5 THEN CASE WHEN fd.total_sum * 0.07 < 150 THEN 150 ELSE fd.total_sum * 0.07 END
			WHEN cr.rate_avg >= 4.5 AND cr.rate_avg < 4.9 THEN CASE WHEN fd.total_sum * 0.08 < 175 THEN 175 ELSE fd.total_sum * 0.08 END
			WHEN cr.rate_avg > 4.9 THEN CASE WHEN fd.total_sum * 0.1 < 200 THEN 200 ELSE fd.total_sum * 0.1 END
		END AS courier_order_sum,
		fd.total_sum,
		fd.tip_sum,
		fd.order_id_dwh
	FROM 
		couriers_rate AS cr
	JOIN
		test_dds.fct_deliveries AS fd
			ON fd.courier_id_dwh = cr.courier_id
			AND date_part('YEAR', fd.order_ts) = cr.settlement_year
			AND date_part('MONTH', fd.order_ts) = cr.settlement_month)
-- считаем все метрики
SELECT 
	cs.courier_id AS courier_id,
	dc."name" AS courier_name,
	cs.settlement_year AS settlement_year,
	cs.settlement_month AS settlement_month,
	count(*) AS orders_count,
	sum(cs.total_sum) AS orders_total_sum,
	avg(fd.rate) AS rate_avg,
	sum(cs.total_sum) * 0.25 AS order_processing_fee,
	sum(cs.courier_order_sum) AS courier_order_sum,
	sum(cs.tip_sum) AS courier_tips_sum,
	sum(cs.courier_order_sum) + sum(cs.tip_sum)*0.95 AS courier_reward_sum
FROM 
	courier_sum AS cs
JOIN
	test_dds.dm_couriers AS dc
		ON cs.courier_id = dc.courier_id_dwh 
JOIN 
	test_dds.fct_deliveries AS fd
		ON fd.order_id_dwh  = cs.order_id_dwh
		INSERT INTO test_cdm.couriers_pay_mart
(courier_id, courier_name, settlement_year, settlement_month, orders_count,
orders_total_sum, rate_avg, order_processing_fee, courier_order_sum, courier_tips_sum, courier_reward_sum)
WITH couriers_rate AS
	(SELECT 
		fd.courier_id_dwh AS courier_id,
		date_part('YEAR', fd.order_ts) AS settlement_year,
		date_part('MONTH', fd.order_ts) AS settlement_month,
		avg(fd.rate) AS rate_avg
	FROM 
		test_dds.fct_deliveries AS fd
	GROUP BY 1, 2, 3),
courier_sum AS
	(SELECT 
		cr.courier_id,
		cr.settlement_year,
		cr.settlement_month,
		CASE 
			WHEN cr.rate_avg < 4 THEN CASE WHEN fd.total_sum * 0.05 < 100 THEN 100 ELSE fd.total_sum * 0.05 END
			WHEN cr.rate_avg >= 4 AND cr.rate_avg < 4.5 THEN CASE WHEN fd.total_sum * 0.07 < 150 THEN 150 ELSE fd.total_sum * 0.07 END
			WHEN cr.rate_avg >= 4.5 AND cr.rate_avg < 4.9 THEN CASE WHEN fd.total_sum * 0.08 < 175 THEN 175 ELSE fd.total_sum * 0.08 END
			WHEN cr.rate_avg > 4.9 THEN CASE WHEN fd.total_sum * 0.1 < 200 THEN 200 ELSE fd.total_sum * 0.1 END
		END AS courier_order_sum,
		fd.total_sum,
		fd.tip_sum,
		fd.order_id_dwh
	FROM 
		couriers_rate AS cr
	JOIN
		test_dds.fct_deliveries AS fd
			ON fd.courier_id_dwh = cr.courier_id
			AND date_part('YEAR', fd.order_ts) = cr.settlement_year
			AND date_part('MONTH', fd.order_ts) = cr.settlement_month)
SELECT 
	cs.courier_id AS courier_id,
	dc."name" AS courier_name,
	cs.settlement_year AS settlement_year,
	cs.settlement_month AS settlement_month,
	count(*) AS orders_count,
	sum(cs.total_sum) AS orders_total_sum,
	avg(fd.rate) AS rate_avg,
	sum(cs.total_sum) * 0.25 AS order_processing_fee,
	sum(cs.courier_order_sum) AS courier_order_sum,
	sum(cs.tip_sum) AS courier_tips_sum,
	sum(cs.courier_order_sum) + sum(cs.tip_sum)*0.95 AS courier_reward_sum
FROM 
	courier_sum AS cs
JOIN
	test_dds.dm_couriers AS dc
		ON cs.courier_id = dc.courier_id_dwh 
JOIN 
	test_dds.fct_deliveries AS fd
		ON fd.order_id_dwh  = cs.order_id_dwh
		AND date_part('YEAR', fd.order_ts) BETWEEN date_part('YEAR', '{{yesterday_ds}}'::date) AND date_part('YEAR', '{{ds}}'::date)
		AND date_part('MONTH', fd.order_ts) BETWEEN date_part('MONTH', '{{yesterday_ds}}'::date) AND date_part('MONTH', '{{ds}}'::date)
GROUP BY 1, 2, 3, 4
-- обновляем данные
ON CONFLICT (courier_id, settlement_year, settlement_month) DO UPDATE SET
	courier_name = EXCLUDED.courier_name,
	orders_count = EXCLUDED.orders_count,
	orders_total_sum = EXCLUDED.orders_total_sum,
	rate_avg = EXCLUDED.rate_avg,
	order_processing_fee = EXCLUDED.order_processing_fee,
	courier_order_sum = EXCLUDED.courier_order_sum,
	courier_tips_sum = EXCLUDED.courier_tips_sum,
	courier_reward_sum = EXCLUDED.courier_reward_sum