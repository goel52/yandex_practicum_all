select case when count(*)=0 then 'true' else 'false' end
from public.user_order_log uol where customer_id is null;