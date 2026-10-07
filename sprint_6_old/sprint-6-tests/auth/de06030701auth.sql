select age
        ,count(1)
from MY__DWH.s_user_socdem
where hk_user_id in (select hk_user_id
                        from MY__DWH.l_user_message
                        where hk_message_id in (select hk_message_id
                                                from MY__DWH.l_groups_dialogs
                                                where hk_group_id in (select hk_group_id
                                                                    from MY__DWH.h_groups
                                                                    order by registration_dt limit 10)))
group by age
order by 2 desc