INSERT INTO DE8A13NOTRULEZ_GMAIL_COM__DWH.l_admins(hk_l_admin_id, hk_group_id,hk_user_id,load_dt,load_src)
select
hash(hg.hk_group_id,hu.hk_user_id)
,hg.hk_group_id
,hu.hk_user_id
,now() as load_dt
,'s3' as load_src
from DE8A13NOTRULEZ_GMAIL_COM__STAGING.groups as g
left join DE8A13NOTRULEZ_GMAIL_COM__DWH.h_users as hu on g.admin_id = hu.user_id
left join DE8A13NOTRULEZ_GMAIL_COM__DWH.h_groups as hg on g.id = hg.group_id
where hash(hg.hk_group_id,hu.hk_user_id) not in (select hk_l_admin_id from DE8A13NOTRULEZ_GMAIL_COM__DWH.l_admins);

INSERT INTO DE8A13NOTRULEZ_GMAIL_COM__DWH.l_groups_dialogs(hk_l_groups_dialogs, hk_message_id,hk_group_id,load_dt,load_src)
select
       hash(hd.hk_message_id,hg.hk_group_id),
       hd.hk_message_id,
       hg.hk_group_id,
       now() as load_dt,
       's3' as load_src
from DE8A13NOTRULEZ_GMAIL_COM__STAGING.dialogs as d
left join DE8A13NOTRULEZ_GMAIL_COM__DWH.h_groups as hg on d.message_group = hg.group_id
left join DE8A13NOTRULEZ_GMAIL_COM__DWH.h_dialogs as hd on d.message_id = hd.message_id
where d.message_group is not null and hash(hd.hk_message_id,hg.hk_group_id) not in (select hk_l_groups_dialogs from DE8A13NOTRULEZ_GMAIL_COM__DWH.l_groups_dialogs);


INSERT INTO DE8A13NOTRULEZ_GMAIL_COM__DWH.l_user_message(hk_l_user_message, hk_user_id,hk_message_id,load_dt,load_src)
select
       hash(hd.hk_message_id,hu.hk_user_id),
       hd.hk_message_id,
       hu.hk_user_id,
       now() as load_dt,
       's3' as load_src
from DE8A13NOTRULEZ_GMAIL_COM__STAGING.dialogs as d
left join DE8A13NOTRULEZ_GMAIL_COM__DWH.h_users as hu on d.message_from = hu.user_id
left join DE8A13NOTRULEZ_GMAIL_COM__DWH.h_dialogs as hd on d.message_id = hd.message_id
where d.message_group is not null
    and hash(hd.hk_message_id,hu.hk_user_id) not in (select hk_l_user_message from DE8A13NOTRULEZ_GMAIL_COM__DWH.l_user_message)
    and hu.hk_user_id is not null;