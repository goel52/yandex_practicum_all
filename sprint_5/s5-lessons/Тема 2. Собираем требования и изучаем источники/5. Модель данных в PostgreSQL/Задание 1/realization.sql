--SELECT DISTINCT product_payment::json->>'product_name' AS product_name
--FROM (
--	SELECT json_array_elements(product_payments::json) AS product_payment
--	FROM (
--		SELECT event_value::json->>'product_payments' AS product_payments
--		FROM outbox
--		WHERE event_value::json->>'product_payments' IS NOT NULL
--	) AS product_payment_jsons
--) AS product_payments
--ORDER BY product_name ASC;

with a as (
SELECT (event_value::JSON->>'product_payments')::JSON->>1 AS product_payments
FROM outbox),
b as (
select (product_payments::JSON->>'product_name')::text as product_name
from a)
select distinct product_name
from b
where product_name is not null