SELECT
    tablename,
    indexname
FROM pg_indexes
WHERE schemaname = 'stage'
    and (
        tablename = 'user_activity_log' or
        tablename = 'user_order_log' or
        tablename = 'customer_research'
    )
ORDER BY
    tablename,
    indexname;
