import datetime
from random import randint

from pyspark.sql import SparkSession
from pyspark.sql.types import (ArrayType, DateType, LongType, Row, StringType,
                               StructField, StructType)

event = 'event'
admins = 'admins'
channel_id = 'channel_id'
_datetime = 'datetime'
media = 'media'
media_type = 'media_type'
src = 'src'
message = 'message'
message_channel_to = 'message_channel_to'
message_from = 'message_from'
message_group = 'message_group'
message_id = 'message_id'
message_to = 'message_to'
message_ts = 'message_ts'
reaction_from = 'reaction_from'
reaction_type = 'reaction_type'
subscription_channel = 'subscription_channel'
subscription_user = 'subscription_user'
tags = 'tags'
user = 'user'

# TODO: make generation df for all checks

SCHEMA = StructType(
    [StructField(event, StructType(
                [StructField(admins, ArrayType(LongType(), True), True),
                 StructField(channel_id, LongType(), True),
                 StructField(_datetime, StringType(), True),
                 StructField(media, StructType([
                        StructField(media_type, StringType(), True),
                        StructField(src, StringType(), True)]), True),
                 StructField(message, StringType(), True),
                 StructField(message_channel_to, LongType(), True),
                 StructField(message_from, LongType(), True),
                 StructField(message_group, LongType(), True),
                 StructField(message_id, LongType(), True),
                 StructField(message_to, LongType(), True),
                 StructField(message_ts, StringType(), True),
                 StructField(reaction_from, StringType(), True),
                 StructField(reaction_type, StringType(), True),
                 StructField(subscription_channel, LongType(), True),
                 StructField(subscription_user, StringType(), True),
                 StructField(tags, ArrayType(StringType(), True), True),
                 StructField(user, StringType(), True)]), True)])


SCHEMA_TAG_TOPS = StructType(
    [StructField(event, StructType(
                [StructField(admins, ArrayType(LongType(), True), True),
                 StructField(channel_id, LongType(), True),
                 StructField(_datetime, StringType(), True),
                 StructField(media, StructType([
                        StructField(media_type, StringType(), True),
                        StructField(src, StringType(), True)]), True),
                 StructField(message, StringType(), True),
                 StructField(message_channel_to, LongType(), True),
                 StructField(message_from, LongType(), True),
                 StructField(message_group, LongType(), True),
                 StructField(message_id, LongType(), True),
                 StructField(message_to, LongType(), True),
                 StructField(message_ts, StringType(), True),
                 StructField(reaction_from, StringType(), True),
                 StructField(reaction_type, StringType(), True),
                 StructField(subscription_channel, LongType(), True),
                 StructField(subscription_user, StringType(), True),
                 StructField(tags, ArrayType(StringType(), True), True),
                 StructField(user, StringType(), True)]), True),
     StructField('date', DateType(), True),
     StructField('event_type', StringType(), True)])


def _row_event(
        admins=[None],
        channel_id=None,
        datetime='2022-05-28 06:01:03',
        media=Row(
            media_type='image',
            src='https://company.com/cdn/OkmXQCKZli'
            ),
        message='...',
        message_channel_to=None,
        message_from=None,
        message_group=None,
        message_id=None,
        message_to=None,
        message_ts=None,
        reaction_from=None,
        reaction_type=None,
        subscription_channel=None,
        subscription_user=None,
        tags=[None],
        user=None):
    return Row(event=Row(
        admins=admins,
        channel_id=channel_id,
        datetime=datetime,
        media=media,
        message=message,
        message_channel_to=message_channel_to,
        message_from=message_from,
        message_group=message_group,
        message_id=message_id,
        message_to=message_to,
        message_ts=message_ts,
        reaction_from=reaction_from,
        reaction_type=reaction_type,
        subscription_channel=subscription_channel,
        subscription_user=subscription_user,
        tags=tags,
        user=user
    ))


def _row_event_type(
        admins=[None],
        channel_id=None,
        datetime='2022-05-28 06:01:03',
        media=Row(
            media_type='image',
            src='https://company.com/cdn/OkmXQCKZli'
            ),
        message='...',
        message_channel_to=None,
        message_from=None,
        message_group=None,
        message_id=None,
        message_to=None,
        message_ts=None,
        reaction_from=None,
        reaction_type=None,
        subscription_channel=None,
        subscription_user=None,
        tags=[None],
        user=None,
        date_event=datetime.datetime(2022, 5, 31),
        event_type='message'):
    return Row(event=Row(
                    admins=admins,
                    channel_id=channel_id,
                    datetime=datetime,
                    media=media,
                    message=message,
                    message_channel_to=message_channel_to,
                    message_from=message_from,
                    message_group=message_group,
                    message_id=message_id,
                    message_to=message_to,
                    message_ts=message_ts,
                    reaction_from=reaction_from,
                    reaction_type=reaction_type,
                    subscription_channel=subscription_channel,
                    subscription_user=subscription_user,
                    tags=tags,
                    user=user),
               date=date_event,
               event_type=event_type
               )


def event_find_new_tags(
        spark: SparkSession,
        count_unique_users: int = 120,
        count_unique_tags: int = 20) -> SparkSession:
    return spark.createDataFrame(
        data=data_for_find_new_tags(count_unique_users=count_unique_users,
                                    count_unique_tags=count_unique_tags),
        schema=SCHEMA)


def event_user_tag_tops(
        spark: SparkSession,
        count_unique_users: int = 10,
        count_unique_tags: int = 10) -> SparkSession:
    return spark.createDataFrame(
        data=data_for_user_tag_tops(count_unique_users=count_unique_users,
                                    count_unique_tags=count_unique_tags),
        schema=SCHEMA_TAG_TOPS)


def data_for_user_tag_tops(
        count_unique_users: int = 10,
        count_unique_tags: int = 10) -> list:

    data = list()

    data.append(
        _row_event_type()
    )

    data.extend([
        _row_event_type(message_from=1, message_channel_to=1, tags=['tag_1']),
        _row_event_type(message_from=1, message_channel_to=1, tags=['tag_2'], message_id=1),  # noqa
        _row_event_type(message_from=1, message_channel_to=1, tags=['tag_2'], message_id=1),  # noqa
        _row_event_type(message_from=2, message_channel_to=1, tags=['tag_1', 'tag_2']),  # noqa
        _row_event_type(message_from=3, message_channel_to=1, tags=['tag_1', 'tag_2', 'tag_3']),  # noqa
        _row_event_type(message_from=4, message_channel_to=1, tags=['tag_1', 'tag_2', 'tag_3', 'tag_4']),  # noqa
        _row_event_type(message_from=5, message_channel_to=1),
        _row_event_type(message_from=6, message_channel_to=1, tags=['tag_6']),
        _row_event_type(message_from=6, message_channel_to=1, tags=['tag_6']),
        _row_event_type(message_from=6, message_channel_to=1, tags=['tag_6']),
        _row_event_type(message_from=6, message_channel_to=1, tags=['tag_6']),
        _row_event_type(message_from=6, message_channel_to=1, tags=['tag_6']),
        _row_event_type(message_from=6, message_channel_to=1, tags=['tag_6']),
        _row_event_type(message_from=6, message_channel_to=1, tags=['tag_6']),
    ])

    return data


def data_for_find_new_tags(
        count_unique_users: int = 120,
        count_unique_tags: int = 20) -> list:

    users = [f'user_{_}' for _ in range(0, count_unique_users)]
    users_id = [_ for _ in range(0, count_unique_users)]

    tags = [f'tag_{_}' for _ in range(0, count_unique_tags)]

    tags.extend([  # TODO: make get random items from tags_verified
        'Настройка Linux',
        'Assembler',
        'include',
        'cipher-cloud'
    ])

    data = list()

    for user_id in users_id:
        data.append(
            _row_event(
                user=users[randint(0, count_unique_users-1)],
                tags=tags)
        )

    for user_id in users_id:
        data.append(
            _row_event(
                user=users[randint(0, count_unique_users-1)],
                tags=tags,
                message_channel_to=randint(1, 100),
                message_from=user_id)
        )

    return data


def event_user_reaction_tag_tops(
        spark: SparkSession) -> SparkSession:
    return spark.createDataFrame(
        data=data_for_user_reaction_tag_tops(),
        schema=SCHEMA_TAG_TOPS)


def data_for_user_reaction_tag_tops() -> list:

    data = list()

    data.append(
        _row_event_type()
    )

    data.extend([
        _row_event_type(message_id=1,  message_from=1, message_channel_to=1, tags=['tag_1']),
        _row_event_type(message_id=2,  message_from=1, message_channel_to=1, tags=['tag_2']),  # noqa
        _row_event_type(message_id=3,  message_from=1, message_channel_to=1, tags=['tag_2']),  # noqa
        _row_event_type(message_id=4,  message_from=2, message_channel_to=1, tags=['tag_1', 'tag_2']),  # noqa
        _row_event_type(message_id=5,  message_from=3, message_channel_to=1, tags=['tag_1', 'tag_2', 'tag_3']),  # noqa
        _row_event_type(message_id=6,  message_from=4, message_channel_to=1, tags=['tag_1', 'tag_2', 'tag_3', 'tag_4']),  # noqa
        _row_event_type(message_id=7,  message_from=5, message_channel_to=1),
        _row_event_type(message_id=8,  message_from=6, message_channel_to=1, tags=['tag_6']),
        _row_event_type(message_id=9,  message_from=6, message_channel_to=1, tags=['tag_6']),
        _row_event_type(message_id=10, message_from=6, message_channel_to=1, tags=['tag_6']),
        _row_event_type(message_id=11, message_from=6, message_channel_to=1, tags=['tag_6']),
        _row_event_type(message_id=12, message_from=6, message_channel_to=1, tags=['tag_6']),
        _row_event_type(message_id=13, message_from=6, message_channel_to=1, tags=['tag_6']),
        _row_event_type(message_id=14, message_from=6, message_channel_to=1, tags=['tag_6']),
        _row_event_type(message_id=1, reaction_type='like',    event_type='reaction', reaction_from=1),
        _row_event_type(message_id=2, reaction_type='dislike', event_type='reaction', reaction_from=2),
        _row_event_type(message_id=4, reaction_type='dislike', event_type='reaction', reaction_from=3),
        _row_event_type(message_id=5, reaction_type='dislike', event_type='reaction', reaction_from=4),
        _row_event_type(message_id=6, reaction_type='dislike', event_type='reaction', reaction_from=5),
        _row_event_type(message_id=8, reaction_type='like',    event_type='reaction', reaction_from=6),
    ])

    return data
