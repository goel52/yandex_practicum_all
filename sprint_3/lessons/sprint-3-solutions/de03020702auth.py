 import psycopg2

conn = psycopg2.connect("dbname='de' port='5432' user='jovyan' host='localhost' password='jovyan'")

cur = conn.cursor()

print(cur)

cur.close()

conn.close()