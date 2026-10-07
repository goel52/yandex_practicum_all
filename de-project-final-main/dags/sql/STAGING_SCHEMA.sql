CREATE SCHEMA IF NOT EXISTS STV2024021923__STAGING;

CREATE TABLE STV2024021923__STAGING.transactions (
    operation_id UUID,
    account_number_from VARCHAR(50),
    account_number_to VARCHAR(50),
    currency_code VARCHAR(3),
    country VARCHAR(50),
    status VARCHAR(20),
    transaction_type VARCHAR(50),
    amount INT,
    transaction_dt TIMESTAMP
);

CREATE TABLE STV2024021923__STAGING.currencies (
    date_update TIMESTAMP,
    currency_code VARCHAR(3),
    currency_code_with VARCHAR(3),
    currency_code_div FLOAT
);