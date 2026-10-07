DELETE FROM MIKEPAFYANDEXRU__DWH.global_metrics WHERE date_update = date('{{execution_date}}');
INSERT INTO MIKEPAFYANDEXRU__DWH.global_metrics (
	date_update,
	currency_from,
	amount_total,
	cnt_transactions,
	avg_transactions_per_account,
	cnt_accounts_make_transactions
)
WITH
transactions_prepared AS (
	SELECT
		date(ho.transaction_dt) as date_update,
		hoa.currency_code || ' - ' || INITCAP(hod.country) as currency_from,
		hod.account_number_from,
		round(hoa.amount * COALESCE(scd.currency_with_div, 1) / 100, 2) AS amount_usd,
		ho.operation_id
	FROM MIKEPAFYANDEXRU__DWH.h_operations ho
	LEFT JOIN MIKEPAFYANDEXRU__DWH.s_operation_details hod  ON hod.hk_operation_pk=ho.hk_operation_pk
	LEFT JOIN MIKEPAFYANDEXRU__DWH.s_operation_amounts hoa  ON hoa.hk_operation_pk=ho.hk_operation_pk
	LEFT JOIN MIKEPAFYANDEXRU__DWH.l_operation_currency loc ON loc.hk_operation_pk=ho.hk_operation_pk
	LEFT JOIN MIKEPAFYANDEXRU__DWH.h_currencies hc 		 ON hc.hk_currency_pk=loc.hk_currency_pk
	LEFT JOIN MIKEPAFYANDEXRU__DWH.s_currency_details scd   ON scd.currency_country_with='usa' -- converting to USD
															AND scd.hk_currency_pk=hc.hk_currency_pk
	WHERE hod.status='done' 		  -- passing done transactions (one transactions hAS different state)
	  AND hod.account_number_from > 0 -- removing test accounts
	  AND hc.currency_code >= 100 	  -- removing currency codes less than 3 sings
	  AND date(ho.transaction_dt)=date('{{execution_date}}')
),
operations_per_account AS (
	 SELECT
	 	tp.date_update,
		tp.currency_from,
	 	tp.account_number_from,
	 	count(tp.operation_id) AS operations_per_account
	 FROM transactions_prepared tp
	 group by 1,2,3
),
avg_transactions_per_account AS (
	SELECT
		opa.date_update,
		opa.currency_from,
		round(avg(opa.operations_per_account), 2) AS avg_transactions_per_account
	FROM operations_per_account opa
	group by 1,2
),
metrics AS (
	SELECT
		tp.date_update,
		tp.currency_from,
		sum(tp.amount_usd) AS amount_total,
		count(tp.operation_id) AS cnt_transactions,
		count(distinct tp.account_number_from) AS cnt_accounts_make_transactions
	FROM transactions_prepared tp
	group by date_update,
			 currency_from
)
SELECT
	m.date_update,
	m.currency_from,
	m.amount_total,
	m.cnt_transactions,
	a.avg_transactions_per_account,
	m.cnt_accounts_make_transactions
FROM metrics m
INNER JOIN avg_transactions_per_account a  ON a.date_update=m.date_update
										  AND a.currency_from=m.currency_from