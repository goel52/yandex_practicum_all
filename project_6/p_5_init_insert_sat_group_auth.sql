drop table if exists MY__DWH.s_auth_history;


create table MY__DWH.s_auth_history
(
    hk_l_user_group_activity bigint not null CONSTRAINT fk_s_auth_l_user_group_activity REFERENCES MY__DWH.l_user_group_activity (hk_l_user_group_activity),
    user_id_from int,
    event varchar(20),
    event_dt datetime,
    load_dt datetime,
    load_src varchar(20)
)
order by event_dt
SEGMENTED BY hk_l_user_group_activity all nodes
PARTITION BY event_dt::date
GROUP BY calendar_hierarchy_day(event_dt::date, 3, 2);
;



INSERT INTO MY__DWH.s_auth_history(hk_l_user_group_activity, user_id_from,event,event_dt,load_dt,load_src)

select luga.hk_l_user_group_activity
        ,gl.user_id_from
        ,gl.event
        ,gl.event_dt
        ,now() as load_dt
       ,'s3' as load_src


from MY__STAGING.group_log as gl
left join MY__DWH.h_groups as hg on gl.group_id = hg.group_id
left join MY__DWH.h_users as hu on gl.user_id = hu.user_id
left join MY__DWH.l_user_group_activity as luga on hg.hk_group_id = luga.hk_group_id and hu.hk_user_id = luga.hk_user_id

;