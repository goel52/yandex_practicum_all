select 
count(g.group_name),
count(distinct hash(g.group_name))
from DE8A13NOTRULEZ_GMAIL_COM__STAGING.groups g; 

