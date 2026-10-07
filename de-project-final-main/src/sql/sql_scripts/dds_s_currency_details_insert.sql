INSERT INTO MIKEPAFYANDEXRU__DWH.s_currency_details(
	hk_currency_pk,
    currency_code_with,
	currency_country,
	currency_country_with,
	currency_with_div,
	load_dt,
	load_src)
WITH currencies_list as (
SELECT
	DISTINCT
	currency_code,
	country
FROM MIKEPAFYANDEXRU__STAGING.transactions t
)
SELECT
hash(currency_code, date_update) 											   AS hk_currency_pk,
currency_code_with,
(SELECT country FROM currencies_list WHERE currency_code=c.currency_code) 	   AS currency_country,
(SELECT country FROM currencies_list WHERE currency_code=c.currency_code_with) AS currency_country_with,
currency_with_div,
now() 																		   AS load_dt,
load_src
FROM MIKEPAFYANDEXRU__STAGING.currencies c
WHERE hash(currency_code, date_update) NOT IN (SELECT hk_currency_pk FROM MIKEPAFYANDEXRU__DWH.s_currency_details);