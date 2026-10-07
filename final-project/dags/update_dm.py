from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.sensors.external_task_sensor import ExternalTaskSensor
from airflow.providers.postgres.hooks.postgres import PostgresHook
#from airflow.contrib.hooks.vertica_hook import VerticaHook
import logging, datetime, vertica_python

postgres_conn_id = 'pg_conn'

#поскольку провайдер для vertica не установлен, задаю параметры соединения тут
conn_info = {'host': '51.250.75.20', 
             'port': '5433',
             'user': 'OARTEMOV1976YANDEXRU',       
             'password': '0312hjDnuiLz0FG',
             'database': 'dwh',
             'autocommit': True
}

temp_file_path = '/tmp'
args = {
    'owner': 'oartemov',
    'email': ['oartemov1976@yandex.ru'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 0
}
log = logging.getLogger(__name__)

def update_dm(date_from, date_to):
    date_from = date_from.strftime('%Y-%m-%d')
    date_to = date_to.strftime('%Y-%m-%d')

    # по постановке задачи непонятно как считать уникальных клиентов, поэтому делаю на свое усмотрение
    with vertica_python.connect(**conn_info) as conn:
        cur = conn.cursor()
        cur.execute(f'DELETE FROM OARTEMOV1976YANDEXRU__DWH.global_metrics WHERE date_update BETWEEN \'{date_from}\' AND \'{date_to}\'')
        sql = f'''insert into OARTEMOV1976YANDEXRU__DWH.global_metrics
        select t.transaction_dt::date as date_update
	          ,t.currency_code as currency_from 
              ,sum(abs(t.amount)*case when t.currency_code = 420 then 1 else c.currency_with_div end) as amount_total 
	          ,count(*) as cnt_transactions 
	          ,count(*)/count(distinct case when right(t.transaction_type, 8) = 'outgoing' then t.account_number_from else t.account_number_to end) as avg_transactions_per_account
              -- Если транзакция исходящая, наш клиент - account_number_from, 
              -- если входящая - account_number_to
	          ,count(distinct case when right(t.transaction_type, 8) = 'outgoing' then t.account_number_from else t.account_number_to end) as cnt_accounts_make_transactions
        from OARTEMOV1976YANDEXRU__STAGING.transactions t
        left join OARTEMOV1976YANDEXRU__STAGING.currencies c on c.currency_code = t.currency_code 
                                                    and c.currency_code_with = 420 -- код доллара
                                                    and c.date_update::date = t.transaction_dt::date
        where t.status = 'done' -- берем только транзакции в статусе «транзакция выполнена успешно»
          and t.account_number_from > 0
          and t.account_number_to > 0
          and t.transaction_dt >= \'{date_from}\'
          and t.transaction_dt < \'{date_to}\'::date+1
          -- Берем только переводы
          and t.transaction_type in ('c2a_incoming',
                                     'c2b_partner_incoming',
                                     'sbp_incoming',
                                     'sbp_outgoing',
                                     'transfer_incoming',
                                     'transfer_outgoing')
        group by t.transaction_dt::date
	            ,t.currency_code 
        '''
        log.info(sql)
        cur.execute(sql)

with DAG(
        'update_dm',
        default_args=args,
        description='DAG for updating global_metrics datamart',
        catchup=True,
        start_date=datetime.datetime.today() - datetime.timedelta(days=1),
        #end_date=datetime.datetime.today() + datetime.timedelta(days=1),
        schedule_interval='@daily'
) as dag:    

    #я бы сделал все в одном даге, но по условиям задачи загрузка данных и обновление витрины должны
    #быть в разных дагах, поэтому использую ExternalTaskSensor чтобы дождаться загрузки данных в стейджинг
    wait_for_staging = ExternalTaskSensor(
    task_id = 'wait_for_staging',
    external_dag_id = 'update_staging',
    external_task_id = 'get_transactions',
    start_date = datetime.datetime.today() - datetime.timedelta(days=1),
    execution_delta =  datetime.timedelta(days=1),
    timeout = 3600,
    )    

    update_dm = PythonOperator(
        task_id='update_dm',
        python_callable=update_dm,
        op_kwargs={'date_from': datetime.datetime.today() - datetime.timedelta(days=1),
                   'date_to': datetime.datetime.today() - datetime.timedelta(days=1)
                  }
        )

    wait_for_staging >> update_dm