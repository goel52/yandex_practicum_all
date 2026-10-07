import datetime

import pyspark.sql.functions as F
from pyspark.sql.window import Window


def input_event_paths(date, depth):
    dt = datetime.datetime.strptime(date, '%Y-%m-%d')
    return [f"/user/username/data/events/date={(dt-datetime.timedelta(days=x)).strftime('%Y-%m-%d')}" for x in range(depth)]


def tag_tops(date, depth, spark):

    # напишите ваш код здесь

    return result
