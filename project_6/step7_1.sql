with user_group_messages as (
    select  lgd.hk_group_id
            ,count(distinct lum.hk_user_id) as cnt_users_in_group_with_messages
    from MY__DWH.l_user_message as lum
    left join MY__DWH.l_groups_dialogs as lgd on lum.hk_message_id = lgd.hk_message_id
    group by lgd.hk_group_id
)

select hk_group_id,
			cnt_users_in_group_with_messages
from user_group_messages
order by cnt_users_in_group_with_messages
limit 10
