CREATE SCHEMA IF NOT EXISTS STV2024021923__DWH;

CREATE TABLE STV2024021923__DWH.global_metrics (
    date_update DATE,
    currency_from VARCHAR(3),
    amount_total FLOAT,
    cnt_transactions INT,
    avg_transactions_per_account FLOAT,
    cnt_accounts_make_transactions INT
);