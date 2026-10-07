INSERT INTO test_dds.dm_couriers
(courier_id_source, "name")
SELECT 
	sc."_id" AS courier_id_source,
	sc."name" AS name
FROM test_stg.couriers AS sc
LEFT JOIN test_dds.dm_couriers as dc
		ON sc."_id"  = dc.courier_id_source 
		AND sc."name" = dc."name" 
WHERE 
	dc.courier_id_source IS NULL
ON CONFLICT (courier_id_source) DO UPDATE SET
name = EXCLUDED.name;