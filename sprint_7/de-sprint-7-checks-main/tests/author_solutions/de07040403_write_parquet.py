import pyspark
from pyspark.sql import SparkSession

spark = SparkSession.builder \
                    .master("yarn") \
                    .appName("Learning DataFrames") \
                    .getOrCreate()

df = spark.read.parquet("/user/master/data/snapshots/channels/actual")

df.write \
        .partitionBy("channel_type") \
        .mode("append") \
        .parquet("/user/*Имя вашей папки*/analytics/test")
