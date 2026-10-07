INSERT INTO MIKEPAFYANDEXRU__DWH.h_currencies(
	hk_currency_pk,
	currency_code,
	date_update,
	load_dt,
	load_src)
WITH pre_process AS (
	SELECT
		hash(c.currency_code, c.date_update) as hk_currency_pk,
		currency_code,
		date_update,
		now() 							 as load_dt,
		load_src,
		ROW_NUMBER() OVER (PARTITION BY hash(c.currency_code, c.date_update)) AS r_n
	FROM MIKEPAFYANDEXRU__STAGING.currencies c
	WHERE hash(c.currency_code, c.date_update) NOT IN (select hk_currency_pk from MIKEPAFYANDEXRU__DWH.h_currencies)
)
SELECT
	hk_currency_pk,
	currency_code,
	date_update,
	load_dt,
	load_src
FROM pre_process
WHERE r_n=1;