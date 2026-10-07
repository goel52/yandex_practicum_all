from pyspark.sql import SparkSession
from pyspark.sql import functions as f
from pyspark.sql.types import StructType, StructField, DoubleType, StringType, TimestampType

spark_jars_packages = ",".join(
    [
        "org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0"
    ]
)

spark = (
    SparkSession.builder
    .master("local")
    .appName('de_s8_th3_les5_ex1')
    .config("spark.jars.packages", spark_jars_packages)
    .getOrCreate()
)

df = (spark.readStream
      .format('kafka')
      .option('kafka.bootstrap.servers', 'rc1b-2erh7b35n4j4v869.mdb.yandexcloud.net:9091')
      .option('kafka.security.protocol', 'SASL_SSL')
      .option('kafka.sasl.mechanism', 'SCRAM-SHA-512')
      .option('kafka.sasl.jaas.config','org.apache.kafka.common.security.scram.ScramLoginModule required username=\"de-student\" password=\"ltcneltyn\";')
      .option("subscribe", "student.topic.cohort39.vladimirsh")
      .option("maxOffsetsPerTrigger", "1000")
      .load())

schema = StructType([
    StructField("client_id", StringType()),
    StructField("timestamp", DoubleType()),
    StructField("lat", DoubleType()),
    StructField("lon", DoubleType())
])




df_for_streaming = (df
    .withColumn('value_str', f.col('value').cast(StringType()))
    .withColumn('data', f.from_json(f.col('value_str'), schema))
    .select(
        f.col('data.client_id'),
        f.from_unixtime(f.col('data.timestamp')).cast(TimestampType()).alias('timestamp'),
        f.col('data.lat'),
        f.col('data.lon')
    )
    .filter(f.col('client_id').isNotNull())
)

query = (df_for_streaming
    .writeStream
    .outputMode("append")
    .format("console")
    .option("truncate", False)
    .option("numRows", 10)
    .start()
)

query.awaitTermination()