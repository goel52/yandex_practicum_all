from datetime import datetime

from pyspark.sql import SparkSession, DataFrame
from pyspark.sql import functions as F
from pyspark.sql.types import StructType, StructField, DoubleType, StringType, TimestampType, IntegerType

# необходимая библиотека с идентификатором в maven
kafka_lib_id = "org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0"

# учебное имя входного топика для автоматической проверки
TOPIC_NAME = "test-3-8-2"

def spark_init(test_name) -> SparkSession:
    return (
    SparkSession.builder
    .master("local")
    .appName(test_name)
    .config("spark.jars.packages", kafka_lib_id)
    .config("spark.jars.repositories", "https://maven.aliyun.com/repository/public")
    .config("spark.sql.session.timeZone", "UTC") # иногда нужно для консистентности timestamp
    .config("spark.driver.host", "localhost") # иногда нужно на локальных машинах, чтобы Spark не пытался резолвить hostname
    .config("spark.ui.enabled", "false") # чтобы не поднимался веб-интерфейс Spark (в headless-среде полезно)
    .getOrCreate()
    )

def read_marketing(spark: SparkSession) -> DataFrame:
    static_df = (spark
    .read
    .format("jdbc")
    .option("url", "jdbc:postgresql://rc1a-fswjkpli01zafgjm.mdb.yandexcloud.net:6432/de")
    .option("driver", "org.postgresql.Driver")
    .option("dbtable", "public.marketing_companies")
    .option("user", "master")
    .option("password", "de-master-password")
    .load())

    return(static_df.select(
        F.col("static_df.id").alias("adv_campaign_id"), # идентификатор акции
        F.col("static_df.name").alias("adv_campaign_name"),# наименование акции
        F.col("static_df.point_lat").alias("adv_campaign_point_lat"), # расположение ресторана/точки широта
        F.col("static_df.point_lon").alias ("adv_campaign_point_lon"), # расположение ресторана/долгота широта
        F.col("static_df.description").alias("adv_campaign_description"), # описание акции
        F.col("static_df.start_time").alias("adv_campaign_start_time"), # время начала акции
        F.col("static_df.end_time").alias("adv_campaign_end_time"), # время конца акции
        F.col("static_df.radius").alias("adv_campaign_radius"), # возможное расстояние до клиента
    ))


def read_client_stream(spark: SparkSession) -> DataFrame:
    df = (spark.readStream
    .format("kafka")
    .option("kafka.bootstrap.servers", "rc1b-2erh7b35n4j4v869.mdb.yandexcloud.net:9091")
    .option("kafka.security.protocol", "SASL_SSL")
    .option("kafka.sasl.mechanism", "SCRAM-SHA-512")
    .option("kafka.sasl.jaas.config", 'org.apache.kafka.common.security.scram.ScramLoginModule required username=\"de-student\" password=\"ltcneltyn\";')
    .option("subscribe", TOPIC_NAME)
    .option("startingOffsets", "earliest") # с чего начать чтение
    .option("failOnDataLoss", "false") # что делать при потере данных
    .load()
    )

    incoming_message_schema = StructType([
        StructField("client_id", StringType(), True),
        StructField("timestamp", DoubleType(), True),   # ← число, не строка!
        StructField("lat", DoubleType(), True),
        StructField("lon", DoubleType(), True),
    ])
    parsed = F.from_json(F.col("value").cast("string"), incoming_message_schema)

    return (df.select(
                "offset",
                parsed.alias("parsed"),
            ).select(
                "offset",  # офсет оригинального сообщения из Kafka
                F.col("parsed.client_id").alias("client_id"),
                #F.from_unixtime(F.col("parsed.timestamp"), "yyyy-MM-dd HH:mm:ss.SSS").cast("timestamp").alias("timestamp"),
                F.to_timestamp(F.from_unixtime(F.col("parsed.timestamp"))).alias("timestamp"),
                F.col("parsed.lat").alias("lat"),
                F.col("parsed.lon").alias("lon"),
            )
            .withWatermark("timestamp", "10 minute")
            .dropDuplicates(["client_id", "timestamp"])
        )


def join(user_df, marketing_df) -> DataFrame:
    # Каждая акция × каждый пользователь
    return (
        user_df.crossJoin(marketing_df)
            .select(
                "client_id",
                "adv_campaign_id",
                "adv_campaign_name",
                "adv_campaign_description",
                "adv_campaign_start_time",
                "adv_campaign_end_time",
                "adv_campaign_point_lat",
                "adv_campaign_point_lon",
                F.current_timestamp().alias("created_at"), # время создания выходного ивента
                "offset",
            )
    )

if __name__ == "__main__":
    spark = spark_init("join stream")
    client_stream = read_client_stream(spark)
    marketing_df = read_marketing(spark)
    result = join(client_stream, marketing_df)

    query = (result
             .writeStream
             .outputMode("append")
             .format("console")
             .option("truncate", False)
             .start())
    query.awaitTermination()
