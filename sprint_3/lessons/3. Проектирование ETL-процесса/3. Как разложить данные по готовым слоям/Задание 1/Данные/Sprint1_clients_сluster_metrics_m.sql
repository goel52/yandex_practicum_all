create table "Sprint1".clients_сluster_metrics_m
(
	date TIMESTAMP, 
	clientid BIGINT,
	utm_campaign VARCHAR(30),
	total_events int ,
	visit_events int,
	registration_events int,
	login_events int,
	visit_to_login_events int,
	total_pay_events int,
	accepted_method_actions int,
	avg_payment numeric(10,2),
	made_payments numeric(10,2),
	sum_payments numeric(10,2), 
	rejects_share numeric(10,2)
);