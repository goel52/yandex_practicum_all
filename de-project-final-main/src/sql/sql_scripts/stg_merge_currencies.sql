MERGE INTO MIKEPAFYANDEXRU__STAGING.currencies t
	  USING (
			WITH s3_deduplicated AS (
				SELECT
					date_update,
					currency_code,
					currency_code_with,
					currency_with_div,
					ROW_NUMBER() OVER (PARTITION BY date_update,
													currency_code,
													currency_code_with) AS rn
				FROM MIKEPAFYANDEXRU__STAGING.currencies_tmp_s3
			)
			SELECT
				COALESCE(k.date_update, s3.date_update) 			  AS date_update,
				COALESCE(k.currency_code, s3.currency_code) 		  AS currency_code,
				COALESCE(k.currency_code_with, s3.currency_code_with) AS currency_code_with,
				COALESCE(k.currency_with_div, s3.currency_with_div)   AS currency_with_div,
				CASE WHEN k.date_update IS NULL
						AND s3.date_update IS NOT NULL
					THEN 's3'
					ELSE 'kafka' END 								  AS load_src
			FROM MIKEPAFYANDEXRU__STAGING.currencies_tmp_kafka k
			FULL JOIN (SELECT * FROM s3_deduplicated WHERE rn=1) s3  ON k.date_update=s3.date_update
										 							AND k.currency_code=s3.currency_code
										 							AND k.currency_code_with=s3.currency_code_with
			) s
	     ON s.date_update   = t.date_update 
	    AND s.currency_code = t.currency_code
        AND s.currency_code_with = t.currency_code_with
WHEN MATCHED THEN UPDATE SET
                         currency_with_div = s.currency_with_div,
						 load_src		   = s.load_src
WHEN NOT MATCHED THEN INSERT (date_update,
					          currency_code,
					          currency_code_with,
					          currency_with_div,
							  load_src) 
                      VALUES (s.date_update,
					          s.currency_code,
					          s.currency_code_with,
					          s.currency_with_div,
							  s.load_src);