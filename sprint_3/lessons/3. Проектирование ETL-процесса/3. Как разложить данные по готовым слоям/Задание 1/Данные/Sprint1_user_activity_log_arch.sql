CREATE TABLE IF NOT EXISTS "Sprint1".user_activity_log_arch
(
    clientid bigint,
    hitdatetime timestamp without time zone,
    action character varying(20) COLLATE pg_catalog."default"
)
