import sys

from pyspark import SparkContext, SparkConf
from pyspark.sql import SQLContext
import pyspark.sql.functions as F
from pyspark.sql.window import Window
import datetime


def input_event_paths(base_path, date, depth):
    dt = datetime.datetime.strptime(date, '%Y-%m-%d')
    return [f"{base_path}/date="
            f"{(dt-datetime.timedelta(days=x)).strftime('%Y-%m-%d')}"
            for x in range(int(depth))]


def main():
    date = sys.argv[1]
    days_count = sys.argv[2]
    events_base_path = sys.argv[3]
    interests_base_path = sys.argv[4]
    verified_tags_path = sys.argv[5]
    output_base_path = sys.argv[6]

    conf = SparkConf().setAppName(
        f"ConnectionInterestsJob-{date}-d{days_count}")
    sc = SparkContext(conf=conf)
    sql = SQLContext(sc)

    messages = sql.read\
        .option("basePath", events_base_path)\
        .parquet(*input_event_paths(events_base_path, date, days_count))\
        .where("event_type='message'")

    direct_messages = messages.where("event.message_to is not null")
    posts = messages.where("event.message_channel_to is not null")

    interests = sql.read.parquet(f"{interests_base_path}/date={date}")
    subscriptions = sql.read.parquet(events_base_path)\
        .where(f"event_type = 'subscription' and date <= '{date}'")

    verified_tags = sql.read.parquet(verified_tags_path)

    contacts = get_contacts(direct_messages)
    contact_interests = get_contact_interests(contacts, interests).cache()
    subs_interests = get_subs_interests(
        posts, subscriptions, verified_tags).cache()

    result = join_result(contact_interests, subs_interests)
    result.write.mode("overwrite").parquet(f"{output_base_path}/date={date}")


def get_contacts(direct_messages):
    return direct_messages\
        .select(
            F.col("event.message_from").alias("from"),
            F.col("event.message_to").alias("to"),
            F.explode(F.array(
                F.col("event.message_from"),
                F.col("event.message_to"))).alias("user_id"))\
        .withColumn("contact_id",
                    F.when(F.col("user_id") == F.col("from"),
                           F.col("to")).otherwise(F.col("from")))\
        .select("user_id", "contact_id")\
        .distinct()


def get_contact_interests(contacts, interests):
    # Count a tag once per contact, regardless of its original top-1/2/3 slot.
    users = contacts.select('user_id').distinct()
    joined = contacts.alias('c').join(
        interests.alias('i'), F.col('c.contact_id') == F.col('i.user_id'))
    result = users
    for reaction in ('like', 'dislike'):
        tags = joined.select(
            F.col('c.user_id').alias('user_id'), 'contact_id',
            F.explode(F.array(*[F.col('i.' + c) for c in tag_columns(reaction)])).alias('tag'))
        top = tags.where(F.col('tag').isNotNull()).groupBy('user_id', 'tag').agg(
            F.countDistinct('contact_id').alias('tag_count'))
        top = top.withColumn('rank', F.row_number().over(
            Window.partitionBy('user_id').orderBy(F.desc('tag_count'), F.desc('tag'))))
        top = top.where('rank <= 3').groupBy('user_id').pivot('rank', [1, 2, 3]).agg(F.first('tag'))
        for rank in (1, 2, 3):
            top = top.withColumnRenamed(str(rank), f'direct_{reaction}_tag_top_{rank}')
        result = result.join(top, 'user_id', 'left')
    return result


def get_subs_interests(posts, subscriptions, verified_tags):
    post_tags = posts\
        .select(F.col("event.message_channel_to").alias("channel_id"),
                F.col("event.tags").alias("tags"))

    subscribers = subscriptions.select(
        F.col('event.subscription_channel').alias('channel_id'),
        F.col('event.user').alias('user_id')).distinct()
    verified_sub_tags = post_tags.join(subscribers, 'channel_id').select(
        'user_id', F.explode('tags').alias('tag')).join(verified_tags, 'tag', 'left_semi')

    return verified_sub_tags\
        .groupBy("user_id", "tag")\
        .agg(F.count("*").alias("tag_count"))\
        .withColumn(
            "rank",
            F.row_number().over(
                Window.partitionBy("user_id").orderBy(F.desc("tag_count"),
                                                      F.desc("tag"))))\
        .where("rank <= 3")\
        .groupBy("user_id")\
        .pivot("rank", [1, 2, 3])\
        .agg(F.first("tag"))\
        .withColumnRenamed("1", "sub_verified_tag_top_1")\
        .withColumnRenamed("2", "sub_verified_tag_top_2")\
        .withColumnRenamed("3", "sub_verified_tag_top_3")


def join_result(contact_interests, subs_interests):
    return contact_interests\
        .join(subs_interests, "user_id", "full_outer")


def tag_columns(reaction):
    return [f"{reaction}_tag_top_{X}" for X in range(1, 4)]


if __name__ == "__main__":
    main()
