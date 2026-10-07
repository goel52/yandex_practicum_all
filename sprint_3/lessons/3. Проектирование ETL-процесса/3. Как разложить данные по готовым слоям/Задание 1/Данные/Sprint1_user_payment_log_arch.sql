CREATE TABLE IF NOT EXISTS "Sprint1".user_payment_log_arch
(
    hitdatetime timestamp without time zone,
    action character varying(20) COLLATE pg_catalog."default",
    clientid bigint,
    payment_amount numeric(14,2)
)
