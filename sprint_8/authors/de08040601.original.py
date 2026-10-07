from pyspark.sql import SparkSession
spark_jars_packages = ','.join(['org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0'])
spark = SparkSession.builder.master('local').appName('test connect to kafka').config('spark.jars.packages', spark_jars_packages).getOrCreate()
df = spark.read.format('kafka').option('kafka.bootstrap.servers', 'fixture:9092').option('kafka.security.protocol', 'SASL_SSL').option('kafka.sasl.mechanism', 'SCRAM-SHA-512').option('kafka.sasl.jaas.config', 'fixture-auth').option('subscribe', 'persist_topic').load()
