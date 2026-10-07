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
,user_group_messages as (
    select --lum.hk_user_id
            --,lum.hk_message_id
            lgd.hk_group_id
            ,count(distinct lum.hk_user_id) as cnt_users_in_group_with_messages
    from MY__DWH.l_user_message as lum
    left join MY__DWH.l_groups_dialogs as lgd on lum.hk_message_id = lgd.hk_message_id
    group by lgd.hk_group_id
)


select  ugl.hk_group_id
        ,ugl.cnt_added_users -- вступившие пользователи в группу
        ,ugm.cnt_users_in_group_with_messages -- польователи с сообщением
        ,ugm.cnt_users_in_group_with_messages / ugl.cnt_added_users as group_conversion -- Конверсия из вступивших в хотя бы одно сообщение
from user_group_log as ugl
left join user_group_messages as ugm on ugl.hk_group_id = ugm.hk_group_id
order by ugm.cnt_users_in_group_with_messages / ugl.cnt_added_users desc