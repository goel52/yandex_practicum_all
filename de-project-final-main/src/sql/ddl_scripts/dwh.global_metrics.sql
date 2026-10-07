DROP TABLE MIKEPAFYANDEXRU__DWH.global_metrics;
CREATE TABLE MIKEPAFYANDEXRU__DWH.global_metrics(
	date_update 				   date 	     NOT NULL,
	currency_from 				   varchar(40) 	 NOT NULL,
	amount_total 				   numeric(19,2) NOT NULL,
	cnt_transactions 			   int 	         NOT NULL,
	avg_transactions_per_account   numeric(19,2) NOT NULL,
	cnt_accounts_make_transactions int 	         NOT NULL
)
PARTITION BY date_update
GROUP BY calendar_hierarchy_day(date_update, 2, 3);

COMMENT ON COLUMN MIKEPAFYANDEXRU__DWH.global_metrics.date_update                    IS 'дата расчёта';
COMMENT ON COLUMN MIKEPAFYANDEXRU__DWH.global_metrics.currency_from                  IS 'код валюты транзакции';
COMMENT ON COLUMN MIKEPAFYANDEXRU__DWH.global_metrics.amount_total                   IS 'общая сумма транзакций по валюте в долларах';
COMMENT ON COLUMN MIKEPAFYANDEXRU__DWH.global_metrics.cnt_transactions               IS 'общий объём транзакций по валюте';
COMMENT ON COLUMN MIKEPAFYANDEXRU__DWH.global_metrics.avg_transactions_per_account   IS 'средний объём транзакций с аккаунта';
COMMENT ON COLUMN MIKEPAFYANDEXRU__DWH.global_metrics.cnt_accounts_make_transactions IS 'количество уникальных аккаунтов с совершёнными транзакциями по валюте';

CREATE PROJECTION MIKEPAFYANDEXRU__DWH.global_metrics
(
    date_update,
    currency_from,
    amount_total,
    cnt_transactions,
    avg_transactions_per_account,
    cnt_accounts_make_transactions
)
AS
SELECT
    global_metrics.date_update,
    global_metrics.currency_from,
    global_metrics.amount_total,
    global_metrics.cnt_transactions,
    global_metrics.avg_transactions_per_account,
    global_metrics.cnt_accounts_make_transactions
FROM MIKEPAFYANDEXRU__DWH.global_metrics
ORDER BY date_update, currency_from
SEGMENTED BY hash(date_update, currency_from) ALL NODES KSAFE 1;