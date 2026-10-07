(SELECT 
    max(u.registration_dt) < now() as 'no future dates',
    min(u.registration_dt) > '2020-09-03' as 'no false-start dates',
    'users' as 'dataset'
FROM TESTUSER2__STAGING.users u)
UNION ALL
(SELECT
    max(g.registration_dt) < now() as 'no future dates',
    min(g.registration_dt) > '2020-09-03' as 'no false-start dates',
    'groups'
FROM TESTUSER2__STAGING.groups g)
UNION ALL
(SELECT
    max(d.message_ts) < now() as 'no future dates',
    min(d.message_ts) > '2020-Sep-03' as 'no false-start dates',
    'dialogs'
FROM TESTUSER2__STAGING.dialogs d);

--no future dates|no false-start dates|dataset|
-----------------+--------------------+-------+
--true           |true                |users  |
--true           |true                |groups |
--true           |false               |dialogs|
