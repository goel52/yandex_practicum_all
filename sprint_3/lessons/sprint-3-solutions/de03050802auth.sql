--f_activity
delete from mart.f_activity;

INSERT INTO mart.f_activity (activity_id, date_id, click_number)
select  ual.action_id,
		dc.date_id,
		sum(ual.quantity) as click_number
from stage.user_activity_log as ual
left join mart.d_calendar as dc on to_date(ual.date_time::TEXT,'YYYY-MM-DD') = dc.fact_date
group by ual.action_id, dc.date_id;

--f_daily_sales
delete from mart.f_daily_sales;

INSERT INTO mart.f_daily_sales  (date_id, item_id, customer_id , price , quantity , payment_amount)
select
	dc.date_id,
	uol.item_id,
	uol.customer_id,
	avg(uol.payment_amount / quantity) as price,
	sum(uol.quantity),
	sum(uol.payment_amount)
from stage.user_order_log as uol
left join mart.d_calendar as dc on to_date(uol.date_time::TEXT,'YYYY-MM-DD') = dc.fact_date
group by dc.date_id,uol.item_id,uol.customer_id;