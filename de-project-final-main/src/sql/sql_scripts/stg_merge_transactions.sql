MERGE INTO MIKEPAFYANDEXRU__STAGING.transactions t
	  USING (
			WITH s3_deduplicated AS (
				SELECT
					operation_id,
					account_number_from,
					account_number_to,
					currency_code,
					country,
					status,
					transaction_type,
					amount,
					transaction_dt,
					ROW_NUMBER() OVER (PARTITION BY operation_id, transaction_dt) AS rn
				FROM MIKEPAFYANDEXRU__STAGING.transactions_tmp_s3
			)
			SELECT
				COALESCE(k.operation_id, s3.operation_id) 				AS operation_id,
				COALESCE(k.account_number_from, s3.account_number_from) AS account_number_from,
				COALESCE(k.account_number_to, s3.account_number_to) 	AS account_number_to,
				COALESCE(k.currency_code, s3.currency_code) 			AS currency_code,
				COALESCE(k.country, s3.country) 						AS country,
				COALESCE(k.status, s3.status) 							AS status,
				COALESCE(k.transaction_type, s3.transaction_type) 		AS transaction_type,
				COALESCE(k.amount, s3.amount) 							AS amount,
				COALESCE(k.transaction_dt, s3.transaction_dt) 			AS transaction_dt,
				CASE WHEN k.operation_id IS NULL 
					  	  AND s3.operation_id IS NOT NULL
					 THEN 's3'
					 ELSE 'kafka' END 									AS load_src
			FROM MIKEPAFYANDEXRU__STAGING.transactions_tmp_kafka k
			FULL JOIN (SELECT * FROM s3_deduplicated WHERE rn=1) s3  ON s3.operation_id=k.operation_id
										 							AND s3.transaction_dt=k.transaction_dt
			) s
	     ON s.operation_id   = t.operation_id 
	    AND s.transaction_dt = t.transaction_dt
WHEN MATCHED THEN UPDATE SET
						 account_number_from = s.account_number_from,
						 account_number_to   = s.account_number_to,
						 currency_code 		 = s.currency_code,
						 country 			 = s.country,
						 status 			 = s.status,
						 transaction_type 	 = s.transaction_type,
						 amount 			 = s.amount,
						 load_src			 = s.load_src
WHEN NOT MATCHED THEN INSERT (operation_id,
							  account_number_from,
							  account_number_to,
							  currency_code,
							  country,
							  status,
							  transaction_type,
							  amount,
							  transaction_dt,
							  load_src) 
                      VALUES (s.operation_id,
 							  s.account_number_from,
 							  s.account_number_to,
 							  s.currency_code,
 							  s.country,
 							  s.status,
 							  s.transaction_type,
 							  s.amount,
 							  s.transaction_dt,
							  s.load_src);