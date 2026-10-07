import vertica_python

conn_info = {'host': 'vertica.tgcloudenv.ru',
             'port': 5433,
             'user': 'testuser1',       
             'password': 'passtestuser1',
             'database': 'dwh',
             'autocommit': True
}

def try_select(conn_info=conn_info):
    with vertica_python.connect(**conn_info) as conn:
        cur = conn.cursor()

        cur.execute("Select 1 as a1;")
        res = cur.fetchall()
    return res