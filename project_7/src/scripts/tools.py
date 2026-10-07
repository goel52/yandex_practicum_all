import findspark
findspark.init()
findspark.find()
import os
import pyspark
from pyspark.sql import SparkSession
from pyspark.sql.window import Window
import pyspark.sql.functions as F

os.environ['HADOOP_CONF_DIR'] = '/etc/hadoop/conf'
os.environ['YARN_CONF_DIR'] = '/etc/hadoop/conf'
os.environ['JAVA_HOME']='/usr'
os.environ['SPARK_HOME'] ='/usr/lib/spark'
os.environ['PYTHONPATH'] ='/usr/local/lib/python3.8'

def get_spark_session(name=""):
    return SparkSession \
        .builder \
        .master("yarn")\
        .appName(f"{name}") \
        .getOrCreate()

def get_city(events_geo, geo_city) -> pyspark.sql.DataFrame:

    EARTH_R = 6371

    calculate_diff = 2 * F.lit(EARTH_R) * F.asin(
        F.sqrt(
            F.pow(F.sin((F.radians(F.col("msg_lat")) - F.radians(F.col("city_lat"))) / 2), 2) +
            F.cos(F.radians(F.col("msg_lat"))) * F.cos(F.radians(F.col("city_lat"))) *
            F.pow(F.sin((F.radians(F.col("msg_lon")) - F.radians(F.col("city_lon"))) / 2), 2)
        )
    )
    

    window = Window().partitionBy('event.message_from').orderBy(F.col('diff').asc())
    events_city = events_geo \
        .crossJoin(geo_city) \
        .withColumn('diff', calculate_diff)\
        .withColumn("row_number", F.row_number().over(window)) \
        .filter(F.col('row_number')==1) \
        .drop('row_number') \
        .persist()

    return events_city

def df_local_time(events: pyspark.sql.DataFrame) -> pyspark.sql.DataFrame:    
    # В geo.csv добавлена новая колонка timezone со сгенерированными временными зонами относительно названия города
    # при помощи библиотеки timezonefinder
    return events.withColumn("TIME",F.col("event.datetime").cast("Timestamp"))\
        .withColumn("local_time",F.from_utc_timestamp(F.col("TIME"),F.col('timezone')))\
        .select("TIME", "local_time", 'city', 'user_id')
        
def write_dm(df: pyspark.sql.DataFrame, dm_name: str, date: str) -> None:
    """Записывает dataframe в дирректорию витрины

    Args:
        df (pyspark.sql.DataFrame): Датафрейм для записи
        dm_name (str): название директории витрины
        date (str): дата
    """
    df.write.mode('overwrite').parquet(f'/user/TEST/analitics/{dm_name}/date={date}')