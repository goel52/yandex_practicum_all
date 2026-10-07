from pyspark.sql import SparkSession

spark = SparkSession \
    .builder \
    .config("spark.driver.cores", "2") \
    .config("spark.driver.memory", "1g") \
    .appName("My first session") \
    .getOrCreate()
