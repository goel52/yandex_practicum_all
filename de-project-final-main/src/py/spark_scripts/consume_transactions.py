import sys, json
from datetime import datetime
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import TimestampType, StructType, StructField, StringType


def consume_from_kafka(spark, kafka_options):

    df = (spark.read
            .format('kafka')
            .options(**kafka_options)
            .load())

    json_schema = StructType([
        StructField("object_id", StringType()),
        StructField("object_type", StringType()),
        StructField("sent_dttm", TimestampType()),
        StructField("payload", StringType())])

    processed_df = (df
        .withColumn('value',
                    from_json(col('value').cast(StringType()),
                    json_schema))
        .select('value.*')
        .dropDuplicates(['object_id', 'object_type'])
        .withWatermark('sent_dttm', '5 minutes')
        )

    return processed_df

def write_to_vertica(processed_df, vertica_table, vertica_options):
    (processed_df.write
                .option('driver', 'com.vertica.jdbc.Driver')
                .option('createTableColumnTypes', '''
                                                object_id varchar(40),
                                                object_type varchar(20),
                                                sent_dttm timestamp,
                                                payload varchar(1024)
                                                ''')
                .mode('append')
                .jdbc(vertica_options['vertica_url'],
                      vertica_table,
                      properties=vertica_options['vertica_props']))

def main():
    kafka_user = sys.argv[1]
    kafka_pass = sys.argv[2]
    kafka_topic = sys.argv[3]
    vertica_user = sys.argv[4]
    vertica_pass = sys.argv[5]
    vertica_table = sys.argv[6]

    kafka_options = {
        "kafka.bootstrap.servers": "rc1a-8sr9ka4r3f8sdjgq.mdb.yandexcloud.net:9091",
        "kafka.sasl.jaas.config": ("org.apache.kafka.common.security.scram.ScramLoginModule"
                                   f" required username=\"{kafka_user}\" password=\"{kafka_pass}\";"
                                  ),
        "kafka.sasl.mechanism": "SCRAM-SHA-512",
        "kafka.security.protocol": "SASL_SSL",
        "subscribe": kafka_topic,
        "startingOffsets": "earliest"
        }

    vertica_options = {
        "vertica_props": {
            "password": vertica_pass,
            "user": vertica_user
        },
        "vertica_url": "jdbc:vertica://51.250.75.20:5433/"
    }

    spark_jars_packages = ",".join(
            [
                "org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0",
                "com.vertica.jdbc:vertica-jdbc:11.0.0-0"
            ]
    )

    spark = (
        SparkSession.builder
        .master("local")
        .appName('collect data from kafka')
        .config("spark.jars.packages", spark_jars_packages)
        .getOrCreate()
    )

    processed_df = consume_from_kafka(spark, kafka_options)
    
    processed_df.show(5)

    write_to_vertica(processed_df, vertica_table, vertica_options)

if __name__ == "__main__":
        main()