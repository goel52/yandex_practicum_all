import vertica_python
from airflow.hooks.base_hook import BaseHook

def fetch_exchange_rates(execution_date, **kwargs):
    vertica_conn = BaseHook.get_connection('vertica')
    
    vertica_conn_info = {
        'host': vertica_conn.host,
        'port': vertica_conn.port,
        'user': vertica_conn.login,
        'password': vertica_conn.password,
        'database': vertica_conn.schema
    }
    
    query = """
        SELECT currency_code, currency_code_with, currency_code_div
        FROM STV2024021923__STAGING.currencies
        WHERE date_update = %s
    """
    with vertica_python.connect(**vertica_conn_info) as connection:
        cur = connection.cursor()
        cur.execute(query, (execution_date,))
        exchange_rates = cur.fetchall()
    return exchange_rates

def update_global_metrics(execution_date, **kwargs):
    vertica_conn = BaseHook.get_connection('vertica')
    
    vertica_conn_info = {
        'host': vertica_conn.host,
        'port': vertica_conn.port,
        'user': vertica_conn.login,
        'password': vertica_conn.password,
        'database': vertica_conn.schema
    }
    
    exchange_rates = kwargs['task_instance'].xcom_pull(task_ids='fetch_exchange_rates')

    query = """
        INSERT INTO STV2024021923__DWH.global_metrics
        SELECT 
            t.transaction_dt::date AS date_update,
            t.currency_code AS currency_from,
            SUM(t.amount * e.currency_code_div) AS amount_total,
            COUNT(*) AS cnt_transactions,
            AVG(t.amount) AS avg_transactions_per_account,
            COUNT(DISTINCT t.account_number_from) AS cnt_accounts_make_transactions
        FROM STV2024021923__STAGING.transactions t
        LEFT JOIN (
            SELECT currency_code, currency_code_div
            FROM STV2024021923__STAGING.currencies
            WHERE currency_code_with = 'USD' AND date_update = %s
        ) e
        ON t.currency_code = e.currency_code
        WHERE t.transaction_dt::date = %s AND t.account_number_from >= 0
        GROUP BY t.transaction_dt::date, t.currency_code
    """
    with vertica_python.connect(**vertica_conn_info) as connection:
        cur = connection.cursor()
        cur.execute(query, (execution_date, execution_date))
        connection.commit()