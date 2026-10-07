MERGE INTO __STAGING.transactions_tmp_kafka t
	  USING (SELECT
            ...
			FROM __STAGING.transactions_input_tmp_kafka
			WHERE object_type = 'TRANSACTION') s
	     ON s.object_id   = t.object_id 
	    AND s.object_type = t.object_type
WHEN MATCHED THEN UPDATE SET
	            ...
WHEN NOT MATCHED THEN INSERT (...)
                      VALUES (...);