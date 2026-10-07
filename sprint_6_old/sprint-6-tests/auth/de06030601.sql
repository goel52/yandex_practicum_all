
drop table if exists DE8A13NOTRULEZ_GMAIL_COM__DWH.h_users CASCADE;
drop table if exists DE8A13NOTRULEZ_GMAIL_COM__DWH.h_groups CASCADE;
drop table if exists DE8A13NOTRULEZ_GMAIL_COM__DWH.h_dialogs CASCADE;


create table DE8A13NOTRULEZ_GMAIL_COM__DWH.h_users
(
    hk_user_id bigint primary key,
    user_id      int,
    registration_dt datetime,
    load_dt datetime,
    load_src varchar(20)
)
order by load_dt
SEGMENTED BY hk_user_id all nodes
PARTITION BY load_dt::date
GROUP BY calendar_hierarchy_day(load_dt::date, 3, 2);




create table DE8A13NOTRULEZ_GMAIL_COM__DWH.h_groups
(
    hk_group_id bigint primary key,
    group_id      int,
    registration_dt datetime,
    load_dt datetime,
    load_src varchar(20)
)
order by load_dt
SEGMENTED BY hk_group_id all nodes
PARTITION BY load_dt::date
GROUP BY calendar_hierarchy_day(load_dt::date, 3, 2);
;



create table DE8A13NOTRULEZ_GMAIL_COM__DWH.h_dialogs
(
    hk_message_id bigint primary key,
    message_id      int,
    message_ts datetime,
    load_dt datetime,
    load_src varchar(20)
)
order by load_dt
SEGMENTED BY hk_message_id all nodes
PARTITION BY load_dt::date
GROUP BY calendar_hierarchy_day(load_dt::date, 3, 2);
;