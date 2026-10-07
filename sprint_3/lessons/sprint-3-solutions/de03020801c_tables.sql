SELECT
    table_name,
    column_name,
    data_type,
    character_maximum_length,
    numeric_precision,
    numeric_scale, 
    is_nullable
    FROM information_schema.columns
WHERE table_schema = 'stage'
    and (
        table_name = 'user_activity_log' or
        table_name = 'user_order_log' or
        table_name = 'customer_research'
    )
ORDER BY
    table_name,
    column_name;