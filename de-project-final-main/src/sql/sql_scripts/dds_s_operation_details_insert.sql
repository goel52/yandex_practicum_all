INSERT INTO MIKEPAFYANDEXRU__DWH.s_operation_details(
	hk_operation_pk,
	account_number_from,
	account_number_to,
	country,
	status,
	transaction_type,
	load_dt,
	load_src)
SELECT 
	hash(operation_id, transaction_dt) AS hk_operation_pk,
	account_number_from,
	account_number_to,
	country,
	status,
	transaction_type,
	now() 							   AS load_dt,
	load_src
FROM MIKEPAFYANDEXRU__STAGING.transactions t
WHERE hash(operation_id, transaction_dt) NOT IN (SELECT hk_operation_pk FROM MIKEPAFYANDEXRU__DWH.s_operation_details);