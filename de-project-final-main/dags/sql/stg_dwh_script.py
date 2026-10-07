import psycopg2
from airflow.hooks.base_hook import BaseHook
import vertica_python

def load_to_stg(execution_date, **kwargs):
    pg_conn = BaseHook.get_connection('database')
    pg_conn_info = {
        'host': pg_conn.host,
        'port': pg_conn.port,
        'user': pg_conn.login,
        'password': pg_conn.password,
        'dbname': pg_conn.schema
    }
    
    with psycopg2.connect(**pg_conn_info) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM public.transactions WHERE transaction_dt::date = %s", (execution_date,))
        transactions_data = cursor.fetchall()
        
        cursor.execute("SELECT * FROM public.currencies WHERE date_update::date = %s", (execution_date,))
        currencies_data = cursor.fetchall()

    vertica_conn = BaseHook.get_connection('vertica')
    vertica_conn_info = {
        'host': vertica_conn.host,
        'port': vertica_conn.port,
        'user': vertica_conn.login,
        'password': vertica_conn.password,
        'database': vertica_conn.schema
    }

    with vertica_python.connect(**vertica_conn_info) as connection:
        cur = connection.cursor()
        for row in transactions_data:
            cur.execute("INSERT INTO STV2024021923__STAGING.transactions VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                        row)
        for row in currencies_data:
            cur.execute("INSERT INTO STV2024021923__STAGING.currencies VALUES (%s, %s, %s, %s)",
                        row)
        connection.commit()

def load_to_dwh(execution_date, **kwargs):
    vertica_conn = BaseHook.get_connection('vertica')
    vertica_conn_info = {
        'host': vertica_conn.host,
        'port': vertica_conn.port,
        'user': vertica_conn.login,
        'password': vertica_conn.password,
        'database': vertica_conn.schema
    }

    query = """
        INSERT INTO STV2024021923__DWH.transactions (SELECT * FROM STV2024021923__STAGING.transactions WHERE transaction_dt::date = %s);
        INSERT INTO STV2024021923__DWH.currencies (SELECT * FROM STV2024021923__STAGING.currencies WHERE date_update::date = %s);
    """
    with vertica_python.connect(**vertica_conn_info) as connection:
        cur = connection.cursor()
        cur.execute(query, (execution_date, execution_date))
        connection.commit()