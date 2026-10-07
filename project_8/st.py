from datetime import datetime
from time import sleep

from pyspark.sql import SparkSession, DataFrame
from pyspark.sql import functions as f
from pyspark.sql.types import StructType, StructField, DoubleType, StringType, TimestampType, IntegerType, LongType

TOPIC_NAME_IN = 'student.topic.cohort11.aleksanderk_in'
TOPIC_NAME_91 = 'student.topic.cohort11.aleksanderk_out'


def spark_init(test_name) -> SparkSession:
    spark_jars_packages = ",".join(
        [
            "org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0",
            "org.postgresql:postgresql:42.4.0",
        ]
    )

    spark = (
        SparkSession.builder.appName(test_name)
            .config("spark.sql.session.timeZone", "UTC")
            .config("spark.jars.packages", spark_jars_packages)
            .getOrCreate()
    )

    return spark


def read_client_stream(spark: SparkSession) -> DataFrame:
    schema = StructType([
        StructField("restaurant_id", StringType()),
        StructField("adv_campaign_id", StringType()),
        StructField("adv_campaign_content", StringType()),
        StructField("adv_campaign_owner", StringType()),
        StructField("adv_campaign_owner_contact", StringType()),
        StructField("adv_campaign_datetime_start", LongType()),
        StructField("adv_campaign_datetime_end", LongType()),
        StructField("client_id", StringType()),
        StructField("datetime_created", LongType()),
        StructField("trigger_datetime_created", LongType())
    ])
    df = (spark.readStream.format('kafka') \
          .option('kafka.bootstrap.servers', 'rc1b-2erh7b35n4j4v869.mdb.yandexcloud.net:9091') \
          .option('kafka.security.protocol', 'SASL_SSL') \
          .option('kafka.sasl.mechanism', 'SCRAM-SHA-512') \
          .option('kafka.sasl.jaas.config',
                  'org.apache.kafka.common.security.scram.ScramLoginModule required username=\"de-student\" password=\"ltcneltyn\";') \
          .option("subscribe", "student.topic.cohort11.aleksanderk_in") \
          .load() \
          .withColumn('value', f.col('value').cast(StringType()))
          .withColumn('event', f.from_json(f.col('value'), schema))
          .selectExpr('event.*')
          .withColumn('restaurant_id',
                      f.col('restaurant_id').cast(IntegerType()))
          .withColumn('adv_campaign_id',
                      f.col('adv_campaign_id').cast(IntegerType()))
          .withColumn('client_id',
                      f.col('client_id').cast(IntegerType()))
          .withColumn('adv_campaign_datetime_start',
                      f.from_unixtime(f.col('adv_campaign_datetime_start'), "yyyy-MM-dd' 'HH:mm:ss.SSS").cast(
                          TimestampType()))
          .withColumn('adv_campaign_datetime_end',
                      f.from_unixtime(f.col('adv_campaign_datetime_end'), "yyyy-MM-dd' 'HH:mm:ss.SSS").cast(
                          TimestampType()))
          .withColumn('datetime_created',
                      f.from_unixtime(f.col('datetime_created'), "yyyy-MM-dd' 'HH:mm:ss.SSS").cast(TimestampType()))
          .withColumn('trigger_datetime_created',
                      f.from_unixtime(f.col('trigger_datetime_created'), "yyyy-MM-dd' 'HH:mm:ss.SSS").cast(
                          TimestampType()))
          .dropDuplicates(["restaurant_id",
                           "adv_campaign_id",
                           "adv_campaign_content",
                           "adv_campaign_owner",
                           "adv_campaign_owner_contact",
                           "adv_campaign_datetime_start",
                           "adv_campaign_datetime_end",
                           "client_id"])
          .withWatermark('datetime_created', '10 minutes')
          )

    return df


def join(user_df, marketing_df) -> DataFrame:
    return user_df


if __name__ == "__main__":
    spark = spark_init('join stream')
    client_stream = read_client_stream(spark)

    query = (client_stream
             .writeStream
             .outputMode("append")
             .format("kafka")
             .option('kafka.bootstrap.servers', 'rc1b-2erh7b35n4j4v869.mdb.yandexcloud.net:9091') \
             .option('kafka.security.protocol', 'SASL_SSL') \
             .option('kafka.sasl.mechanism', 'SCRAM-SHA-512') \
             .option('kafka.sasl.jaas.config',
                     'org.apache.kafka.common.security.scram.ScramLoginModule required username=\"de-student\" password=\"ltcneltyn\";') \
             .option("checkpointLocation", "checkpoint_dir")
             .option("topic", TOPIC_NAME_91)
             .trigger(processingTime="15 seconds")
             .option("truncate", False)
             .start())

    while query.isActive:
        print(f"query information: runId={query.runId}, "
              f"status is {query.status}, "
              f"recent progress={query.recentProgress}")
        sleep(30)

    query.awaitTermination()



