from pyspark.sql import SparkSession
spark = SparkSession.builder.appName('test_name').config('spark.jars.packages', 'org.postgresql:postgresql:42.4.0').getOrCreate()
db_pass = 'de-master-password'
df = spark.read.format('jdbc').option('url', 'jdbc:postgresql://fixture/de').option('driver', 'org.postgresql.Driver').option('dbtable', 'public.marketing_companies').option('user', 'fixture').option('password', 'fixture').load()
df.count()
