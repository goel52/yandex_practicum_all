import findspark
findspark.init()
findspark.find()
import sys
import pyspark.sql.functions as F 
from pyspark.sql.types import FloatType
from pyspark.sql.window import Window
from tools import get_spark_session, get_city, write_dm

date = sys.argv[1]

spark = get_spark_session(name='DM_by_zones')

path_geo = "/user/violent140/geo_2.csv"
raw_path_geo_events = "/user/master/data/geo/events"

events_geo = spark.read.parquet(raw_path_geo_events) \
    .sample(0.05) \
    .withColumn('user_id', F.col('event.message_from'))\
    .withColumnRenamed('lat', 'msg_lat')\
    .withColumnRenamed('lon', 'msg_lon')\
    .withColumn('event_id', F.monotonically_increasing_id())

geo_city = spark.read.csv(path_geo, sep=';',inferSchema=True, header=True)

geo_city = geo_city.withColumn('lat', F.regexp_replace('lat', ',', '.')) \
    .withColumn('lat', F.col('lat').cast(FloatType())) \
    .withColumn('lng', F.regexp_replace('lng', ',', '.')) \
    .withColumn('lng', F.col('lng').cast(FloatType())) \
    .withColumnRenamed('lat', "city_lat")\
    .withColumnRenamed('lng', "city_lon")


events = get_city(
    events_geo=events_geo,
    geo_city=geo_city
)

# Исправил
w_week = Window.partitionBy(['city', F.trunc(F.col("date"), "week")])
w_month = Window.partitionBy(['city', F.trunc(F.col("date"), "month")])

df_zones = events.withColumn('week_message', F.count(F.when(events.event_type == 'message','event_id')).over(w_week)) \
    .withColumn('week_reaction', F.count(F.when(events.event_type == 'reaction','event_id')).over(w_week)) \
    .withColumn('week_subscription', F.count(F.when(events.event_type == 'subscription','event_id')).over(w_week)) \
    .withColumn('week_user', F.count(F.when(events.event_type == 'registration','event_id')).over(w_week)) \
    .withColumn('month_message', F.count(F.when(events.event_type == 'message','event_id')).over(w_month)) \
    .withColumn('month_reaction', F.count(F.when(events.event_type == 'reaction','event_id')).over(w_month)) \
    .withColumn('month_subscription', F.count(F.when(events.event_type == 'subscription','event_id')).over(w_month)) \
    .withColumn('month_user', F.count(F.when(events.event_type == 'registration','event_id')).over(w_month)) \
    .withColumn('month', F.trunc(F.col("date"), "month")) \
    .withColumn('week', F.trunc(F.col("date"), "week")) \
    .select('month', 'week', 'city', 'week_message', 'week_reaction', 'week_subscription', 'week_user', \
            'month_message', 'month_reaction', 'month_subscription', 'month_user') \
    .distinct()

write_dm(df_zones, 'dm_zones', date)