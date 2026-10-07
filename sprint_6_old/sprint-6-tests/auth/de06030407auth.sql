(SELECT count(1), 'missing group admin info' as info
FROM DE8A13NOTRULEZ_GMAIL_COM__STAGING.groups g LEFT JOIN DE8A13NOTRULEZ_GMAIL_COM__STAGING.users u ON g.admin_id = u.id
WHERE u.id is NULL)
UNION ALL
(SELECT count(1), 'missing sender info'
FROM DE8A13NOTRULEZ_GMAIL_COM__STAGING.dialogs d LEFT JOIN DE8A13NOTRULEZ_GMAIL_COM__STAGING.users u ON d.message_from = u.id
WHERE u.id is NULL)
UNION ALL  
(SELECT count(1), 'missing receiver info'
FROM DE8A13NOTRULEZ_GMAIL_COM__STAGING.dialogs d LEFT JOIN DE8A13NOTRULEZ_GMAIL_COM__STAGING.users u ON d.message_to = u.id
WHERE u.id is NULL)
UNION ALL 
(SELECT count(1), 'norm receiver info'
FROM DE8A13NOTRULEZ_GMAIL_COM__STAGING.dialogs d LEFT JOIN DE8A13NOTRULEZ_GMAIL_COM__STAGING.users u ON d.message_to = u.id
WHERE u.id is not NULL);