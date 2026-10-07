MERGE INTO MIKEPAFYANDEXRU__STAGING.currencies_tmp_kafka t
	  USING (SELECT
				CAST(object_id AS uuid) 														  AS object_id,
				object_type,
				sent_dttm,
				CAST(MAPLOOKUP(MapJSONExtractor(payload), 'date_update')        as date)	      AS date_update,
				CAST(MAPLOOKUP(MapJSONExtractor(payload), 'currency_code')      as integer)       AS currency_code,
				CAST(MAPLOOKUP(MapJSONExtractor(payload), 'currency_code_with') as integer)       AS currency_code_with,
				CAST(MAPLOOKUP(MapJSONExtractor(payload), 'currency_with_div')  as numeric(19,2)) AS currency_with_div
			FROM MIKEPAFYANDEXRU__STAGING.transactions_input_tmp_kafka
			WHERE object_type = 'CURRENCY') s
	     ON s.object_id   = t.object_id 
	    AND s.object_type = t.object_type
WHEN MATCHED THEN UPDATE SET
						 sent_dttm          = s.sent_dttm,
                         date_update        = s.date_update,
                         currency_code      = s.currency_code,
                         currency_code_with = s.currency_code_with,
                         currency_with_div  = s.currency_with_div
WHEN NOT MATCHED THEN INSERT (object_id,
                              object_type,
					          sent_dttm,
					          date_update,
					          currency_code,
					          currency_code_with,
					          currency_with_div) 
                      VALUES (s.object_id, 
					          s.object_type,
					          s.sent_dttm,
					          s.date_update,
					          s.currency_code,
					          s.currency_code_with,
					          s.currency_with_div);