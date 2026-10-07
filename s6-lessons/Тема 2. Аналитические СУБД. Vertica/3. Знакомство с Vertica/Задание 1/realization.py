import vertica_python

conn_info = {'host': 'vertica.data-engineer.education-services.ru',
             'port': '5433',
             'user': 'vt260202c92750',
             'password': '68f7a57a039a42c784b374907b9a22aa',
             'database': 'dwh',
             # Вначале он нам понадобится, а дальше — решите позже сами
            'autocommit': True
}

def try_select(conn_info=conn_info):
    # И рекомендуем использовать соединение вот так
    with vertica_python.connect(**conn_info) as conn:
        cur = conn.cursor()
        cur.execute("select 1 as a1;")
        res = cur.fetchall()
        return res