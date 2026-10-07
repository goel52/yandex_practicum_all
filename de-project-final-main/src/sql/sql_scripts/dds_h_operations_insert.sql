INSERT INTO MIKEPAFYANDEXRU__DWH.h_operations(
	hk_operation_pk,
	operation_id,
	transaction_dt,
	load_dt,
	load_src)
SELECT
	hash(operation_id, transaction_dt) as hk_operation_pk,
	operation_id,
	transaction_dt,
	now() 							   AS load_dt,
	load_src
FROM MIKEPAFYANDEXRU__STAGING.transactions t
WHERE hash(operation_id, transaction_dt) NOT IN (SELECT hk_operation_pk FROM MIKEPAFYANDEXRU__DWH.h_operations);