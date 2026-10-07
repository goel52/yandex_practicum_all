(SELECT 
	min(u.registration_dt) as 'datestamp',
	'earliest user registration' as info
FROM DE8A13NOTRULEZ_GMAIL_COM__STAGING.users u)
UNION ALL
(SELECT
	max(u.registration_dt),
	'latest user registration'
FROM DE8A13NOTRULEZ_GMAIL_COM__STAGING.users u)
UNION ALL
(SELECT 
	min(g.registration_dt),
	'earliest group creation'
FROM DE8A13NOTRULEZ_GMAIL_COM__STAGING.groups g)
UNION ALL
(SELECT
	max(g.registration_dt),
	'latest group creation'
FROM DE8A13NOTRULEZ_GMAIL_COM__STAGING.groups g)
UNION ALL
(SELECT 
	min(d.message_ts),
	'earliest dialog message'
FROM DE8A13NOTRULEZ_GMAIL_COM__STAGING.dialogs d)
UNION ALL
(SELECT
	max(d.message_ts),
	'latest dialog message'
FROM DE8A13NOTRULEZ_GMAIL_COM__STAGING.dialogs d)
;