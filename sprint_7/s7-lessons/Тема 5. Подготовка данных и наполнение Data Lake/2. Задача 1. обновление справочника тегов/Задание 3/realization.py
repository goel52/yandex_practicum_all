"""Заготовка решения. Замените TODO своим кодом перед отправкой."""

import datetime

import pyspark.sql.functions as F
from pyspark.sql import SparkSession

spark = SparkSession \
    .builder \
    .master("yarn") \
        .config("spark.driver.cores", "2") \
        .config("spark.driver.memory", "2g") \
        .appName("test1337") \
        .getOrCreate()

def input_paths(date, depth):
    dt = datetime.datetime.strptime(date, '%Y-%m-%d')
    return [f"/user/username/data/events/date={(dt-datetime.timedelta(days=x)).strftime('%Y-%m-%d')}/event_type=message" for x in range(depth)]


paths = input_paths('2022-05-31', 84)
messages = spark.read.parquet(*paths)
all_tags = messages.where("event.message_channel_to is not null").selectExpr(["event.message_from as user", "explode(event.tags) as tag"]).groupBy("tag").agg(F.expr("count(distinct user) as suggested_count")).where("suggested_count >= 100")
verified_tags = spark.read.parquet("/user/master/data/snapshots/tags_verified/actual")
candidates = all_tags.join(verified_tags, "tag", "left_anti")

candidates.write.parquet('/user/username/data/analytics/candidates_d84_pyspark')