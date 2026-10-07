-- transactions_input_tmp_kafka
DROP TABLE IF EXISTS MIKEPAFYANDEXRU__STAGING.transactions_input_tmp_kafka;
CREATE TABLE MIKEPAFYANDEXRU__STAGING.transactions_input_tmp_kafka
(
	id 			 identity 	   PRIMARY KEY,
	object_id 	 varchar(40)   NOT NULL,
	object_type  varchar(20)   NOT NULL,
	sent_dttm    timestamp 	   NOT NULL,
	payload  	 varchar(1024) NOT NULL

)
PARTITION BY sent_dttm::date
GROUP BY calendar_hierarchy_day(sent_dttm::date, 2, 3);

COMMENT ON COLUMN MIKEPAFYANDEXRU__STAGING.transactions_input_tmp_kafka.id 	        IS 'идентификатор записи';
COMMENT ON COLUMN MIKEPAFYANDEXRU__STAGING.transactions_input_tmp_kafka.object_id   IS 'идентификатор объекта в событии';
COMMENT ON COLUMN MIKEPAFYANDEXRU__STAGING.transactions_input_tmp_kafka.object_type IS 'тип объекта';
COMMENT ON COLUMN MIKEPAFYANDEXRU__STAGING.transactions_input_tmp_kafka.sent_dttm   IS 'дата и время отправки сообщения';
COMMENT ON COLUMN MIKEPAFYANDEXRU__STAGING.transactions_input_tmp_kafka.payload     IS 'событие в формате JSON';

CREATE PROJECTION MIKEPAFYANDEXRU__STAGING.transactions_input_tmp_kafka
(
    id,
    object_id,
    object_type,
    sent_dttm,
    payload
)
AS
SELECT
	transactions_input_tmp_kafka.id,
	transactions_input_tmp_kafka.object_id,
	transactions_input_tmp_kafka.object_type,
	transactions_input_tmp_kafka.sent_dttm,
	transactions_input_tmp_kafka.payload
FROM MIKEPAFYANDEXRU__STAGING.transactions_input_tmp_kafka
ORDER BY transactions_input_tmp_kafka.id
SEGMENTED BY hash(object_id, object_type) ALL NODES KSAFE 1;


-- transactions_tmp_kafka
DROP TABLE IF EXISTS MIKEPAFYANDEXRU__STAGING.transactions_tmp_kafka;
CREATE TABLE MIKEPAFYANDEXRU__STAGING.transactions_tmp_kafka
(
	object_id 	 		uuid   	    NOT NULL,
	object_type  		varchar(20) NOT NULL,
	sent_dttm    		timestamp 	NOT NULL,
	operation_id		uuid		NOT NULL,
	account_number_from int 		NOT NULL,
	account_number_to	int 		NOT NULL,	
	currency_code		int 		NOT NULL,
	country				varchar(20) NOT NULL,
	status				varchar(20) NOT NULL,
	transaction_type	varchar(40) NOT NULL,
	amount				int 		NOT NULL,
	transaction_dt		timestamp	NOT NULL,

	CONSTRAINT unique_object_id_type UNIQUE(object_id, object_type) ENABLED,
	CONSTRAINT is_transaction CHECK(object_type = 'TRANSACTION') ENABLED
)
PARTITION BY sent_dttm::date
GROUP BY calendar_hierarchy_day(sent_dttm::date, 2, 3);

COMMENT ON COLUMN MIKEPAFYANDEXRU__STAGING.transactions_tmp_kafka.object_id   		  IS 'идентификатор объекта в событии';
COMMENT ON COLUMN MIKEPAFYANDEXRU__STAGING.transactions_tmp_kafka.object_type 		  IS 'тип объекта';
COMMENT ON COLUMN MIKEPAFYANDEXRU__STAGING.transactions_tmp_kafka.sent_dttm   		  IS 'дата и время отправки сообщения';
COMMENT ON COLUMN MIKEPAFYANDEXRU__STAGING.transactions_tmp_kafka.operation_id  	  IS 'id транзакции';
COMMENT ON COLUMN MIKEPAFYANDEXRU__STAGING.transactions_tmp_kafka.account_number_from IS 'внутренний бухгалтерский номер счёта транзакции ОТ КОГО';
COMMENT ON COLUMN MIKEPAFYANDEXRU__STAGING.transactions_tmp_kafka.account_number_to   IS 'внутренний бухгалтерский номер счёта транзакции К КОМУ';
COMMENT ON COLUMN MIKEPAFYANDEXRU__STAGING.transactions_tmp_kafka.currency_code 	  IS 'трёхзначный код валюты страны, из которой идёт транзакция';
COMMENT ON COLUMN MIKEPAFYANDEXRU__STAGING.transactions_tmp_kafka.country 			  IS 'страна-источник транзакции';
COMMENT ON COLUMN MIKEPAFYANDEXRU__STAGING.transactions_tmp_kafka.status 			  IS 'статус проведения транзакции [queued|in_progress|blocked|done|chargeback]';
COMMENT ON COLUMN MIKEPAFYANDEXRU__STAGING.transactions_tmp_kafka.transaction_type 	  IS 'тип транзакции во внутреннем учёте [authorisation|sbp_incoming|sbp_outgoing|transfer_incoming|transfer_outgoing|c2b_partner_incoming|c2b_partner_outgoing]';
COMMENT ON COLUMN MIKEPAFYANDEXRU__STAGING.transactions_tmp_kafka.amount 			  IS 'целочисленная сумма транзакции в минимальной единице валюты страны (копейка, цент, куруш)';
COMMENT ON COLUMN MIKEPAFYANDEXRU__STAGING.transactions_tmp_kafka.transaction_dt      IS 'дата и время исполнения транзакции до миллисекунд';  

CREATE PROJECTION MIKEPAFYANDEXRU__STAGING.transactions_tmp_kafka
(
    object_id,
    object_type,
    sent_dttm,
    operation_id,
    account_number_from,
    account_number_to,
    currency_code,
    country,
    status,
    transaction_type,
    amount,
    transaction_dt
)
AS
SELECT
	transactions_tmp_kafka.object_id,
	transactions_tmp_kafka.object_type,
	transactions_tmp_kafka.sent_dttm,
	transactions_tmp_kafka.operation_id,
	transactions_tmp_kafka.account_number_from,
	transactions_tmp_kafka.account_number_to,
	transactions_tmp_kafka.currency_code,
	transactions_tmp_kafka.country,
	transactions_tmp_kafka.status,
	transactions_tmp_kafka.transaction_type,
	transactions_tmp_kafka.amount,
	transactions_tmp_kafka.transaction_dt
FROM MIKEPAFYANDEXRU__STAGING.transactions_tmp_kafka
ORDER BY object_id, sent_dttm
SEGMENTED BY hash(object_id, sent_dttm) ALL NODES KSAFE 1;

-- currencies_tmp_kafka
DROP TABLE IF EXISTS MIKEPAFYANDEXRU__STAGING.currencies_tmp_kafka;
CREATE TABLE MIKEPAFYANDEXRU__STAGING.currencies_tmp_kafka
(
	object_id 	 	   uuid   	   	 NOT NULL,
	object_type  	   varchar(20) 	 NOT NULL,
	sent_dttm    	   timestamp   	 NOT NULL,
	currency_code	   int 		     NOT NULL,
	currency_code_with int 		     NOT NULL,
	date_update		   date	         NOT NULL,
	currency_with_div  numeric(19,2) NOT NULL,

	CONSTRAINT unique_object_id_type UNIQUE(object_id, object_type) ENABLED,
	CONSTRAINT is_transaction CHECK(object_type = 'CURRENCY') ENABLED
)
PARTITION BY sent_dttm::date
GROUP BY calendar_hierarchy_day(sent_dttm::date, 2, 3);

COMMENT ON COLUMN MIKEPAFYANDEXRU__STAGING.currencies_tmp_kafka.object_id   	   IS 'идентификатор объекта в событии';
COMMENT ON COLUMN MIKEPAFYANDEXRU__STAGING.currencies_tmp_kafka.object_type 	   IS 'тип объекта';
COMMENT ON COLUMN MIKEPAFYANDEXRU__STAGING.currencies_tmp_kafka.sent_dttm   	   IS 'дата и время отправки сообщения';
COMMENT ON COLUMN MIKEPAFYANDEXRU__STAGING.currencies_tmp_kafka.date_update 	   IS 'дата обновления курса валют';
COMMENT ON COLUMN MIKEPAFYANDEXRU__STAGING.currencies_tmp_kafka.currency_code 	   IS 'трёхзначный код валюты транзакции';
COMMENT ON COLUMN MIKEPAFYANDEXRU__STAGING.currencies_tmp_kafka.currency_code_with IS 'отношение другой валюты к валюте трёхзначного кода';
COMMENT ON COLUMN MIKEPAFYANDEXRU__STAGING.currencies_tmp_kafka.currency_with_div  IS 'значение отношения единицы одной валюты к единице валюты транзакции';

CREATE PROJECTION MIKEPAFYANDEXRU__STAGING.currencies_tmp_kafka
(
    object_id,
    object_type,
    sent_dttm,
    currency_code,
    currency_code_with,
    date_update,
    currency_with_div
)
AS
SELECT
	currencies_tmp_kafka.object_id,
	currencies_tmp_kafka.object_type,
	currencies_tmp_kafka.sent_dttm,
	currencies_tmp_kafka.currency_code,
	currencies_tmp_kafka.currency_code_with,
	currencies_tmp_kafka.date_update,
	currencies_tmp_kafka.currency_with_div
FROM MIKEPAFYANDEXRU__STAGING.currencies_tmp_kafka
ORDER BY object_id, sent_dttm
SEGMENTED BY hash(object_id, sent_dttm) ALL NODES KSAFE 1;

-- transactions_tmp_s3
DROP TABLE IF EXISTS MIKEPAFYANDEXRU__STAGING.transactions_tmp_s3;
CREATE TABLE MIKEPAFYANDEXRU__STAGING.transactions_tmp_s3
(
	operation_id		uuid		NOT NULL,
	account_number_from int 		NOT NULL,
	account_number_to	int 		NOT NULL,	
	currency_code		int 		NOT NULL,
	country				varchar(20) NOT NULL,
	status				varchar(20) NOT NULL,
	transaction_type	varchar(40) NOT NULL,
	amount				int 		NOT NULL,
	transaction_dt		timestamp	NOT NULL
)
PARTITION BY transaction_dt::date
GROUP BY calendar_hierarchy_day(transaction_dt::date, 2, 3);

COMMENT ON COLUMN MIKEPAFYANDEXRU__STAGING.transactions_tmp_s3.operation_id  	   IS 'id транзакции';
COMMENT ON COLUMN MIKEPAFYANDEXRU__STAGING.transactions_tmp_s3.account_number_from IS 'внутренний бухгалтерский номер счёта транзакции ОТ КОГО';
COMMENT ON COLUMN MIKEPAFYANDEXRU__STAGING.transactions_tmp_s3.account_number_to   IS 'внутренний бухгалтерский номер счёта транзакции К КОМУ';
COMMENT ON COLUMN MIKEPAFYANDEXRU__STAGING.transactions_tmp_s3.currency_code 	   IS 'трёхзначный код валюты страны, из которой идёт транзакция';
COMMENT ON COLUMN MIKEPAFYANDEXRU__STAGING.transactions_tmp_s3.country 			   IS 'страна-источник транзакции';
COMMENT ON COLUMN MIKEPAFYANDEXRU__STAGING.transactions_tmp_s3.status 			   IS 'статус проведения транзакции [queued|in_progress|blocked|done|chargeback]';
COMMENT ON COLUMN MIKEPAFYANDEXRU__STAGING.transactions_tmp_s3.transaction_type    IS 'тип транзакции во внутреннем учёте [authorisation|sbp_incoming|sbp_outgoing|transfer_incoming|transfer_outgoing|c2b_partner_incoming|c2b_partner_outgoing]';
COMMENT ON COLUMN MIKEPAFYANDEXRU__STAGING.transactions_tmp_s3.amount 			   IS 'целочисленная сумма транзакции в минимальной единице валюты страны (копейка, цент, куруш)';
COMMENT ON COLUMN MIKEPAFYANDEXRU__STAGING.transactions_tmp_s3.transaction_dt      IS 'дата и время исполнения транзакции до миллисекунд';   

CREATE PROJECTION MIKEPAFYANDEXRU__STAGING.transactions_tmp_s3
(
    operation_id,
    account_number_from,
    account_number_to,
    currency_code,
    country,
    status,
    transaction_type,
    amount,
    transaction_dt
)
AS
SELECT
	transactions_tmp_s3.operation_id,
	transactions_tmp_s3.account_number_from,
	transactions_tmp_s3.account_number_to,
	transactions_tmp_s3.currency_code,
	transactions_tmp_s3.country,
	transactions_tmp_s3.status,
	transactions_tmp_s3.transaction_type,
	transactions_tmp_s3.amount,
	transactions_tmp_s3.transaction_dt
FROM MIKEPAFYANDEXRU__STAGING.transactions_tmp_s3
ORDER BY operation_id, transaction_dt
SEGMENTED BY hash(operation_id, transaction_dt) ALL NODES KSAFE 1;

-- currencies_tmp_s3
DROP TABLE IF EXISTS MIKEPAFYANDEXRU__STAGING.currencies_tmp_s3;
CREATE TABLE MIKEPAFYANDEXRU__STAGING.currencies_tmp_s3
(
	currency_code	   int 		     NOT NULL,
	currency_code_with int 		     NOT NULL,
	date_update		   date	         NOT NULL,
	currency_with_div  numeric(19,2) NOT NULL
)
PARTITION BY date_update::date
GROUP BY calendar_hierarchy_day(date_update::date, 2, 3);

COMMENT ON COLUMN MIKEPAFYANDEXRU__STAGING.currencies_tmp_s3.currency_code 	 	IS 'трёхзначный код валюты транзакции';
COMMENT ON COLUMN MIKEPAFYANDEXRU__STAGING.currencies_tmp_s3.currency_code_with IS 'отношение другой валюты к валюте трёхзначного кода';
COMMENT ON COLUMN MIKEPAFYANDEXRU__STAGING.currencies_tmp_s3.date_update 		IS 'дата обновления курса валют';
COMMENT ON COLUMN MIKEPAFYANDEXRU__STAGING.currencies_tmp_s3.currency_with_div  IS 'значение отношения единицы одной валюты к единице валюты транзакции';

CREATE PROJECTION MIKEPAFYANDEXRU__STAGING.currencies_tmp_s3 
(
    currency_code,
    currency_code_with,
    date_update,
    currency_with_div
)
AS
SELECT
	currencies_tmp_s3.currency_code,
	currencies_tmp_s3.currency_code_with,
	currencies_tmp_s3.date_update,
	currencies_tmp_s3.currency_with_div
FROM MIKEPAFYANDEXRU__STAGING.currencies_tmp_s3
ORDER BY date_update
SEGMENTED BY hash(date_update) ALL NODES KSAFE 1;

-- resulting transactions
DROP TABLE IF EXISTS MIKEPAFYANDEXRU__STAGING.transactions;
CREATE TABLE MIKEPAFYANDEXRU__STAGING.transactions
(
	operation_id		uuid		NOT NULL,
	account_number_from int 		NOT NULL,
	account_number_to	int 		NOT NULL,	
	currency_code		int 		NOT NULL,
	country				varchar(20) NOT NULL,
	status				varchar(20) NOT NULL,
	transaction_type	varchar(40) NOT NULL,
	amount				int 		NOT NULL,
	transaction_dt		timestamp	NOT NULL,
	load_src			varchar(20) NOT NULL,

	CONSTRAINT unique_operation_id_transaction_dt UNIQUE(operation_id, transaction_dt) ENABLED
)
PARTITION BY transaction_dt::date
GROUP BY calendar_hierarchy_day(transaction_dt::date, 2, 3);

COMMENT ON COLUMN MIKEPAFYANDEXRU__STAGING.transactions.operation_id  	    IS 'id транзакции';
COMMENT ON COLUMN MIKEPAFYANDEXRU__STAGING.transactions.account_number_from IS 'внутренний бухгалтерский номер счёта транзакции ОТ КОГО';
COMMENT ON COLUMN MIKEPAFYANDEXRU__STAGING.transactions.account_number_to   IS 'внутренний бухгалтерский номер счёта транзакции К КОМУ';
COMMENT ON COLUMN MIKEPAFYANDEXRU__STAGING.transactions.currency_code 	    IS 'трёхзначный код валюты страны, из которой идёт транзакция';
COMMENT ON COLUMN MIKEPAFYANDEXRU__STAGING.transactions.country 			IS 'страна-источник транзакции';
COMMENT ON COLUMN MIKEPAFYANDEXRU__STAGING.transactions.status 			    IS 'статус проведения транзакции [queued|in_progress|blocked|done|chargeback]';
COMMENT ON COLUMN MIKEPAFYANDEXRU__STAGING.transactions.transaction_type 	IS 'тип транзакции во внутреннем учёте [authorisation|sbp_incoming|sbp_outgoing|transfer_incoming|transfer_outgoing|c2b_partner_incoming|c2b_partner_outgoing]';
COMMENT ON COLUMN MIKEPAFYANDEXRU__STAGING.transactions.amount 			    IS 'целочисленная сумма транзакции в минимальной единице валюты страны (копейка, цент, куруш)';
COMMENT ON COLUMN MIKEPAFYANDEXRU__STAGING.transactions.transaction_dt      IS 'дата и время исполнения транзакции до миллисекунд';   

CREATE PROJECTION MIKEPAFYANDEXRU__STAGING.transactions
(
    operation_id,
    account_number_from,
    account_number_to,
    currency_code,
    country,
    status,
    transaction_type,
    amount,
    transaction_dt,
    load_src
)
AS
SELECT
	transactions.operation_id,
    transactions.account_number_from,
    transactions.account_number_to,
    transactions.currency_code,
    transactions.country,
    transactions.status,
    transactions.transaction_type,
    transactions.amount,
    transactions.transaction_dt,
    transactions.load_src
FROM MIKEPAFYANDEXRU__STAGING.transactions
ORDER BY operation_id, transaction_dt
SEGMENTED BY hash(operation_id, transaction_dt) ALL NODES KSAFE 1;

-- resulting currencies
DROP TABLE IF EXISTS MIKEPAFYANDEXRU__STAGING.currencies;
CREATE TABLE MIKEPAFYANDEXRU__STAGING.currencies
(
	currency_code	   int 		     NOT NULL,
	currency_code_with int 		     NOT NULL,
	date_update		   date	         NOT NULL,
	currency_with_div  numeric(19,2) NOT NULL,
	load_src		   varchar(20)   NOT NULL,

	CONSTRAINT unique_date_update_currency_code UNIQUE(currency_code, currency_code_with, date_update) ENABLED
)
PARTITION BY date_update::date
GROUP BY calendar_hierarchy_day(date_update::date, 2, 3);

COMMENT ON COLUMN MIKEPAFYANDEXRU__STAGING.currencies.currency_code 	 IS 'трёхзначный код валюты транзакции';
COMMENT ON COLUMN MIKEPAFYANDEXRU__STAGING.currencies.currency_code_with IS 'отношение другой валюты к валюте трёхзначного кода';
COMMENT ON COLUMN MIKEPAFYANDEXRU__STAGING.currencies.date_update 		 IS 'дата обновления курса валют';
COMMENT ON COLUMN MIKEPAFYANDEXRU__STAGING.currencies.currency_with_div  IS 'значение отношения единицы одной валюты к единице валюты транзакции';

CREATE PROJECTION MIKEPAFYANDEXRU__STAGING.currencies
(
 currency_code,
 currency_code_with,
 date_update,
 currency_with_div,
 load_src
)
AS
 SELECT
 	currencies.currency_code,
	currencies.currency_code_with,
	currencies.date_update,
	currencies.currency_with_div,
	currencies.load_src
 FROM MIKEPAFYANDEXRU__STAGING.currencies
ORDER BY currency_code, date_update
SEGMENTED BY hash(date_update, currency_code) ALL NODES KSAFE 1;