def input_paths(base_input_path, date, depth, event_type='message'):
    dt = datetime.strptime(date, '%Y-%m-%d')
    dt_last = datetime.strptime('2021-09-18', '%Y-%m-%d')
    return [
        f"{base_input_path}/date={(dt - timedelta(days=x)).strftime('%Y-%m-%d')}/event_type={event_type}"
        for x in range(int(depth)) if dt_last < (dt - timedelta(days=x))
    ]


def reaction_tag_tops(date, depth, session):
    """Рассчитывает метрики по постам, к которым пользователь поставил реакцию (лайк или дизлайк)

    Args:
        date (_type_): дата
        depth (_type_): глубина входных данных в днях
        spark_session (_type_): Spark-сессия

    Returns:
    датафрейм с топ 1–3 тегов в постах самого пользователя и следующими колонками:
    - user_id — id пользователя;
    - like_tag_top_1 — top-1 тег в лайках пользователя за заданный период;
    - like_tag_top_2 — top-2 тег в лайках;
    - like_tag_top_3 — top-3 тег в лайках;
    - dislike_tag_top_1 — top-1 тег в дизлайках пользователя за заданный период;
    - dislike_tag_top_2 — top-2 тег в дизлайках;
    - dislike_tag_top_3 — top-3 тег в дизлайках.
    """
    base_input_path = '/user/evgenyvese/data/events'

    reactions_paths = input_paths(base_input_path, date, depth, event_type='reaction')
    reactions = session.read.parquet(reactions_paths) \
        .selectExpr(["event.reaction_from as user_id", "event.reaction_type", "event.message_id"]) \
 \
            messages_paths = input_paths(base_input_path, date, 1000, event_type='message')
    all_message_tags = session.read.parquet(messages_paths) \
        .selectExpr(["event.message_id", "explode(event.tags) as tag"])

    reaction_tags = reactions.join(all_message_tags, 'message_id', how='inner')

    window = Window().partitionBy(['user_id', 'reaction_type']).orderBy(F.desc('cnt'), F.desc('tag'))

    reaction_tops = reaction_tags.groupBy(["user_id", "reaction_type", "tag"]).agg(F.expr("count(tag) as cnt")) \
        .withColumn("rank", F.rank().over(window)) \
        .where('rank <= 3').groupBy(['user_id', 'reaction_type']).pivot('rank').agg(F.expr("first(tag)"))

    like_tops = reaction_tops.filter(F.col('reaction_type') == 'like') \
        .selectExpr(["user_id", "1 as like_tag_top_1", "2 as like_tag_top_2", "3 as like_tag_top_3"])

    dislike_tops = reaction_tops.filter(F.col('reaction_type') == 'dislike') \
        .selectExpr(["user_id", "1 as dislike_tag_top_1", "2 as dislike_tag_top_2", "3 as dislike_tag_top_3"])

    result = like_tops.join(dislike_tops, 'user_id', how='outer') \
 \
            return result
