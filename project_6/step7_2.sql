with user_group_log as (
    select --sah.hk_l_user_group_activity
         --, sah.event
         --, luga.hk_user_id
          luga.hk_group_id
        ,count(distinct luga.hk_user_id) as cnt_added_users

    from MY__DWH.s_auth_history as sah
             left join MY__DWH.l_user_group_activity luga
                       on luga.hk_l_user_group_activity = sah.hk_l_user_group_activity
--подключаем самые ранние группы и их названия
             left join MY__DWH.h_groups as hg on luga.hk_group_id = hg.hk_group_id
--условия
    where sah.event = 'add'
      and hg.hk_group_id in (
        --10 самых ранних групп
        select hk_group_id
        from MY__DWH.h_groups
        order by registration_dt
        limit 10
    )
    group by luga.hk_group_id
)

select hk_group_id
			,cnt_added_users
from user_group_messages
order by cnt_added_users
limit 10
;
