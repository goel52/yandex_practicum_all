select case when count(*)=0 then 'true' else 'false' end
from public.user_activity_log ual where customer_id is null;