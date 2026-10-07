drop table if exists DE8A13NOTRULEZ_GMAIL_COM__DWH.l_user_message CASCADE;

create table DE8A13NOTRULEZ_GMAIL_COM__DWH.l_user_message
(
hk_l_user_message bigint primary key,
hk_user_id bigint not null CONSTRAINT fk_l_user_message_user REFERENCES DE8A13NOTRULEZ_GMAIL_COM__DWH.h_users (hk_user_id),
hk_message_id bigint not null CONSTRAINT fk_l_user_message_message REFERENCES DE8A13NOTRULEZ_GMAIL_COM__DWH.h_dialogs (hk_message_id),
load_dt datetime,
load_src varchar(20)
)
order by load_dt
SEGMENTED BY hk_user_id all nodes
PARTITION BY load_dt::date
GROUP BY calendar_hierarchy_day(load_dt::date, 3, 2);
	

drop table if exists DE8A13NOTRULEZ_GMAIL_COM__DWH.l_groups_dialogs CASCADE;


create table DE8A13NOTRULEZ_GMAIL_COM__DWH.l_groups_dialogs
(
    hk_l_groups_dialogs bigint primary key,
    hk_group_id      bigint not null CONSTRAINT fk_l_groups_dialogs_group REFERENCES DE8A13NOTRULEZ_GMAIL_COM__DWH.h_groups (hk_group_id),
    hk_message_id bigint not null CONSTRAINT fk_l_groups_dialogs_message REFERENCES DE8A13NOTRULEZ_GMAIL_COM__DWH.h_dialogs (hk_message_id),
    load_dt datetime,
    load_src varchar(20)
)
order by load_dt
SEGMENTED BY hk_l_groups_dialogs all nodes
PARTITION BY load_dt::date
GROUP BY calendar_hierarchy_day(load_dt::date, 3, 2);
;


drop table if exists DE8A13NOTRULEZ_GMAIL_COM__DWH.l_admins CASCADE;


create table DE8A13NOTRULEZ_GMAIL_COM__DWH.l_admins
(
    hk_l_admin_id bigint primary key,
    hk_group_id      bigint not null CONSTRAINT fk_l_admins_group REFERENCES DE8A13NOTRULEZ_GMAIL_COM__DWH.h_groups (hk_group_id),
    hk_user_id bigint not null CONSTRAINT fk_l_admins_user REFERENCES DE8A13NOTRULEZ_GMAIL_COM__DWH.h_users (hk_user_id),
    load_dt datetime,
    load_src varchar(20)
)
order by load_dt
SEGMENTED BY hk_l_admin_id all nodes
PARTITION BY load_dt::date
GROUP BY calendar_hierarchy_day(load_dt::date, 3, 2);
;
