from pyspark.sql import SparkSession

def main():

    spark_jars_packages = ",".join(
        [
            "org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0",
            "org.postgresql:postgresql:42.4.0",
        ]
    )

    spark = (
        SparkSession.builder.appName('test_name')
        .config("spark.sql.session.timeZone", "UTC")
        .config("spark.jars.packages", spark_jars_packages)
        .getOrCreate()
    )

    db_pass = 'de-student'
    df = (spark.read
          .format('jdbc')
          .option('url', 'jdbc:postgresql://rc1a-fswjkpli01zafgjm.mdb.yandexcloud.net:6432/de')
          .option('driver', 'org.postgresql.Driver')
          .option('dbtable', 'public.marketing_companies')
          .option('user', 'student')
          .option('password', db_pass)
          .load())
    print(df.printSchema())
    print(df.count())


if __name__ == '__main__':
    main()