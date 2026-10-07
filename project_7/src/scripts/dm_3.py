import findspark
findspark.init()
findspark.find()
import sys
import pyspark.sql.functions as F 
from pyspark.sql.window import Window
from tools import get_spark_session, get_city, df_local_time, write_dm

date = sys.argv[1]

spark = get_spark_session(name='DM_friends_recomendations')
        

path_geo = "/user/TEST/geo_2.csv"
raw_path_geo_events = "/user/master/data/geo/events"

events_geo = spark.read.parquet(raw_path_geo_events) \
    .sample(0.05) \
    .where("event_type == 'message'")\
    .withColumn('user_id', F.col('event.message_from'))\
    .withColumnRenamed('lat', 'msg_lat')\
    .withColumnRenamed('lon', 'msg_lon')\
    .withColumn('event_id', F.monotonically_increasing_id())

geo_city = spark.read.csv(path_geo, sep=';',inferSchema=True, header=True)\
    .withColumnRenamed('lat', "city_lat")\
    .withColumnRenamed('lng', "city_lon")


events = get_city(
    events_geo=events_geo,
    geo_city=geo_city
)

w_l = Window.partitionBy('user_id').orderBy(F.col('event.message_ts').desc())
view_last = events.where('msg_lon is not null') \
    .withColumn("rn",F.row_number().over(Window().partitionBy('user_id').orderBy(F.col('event.message_ts').desc()))) \
    .filter(F.col('rn') == 1) \
    .drop(F.col('rn')) \
    .selectExpr('user_id', 'msg_lon as lon', 'msg_lat as lat')

# локальное время сразу к событиям получил и дальше уже с ним выборки делаю    
events_with_local_time = df_local_time(events)
events_city = events_with_local_time.select('user_id', 'city', 'local_time')

view_last = view_last.join(events_city, ['user_id'], 'inner')

view_last_channel = events.select(
    F.col('event.subscription_channel').alias('channel'),
    F.col('event.user').alias('user_id')
).distinct()

new = view_last_channel.join(view_last_channel.withColumnRenamed('user_id', 'user_id2'), ['channel'], 'inner') \
    .filter('user_id < user_id2')
    
user_list = new.join(view_last,['user_id'],'inner') \
    .withColumnRenamed('lon','lon_user1') \
    .withColumnRenamed('lat','lat_user1') \
    .drop('city').drop('local_time')

user_list = user_list\
    .join(view_last, view_last['user_id'] == user_list['user_id2'], 'inner').drop(view_last['user_id']) \
    .withColumnRenamed('lon','lon_user2') \
    .withColumnRenamed('lat','lat_user2') \
    .drop(view_last['city'])

distance = user_list \
    .withColumn('dlon_start', F.radians(F.col('lon_user1')) - F.radians(F.col('lon_user1'))) \
    .withColumn('dlat_start', F.radians(F.col('lat_user1')) - F. radians(F.col('lat_user2'))) \
    .withColumn('dist_start', F.asin(F.sqrt(
        F.sin(F.col('dlat_start') / 2) ** 2 + F.cos(F.radians(F.col('lat_user2')))
        * F.cos(F.radians(F.col('lat_user1'))) * F.sin(F.col('dlon_start') / 2) ** 2
    )) * 2 * 6371)
    
# Выбрал отправителя и получателя, объединил с первернутыми и оставил уникальные
events_pairs = events.selectExpr('event.message_from as user_id','event.message_to as user_id2').where(F.col('user_id2').isNotNull())
events_pairs_union = events_pairs.union(events_pairs.select('user_id2', 'user_id')).distinct()

# вычел пары из выборки
result_dist = distance \
    .filter(F.col('dist_start') <= 1) \
    .join(events_pairs_union, ['user_id', 'user_id2'], 'left_anti') \
    .withColumn('processed_dttm', F.current_timestamp()) \
    .selectExpr('user_id as user_left', 'user_id2 as user_right', 'processed_dttm', 'city', 'local_time').distinct()

write_dm(result_dist, 'dm_friends_recomendation', date)