SELECT client_id,
       CASE WHEN action = 'visit' THEN hitdatetime ELSE NULL END AS visit_dt,
       CASE WHEN action = 'registration' THEN 1 ELSE 0 END AS is_registration
FROM user_activity_log
LIMIT 10;