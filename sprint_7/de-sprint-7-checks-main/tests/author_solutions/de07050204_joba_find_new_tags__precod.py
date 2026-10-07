import datetime
import sys

import pyspark.sql.functions as F
from pyspark import SparkConf, SparkContext
from pyspark.sql import SQLContext


def main():
    date = # допишите код
    days_count = # допишите код
    suggested_cutoff = # допишите код
    base_input_path = # допишите код
    verified_tags_path = # допишите код
    base_output_path = # допишите код

    conf = SparkConf().setAppName(f"VerifiedTagsCandidatesJob-{date}-d{days_count}-cut{suggested_cutoff}")
    sc = SparkContext(conf=conf)
    sql = SQLContext(sc)

    dt = datetime.datetime.strptime(date, '%Y-%m-%d')
    paths = # допишите код используя переменные `base_input_path`, `days_count`
    messages = sql.read.parquet(*paths)

    verified_tags = sql.read.parquet(verified_tags_path)

    candidates = find_candidates(messages, verified_tags, suggested_cutoff)

    candidates.write.parquet # допишите код


def find_candidates(messages, verified_tags, suggested_cutoff):
    all_tags = messages\
        .where("event.message_channel_to is not null")\
        .selectExpr(["event.message_from as user", "explode(event.tags) as tag"])\
        .groupBy("tag")\
        .agg(F.countDistinct("user").alias("suggested_count"))\
        .where(F.col("suggested_count") >= suggested_cutoff)

    return all_tags.join(verified_tags, "tag", "left_anti")


if __name__ == "__main__":
    main()
