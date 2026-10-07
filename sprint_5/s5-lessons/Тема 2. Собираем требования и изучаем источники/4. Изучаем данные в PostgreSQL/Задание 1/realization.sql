
select 
    table_name, 
    column_name, 
    data_type, 
    character_maximum_length, 
    column_default, 
    is_nullable  
from information_schema.columns
where table_name in (
                        select distinct(table_name) 
                        from information_schema.tables 
                        where table_schema = 'public'
)
order by table_name asc


