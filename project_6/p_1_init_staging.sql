
drop table if exists MY__STAGING.group_log;

create table MY__STAGING.group_log
(
    group_id      int,
    user_id int,
    user_id_from int,
    event varchar(100),
    event_dt datetime
)
order by group_id, user_id, event_dt
SEGMENTED BY hash(group_id) all nodes
PARTITION BY event_dt::date
GROUP BY calendar_hierarchy_day(event_dt::date, 3, 2);
;
