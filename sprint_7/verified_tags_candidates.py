from datetime import datetime, timedelta
import sys
import findspark
findspark.init()
findspark.find()
import os

os.environ['HADOOP_CONF_DIR'] = '/etc/hadoop/conf'
os.environ['YARN_CONF_DIR'] = '/etc/hadoop/conf'
os.environ['JAVA_HOME']='/usr'
os.environ['SPARK_HOME'] ='/usr/lib/spark'
os.environ['PYTHONPATH'] ='/usr/local/lib/python3.8'

import pyspark
from pyspark.sql import SparkSession
from pyspark.sql.window import Window
import pyspark.sql.functions as F
from pyspark import SparkContext, SparkConf
from pyspark.sql import SQLContext

user = 'zrtsr'
pre_path = 'hdfs://rc1a-dataproc-m-dg5lgqqm7jju58f9.mdb.yandexcloud.net:8020'

def main():
    
    date = sys.argv[1]
    depth = sys.argv[2]
    cut = sys.argv[3]
    base_input_path = sys.argv[4]
    verified_tags_path = sys.argv[5]
    base_output_path = sys.argv[6]

    spark = SparkSession.builder.master("yarn").appName(f"VerifiedTagsCandidatesJob-{date}-{depth}-{cut}").getOrCreate()

    try:
        isinstance(date, datetime.date())
    except:
        date = datetime.strptime(date, '%Y-%m-%d').date()
    
    paths = [f'{pre_path}{base_input_path}/date={date-timedelta(depth)}/event_type=message' for depth in range(depth)]
        
    messages_df = spark.read.parquet(*paths)

    all_tags = messages_df \
        .filter(F.col("event.message_channel_to").isNotNull()) \
        .selectExpr(["event.message_from as user", "explode(event.tags) as tag"]) \
        .groupBy("tag").agg(F.expr("count(distinct user) as suggested_count")) \
        .filter(F.col("suggested_count") >= cut)

    verified_tags = spark.read.parquet(verified_tags_path)
    candidates = all_tags.join(verified_tags, "tag", "left_anti")
    candidates.write.format('parquet').mode('overwrite').save(f'{pre_path}{base_output_path}/date={date}')

    # /usr/lib/spark/bin/spark-submit 
    # verified_tags_candidates.py 
    # 2022-05-31 
    # 5 
    # 300 
    # /user/username/data/events 
    # /user/username/data/snapshots/tags_verified/actual 
    # /user/username/data/analytics/verified_tags_candidates_d5

    # spark-submit \
    # /lessons/verified_tags_candidates.py \
    # 2022-05-31 \
    # 5 \
    # 300 \
    # /user/zrtsr/data/events \
    # /user/master/data/snapshots/tags_verified/actual \
    # /user/zrtsr/data/analytics

if __name__ == "__main__":
    main()