from datetime import datetime
from time import sleep
from pyspark.sql import SparkSession, DataFrame
from pyspark.sql import functions as f
from pyspark.sql.types import StructType, StructField, DoubleType, StringType, TimestampType, IntegerType
TOPIC_NAME_91 = 'student.topic.cohort0.test.out'
TOPIC_NAME_IN = 'student.topic.cohort0.test'

def spark_init(test_name) -> SparkSession:
    spark_jars_packages = ','.join(['org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0', 'org.postgresql:postgresql:42.4.0'])
    spark = SparkSession.builder.appName(test_name).config('spark.sql.session.timeZone', 'UTC').config('spark.jars.packages', spark_jars_packages).getOrCreate()
    return spark
postgresql_settings = {'user': 'fixture', 'password': 'fixture'}

def read_marketing(spark: SparkSession) -> DataFrame:
    marketing_df = spark.read.format('jdbc').option('url', 'jdbc:postgresql://fixture/de').option('dbtable', 'marketing_companies').option('driver', 'org.postgresql.Driver').options(**postgresql_settings).load()
    return marketing_df
kafka_security_options = {'kafka.security.protocol': 'SASL_SSL', 'kafka.sasl.mechanism': 'SCRAM-SHA-512', 'kafka.sasl.jaas.config': 'fixture-auth'}

def read_client_stream(spark: SparkSession) -> DataFrame:
    schema = StructType([StructField('client_id', StringType()), StructField('timestamp', DoubleType()), StructField('lat', DoubleType()), StructField('lon', DoubleType())])
    df = spark.readStream.format('kafka').option('kafka.bootstrap.servers', 'fixture:9092').option('subscribe', TOPIC_NAME_IN).options(**kafka_security_options).option('maxOffsetsPerTrigger', 1000).load().withColumn('value', f.col('value').cast(StringType())).withColumn('event', f.from_json(f.col('value'), schema)).selectExpr('event.*').withColumn('timestamp', f.from_unixtime(f.col('timestamp'), "yyyy-MM-dd' 'HH:mm:ss.SSS").cast(TimestampType())).withWatermark('timestamp', '10 minutes').dropDuplicates(['client_id', 'timestamp'])
    return df

def join(user_df, marketing_df) -> DataFrame:
    """

    {
        "client_id": идентификатор клиента,
        "distance" : int расстояние до рестора/точки, в метрах
        "adv_campaign_id": идентификатор рекламной акции,
        "adv_campaign_description": описание рекламной акции,
        "adv_campaign_start_time": время начала акции,
        "adv_campaign_end_time": время окончания акции,
        "created_at": время создания выходного ивента
    }
    """
    return user_df.crossJoin(marketing_df).withColumn('adv_campaign_id', marketing_df.id).withColumn('adv_campaign_name', marketing_df.name).withColumn('adv_campaign_point_lat', marketing_df.point_lat).withColumn('adv_campaign_point_lon', marketing_df.point_lon).withColumn('adv_campaign_description', marketing_df.description).withColumn('adv_campaign_start_time', marketing_df.start_time).withColumn('adv_campaign_end_time', marketing_df.end_time).withColumn('created_at', f.lit(datetime.now())).withColumn('a', f.pow(f.sin(f.radians(marketing_df.point_lat - user_df.lat) / 2), 2) + f.cos(f.radians(user_df.lat)) * f.cos(f.radians(marketing_df.point_lat)) * f.pow(f.sin(f.radians(marketing_df.point_lon - user_df.lon) / 2), 2)).withColumn('distance', f.atan2(f.sqrt(f.col('a')), f.sqrt(-f.col('a') + 1)) * 12742000).where(f.col('distance') <= 1000).withColumn('distance', f.col('distance').cast(IntegerType())).select(f.to_json(f.struct('client_id', 'distance', 'adv_campaign_id', 'adv_campaign_name', 'adv_campaign_point_lat', 'adv_campaign_point_lon', 'adv_campaign_description', 'adv_campaign_start_time', 'adv_campaign_end_time', 'created_at')).alias('value'))

def run_query(df):
    return df.writeStream.outputMode('append').format('kafka').option('kafka.bootstrap.servers', 'fixture:9092').options(**kafka_security_options).option('topic', TOPIC_NAME_91).option('checkpointLocation', 'test_query').trigger(processingTime='1 minute').start()
if __name__ == '__main__':
    spark = spark_init('join stream')
    client_stream = read_client_stream(spark)
    marketing_df = read_marketing(spark)
    output = join(client_stream, marketing_df)
    query = run_query(output)
    while query.isActive:
        print(f'query information: runId={query.runId}, status is {query.status}, recent progress={query.recentProgress}')
        sleep(30)
    query.awaitTermination()
