INSERT INTO MIKEPAFYANDEXRU__DWH.l_operation_currency(
	hk_operation_currency_pk,
	hk_operation_pk,
	hk_currency_pk,
	load_dt,
	load_src)
WITH pre_process AS (
	SELECT
		hash(hash(t.operation_id, t.transaction_dt),
			 hash(c.currency_code, c.date_update)) AS hk_operation_currency_pk,
		hash(t.operation_id, t.transaction_dt)     AS hk_operation_pk,
		hash(c.currency_code, c.date_update)       AS hk_currency_pk,
		now()                                      AS load_dt,
		CONCAT(t.load_src, c.load_src)             AS load_src,
		ROW_NUMBER() OVER (PARTITION BY hash(hash(t.operation_id, t.transaction_dt),
			 								 hash(c.currency_code, c.date_update))) as r_n
	FROM MIKEPAFYANDEXRU__STAGING.transactions t
	INNER JOIN MIKEPAFYANDEXRU__STAGING.currencies c  ON c.currency_code=t.currency_code
													 AND date(c.date_update)=date(t.transaction_dt)
	WHERE hash(hash(t.operation_id, t.transaction_dt),
			 hash(c.currency_code, c.date_update)) NOT IN (SELECT hk_operation_currency_pk FROM MIKEPAFYANDEXRU__DWH.l_operation_currency)
)
SELECT
	hk_operation_currency_pk,
	hk_operation_pk,
	hk_currency_pk,
	load_dt,
	load_src
FROM pre_process
WHERE r_n=1;