-- HUBS
-- h_operations
DROP TABLE IF EXISTS MIKEPAFYANDEXRU__DWH.h_operations CASCADE;
CREATE TABLE MIKEPAFYANDEXRU__DWH.h_operations
(
    hk_operation_pk bigint PRIMARY KEY,
    operation_id    uuid,
    transaction_dt  datetime,
    load_dt         datetime,
    load_src        varchar(20)
)
PARTITION BY load_dt::date
GROUP BY calendar_hierarchy_day(load_dt::date, 3, 2);

COMMENT ON COLUMN MIKEPAFYANDEXRU__DWH.h_operations.hk_operation_pk IS 'первичный хэш-ключ';
COMMENT ON COLUMN MIKEPAFYANDEXRU__DWH.h_operations.operation_id    IS 'id транзакции';
COMMENT ON COLUMN MIKEPAFYANDEXRU__DWH.h_operations.transaction_dt  IS 'дата и время исполнения транзакции';
COMMENT ON COLUMN MIKEPAFYANDEXRU__DWH.h_operations.load_dt         IS 'время загрузки';
COMMENT ON COLUMN MIKEPAFYANDEXRU__DWH.h_operations.load_src        IS 'источник загрузки';

CREATE PROJECTION MIKEPAFYANDEXRU__DWH.h_operations
(
    hk_operation_pk,
    operation_id,
    transaction_dt,
    load_dt,
    load_src
)
AS
SELECT
    h_operations.hk_operation_pk,
    h_operations.operation_id,
    h_operations.transaction_dt,
    h_operations.load_dt,
    h_operations.load_src
FROM MIKEPAFYANDEXRU__DWH.h_operations
ORDER BY load_dt
SEGMENTED BY hk_operation_pk ALL NODES KSAFE 1;

-- h_currencies
DROP TABLE IF EXISTS MIKEPAFYANDEXRU__DWH.h_currencies CASCADE;
CREATE TABLE MIKEPAFYANDEXRU__DWH.h_currencies
(
    hk_currency_pk bigint PRIMARY KEY,
    currency_code  int,
    date_update    datetime,
    load_dt        datetime,
    load_src       varchar(20)
)
PARTITION BY load_dt::date
GROUP BY calendar_hierarchy_day(load_dt::date, 3, 2);

COMMENT ON COLUMN MIKEPAFYANDEXRU__DWH.h_currencies.hk_currency_pk IS 'первичный хэш-ключ';
COMMENT ON COLUMN MIKEPAFYANDEXRU__DWH.h_currencies.currency_code  IS 'трёхзначный код валюты страны, из которой идёт транзакция';
COMMENT ON COLUMN MIKEPAFYANDEXRU__DWH.h_currencies.date_update    IS 'дата обновления курса валют';
COMMENT ON COLUMN MIKEPAFYANDEXRU__DWH.h_currencies.load_dt        IS 'время загрузки';
COMMENT ON COLUMN MIKEPAFYANDEXRU__DWH.h_currencies.load_src       IS 'источник загрузки';

CREATE PROJECTION MIKEPAFYANDEXRU__DWH.h_currencies
(
    hk_currency_pk,
    currency_code,
    date_update,
    load_dt,
    load_src
)
AS
SELECT
    h_currencies.hk_currency_pk,
    h_currencies.currency_code,
    h_currencies.date_update,
    h_currencies.load_dt,
    h_currencies.load_src
FROM MIKEPAFYANDEXRU__DWH.h_currencies
ORDER BY load_dt
SEGMENTED BY hk_currency_pk ALL NODES KSAFE 1;

-- LINKS
-- l_operation_currency
DROP TABLE IF EXISTS MIKEPAFYANDEXRU__DWH.l_operation_currency;
CREATE TABLE MIKEPAFYANDEXRU__DWH.l_operation_currency
(
    hk_operation_currency_pk bigint PRIMARY KEY,
    hk_operation_pk          bigint NOT NULL CONSTRAINT fk_operation_currency_operation_pk
                                        REFERENCES MIKEPAFYANDEXRU__DWH.h_operations(hk_operation_pk), 
    hk_currency_pk           bigint NOT NULL CONSTRAINT fk_operation_currency_currency_pk
                                        REFERENCES MIKEPAFYANDEXRU__DWH.h_currencies(hk_currency_pk),
    load_dt                  datetime,
    load_src                 varchar(20)
)
PARTITION BY load_dt::date
GROUP BY calendar_hierarchy_day(load_dt::date, 3, 2);

COMMENT ON COLUMN MIKEPAFYANDEXRU__DWH.l_operation_currency.hk_operation_currency_pk IS 'первичный хэш-ключ';
COMMENT ON COLUMN MIKEPAFYANDEXRU__DWH.l_operation_currency.hk_operation_pk          IS 'хэш-ключ из таблицы операций';
COMMENT ON COLUMN MIKEPAFYANDEXRU__DWH.l_operation_currency.hk_currency_pk           IS 'хэш-ключ из таблицы валют';
COMMENT ON COLUMN MIKEPAFYANDEXRU__DWH.l_operation_currency.load_dt                  IS 'время загрузки';
COMMENT ON COLUMN MIKEPAFYANDEXRU__DWH.l_operation_currency.load_src                 IS 'источники загрузки';

CREATE PROJECTION MIKEPAFYANDEXRU__DWH.l_operation_currency
(
    hk_operation_currency_pk,
    hk_operation_pk,
    hk_currency_pk,
    load_dt,
    load_src
)
AS
SELECT
    l_operation_currency.hk_operation_currency_pk,
    l_operation_currency.hk_operation_pk,
    l_operation_currency.hk_currency_pk,
    l_operation_currency.load_dt,
    l_operation_currency.load_src
FROM MIKEPAFYANDEXRU__DWH.l_operation_currency
ORDER BY load_dt
SEGMENTED BY hk_operation_currency_pk ALL NODES KSAFE 1;

-- SATELLITES
-- s_operation_details
DROP TABLE IF EXISTS MIKEPAFYANDEXRU__DWH.s_operation_details;
CREATE TABLE MIKEPAFYANDEXRU__DWH.s_operation_details
(
    hk_operation_pk  bigint NOT NULL CONSTRAINT fk_operation_details_operation_pk
                                REFERENCES MIKEPAFYANDEXRU__DWH.h_operations(hk_operation_pk),
    account_number_from     int,
    account_number_to       int,
    country                 varchar(20),
    status                  varchar(20),
    transaction_type        varchar(40),
    load_dt                 datetime,
    load_src                varchar(20)
)
PARTITION BY load_dt::date
GROUP BY calendar_hierarchy_day(load_dt::date, 3, 2);

COMMENT ON COLUMN MIKEPAFYANDEXRU__DWH.s_operation_details.hk_operation_pk     IS 'первичный хэш-ключ';
COMMENT ON COLUMN MIKEPAFYANDEXRU__DWH.s_operation_details.account_number_from IS 'внутренний бухгалтерский номер счёта транзакции ОТ КОГО';
COMMENT ON COLUMN MIKEPAFYANDEXRU__DWH.s_operation_details.account_number_to   IS 'внутренний бухгалтерский номер счёта транзакции К КОМУ';
COMMENT ON COLUMN MIKEPAFYANDEXRU__DWH.s_operation_details.country             IS 'страна-источник транзакции';
COMMENT ON COLUMN MIKEPAFYANDEXRU__DWH.s_operation_details.status              IS 'статус проведения транзакции [queued|in_progress|blocked|done|chargeback]';
COMMENT ON COLUMN MIKEPAFYANDEXRU__DWH.s_operation_details.transaction_type    IS 'тип транзакции во внутреннем учёте [authorisation|sbp_incoming|sbp_outgoing|transfer_incoming|transfer_outgoing|c2b_partner_incoming|c2b_partner_outgoing]';
COMMENT ON COLUMN MIKEPAFYANDEXRU__DWH.s_operation_details.load_dt             IS 'время загрузки';
COMMENT ON COLUMN MIKEPAFYANDEXRU__DWH.s_operation_details.load_src            IS 'источник загрузки';

CREATE PROJECTION MIKEPAFYANDEXRU__DWH.s_operation_details
(
    hk_operation_pk,
    account_number_from,
    account_number_to,
    country,
    status,
    transaction_type,
    load_dt,
    load_src
)
AS
SELECT
    s_operation_details.hk_operation_pk,
    s_operation_details.account_number_from,
    s_operation_details.account_number_to,
    s_operation_details.country,
    s_operation_details.status,
    s_operation_details.transaction_type,
    s_operation_details.load_dt,
    s_operation_details.load_src
FROM MIKEPAFYANDEXRU__DWH.s_operation_details
ORDER BY load_dt
SEGMENTED BY hk_operation_pk ALL NODES KSAFE 1;

-- s_operation_amounts
DROP TABLE IF EXISTS MIKEPAFYANDEXRU__DWH.s_operation_amounts;
CREATE TABLE MIKEPAFYANDEXRU__DWH.s_operation_amounts
(
    hk_operation_pk bigint NOT NULL CONSTRAINT fk_operation_amounts_operation_pk
                                REFERENCES MIKEPAFYANDEXRU__DWH.h_operations(hk_operation_pk),
    currency_code   int,
    amount          int,
    load_dt         datetime,
    load_src        varchar(20)
)
PARTITION BY load_dt::date
GROUP BY calendar_hierarchy_day(load_dt::date, 3, 2);

COMMENT ON COLUMN MIKEPAFYANDEXRU__DWH.s_operation_amounts.hk_operation_pk IS 'первичный хэш-ключ';
COMMENT ON COLUMN MIKEPAFYANDEXRU__DWH.s_operation_amounts.amount          IS 'целочисленная сумма транзакции в минимальной единице валюты страны (копейка, цент, куруш)';
COMMENT ON COLUMN MIKEPAFYANDEXRU__DWH.s_operation_amounts.load_dt         IS 'время загрузки';
COMMENT ON COLUMN MIKEPAFYANDEXRU__DWH.s_operation_amounts.load_src        IS 'источник загрузки';

CREATE PROJECTION MIKEPAFYANDEXRU__DWH.s_operation_amounts
(
    hk_operation_pk,
    currency_code,
    amount,
    load_dt,
    load_src
)
AS
SELECT
    s_operation_amounts.hk_operation_pk,
    s_operation_amounts.currency_code,
    s_operation_amounts.amount,
    s_operation_amounts.load_dt,
    s_operation_amounts.load_src
FROM MIKEPAFYANDEXRU__DWH.s_operation_amounts
ORDER BY load_dt
SEGMENTED BY hk_operation_pk ALL NODES KSAFE 1;

-- s_currency_details
DROP TABLE IF EXISTS MIKEPAFYANDEXRU__DWH.s_currency_details;
CREATE TABLE MIKEPAFYANDEXRU__DWH.s_currency_details
(
    hk_currency_pk        bigint NOT NULL CONSTRAINT fk_operation_currency_details_currency_pk
                                        REFERENCES MIKEPAFYANDEXRU__DWH.h_currencies(hk_currency_pk),
    currency_code_with    int,
    currency_country      varchar(20),
    currency_country_with varchar(20),
    currency_with_div     numeric(19,2),
    load_dt               datetime,
    load_src              varchar(20)
)
PARTITION BY load_dt::date
GROUP BY calendar_hierarchy_day(load_dt::date, 3, 2);

COMMENT ON COLUMN MIKEPAFYANDEXRU__DWH.s_currency_details.hk_currency_pk        IS 'первичный хэш-ключ';
COMMENT ON COLUMN MIKEPAFYANDEXRU__DWH.s_currency_details.currency_code_with    IS 'отношение другой валюты к валюте трёхзначного кода';
COMMENT ON COLUMN MIKEPAFYANDEXRU__DWH.s_currency_details.currency_country      IS 'страна исходящей валюты';
COMMENT ON COLUMN MIKEPAFYANDEXRU__DWH.s_currency_details.currency_country_with IS 'страна входящей валюты';
COMMENT ON COLUMN MIKEPAFYANDEXRU__DWH.s_currency_details.currency_with_div     IS 'значение отношения единицы одной валюты к единице валюты транзакции';
COMMENT ON COLUMN MIKEPAFYANDEXRU__DWH.s_currency_details.load_dt               IS 'время загрузки';
COMMENT ON COLUMN MIKEPAFYANDEXRU__DWH.s_currency_details.load_src              IS 'источник загрузки';

CREATE PROJECTION MIKEPAFYANDEXRU__DWH.s_currency_details 
(
    hk_currency_pk,
    currency_code_with,
    currency_country,
    currency_country_with,
    currency_with_div,
    load_dt,
    load_src
)
AS
SELECT
    s_currency_details.hk_currency_pk,
    s_currency_details.currency_code_with,
    s_currency_details.currency_country,
    s_currency_details.currency_country_with,
    s_currency_details.currency_with_div,
    s_currency_details.load_dt,
    s_currency_details.load_src
FROM MIKEPAFYANDEXRU__DWH.s_currency_details
ORDER BY load_dt
SEGMENTED BY hk_currency_pk ALL NODES KSAFE 1;