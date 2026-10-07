"""Structural checks of the supplied template. Never import or execute the job.

These are recognizable-code checks, not a proof of equivalent DataFrame results.
"""
import ast
import re

FUNCTIONS = ('main', 'input_event_paths', 'get_contacts', 'get_contact_interests',
             'get_subs_interests', 'join_result', 'tag_columns')


def name(node):
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    return ''


def calls(node, method):
    return [n for n in ast.walk(node) if isinstance(n, ast.Call) and name(n.func) == method]


def strings(node):
    return {n.value for n in ast.walk(node)
            if isinstance(n, ast.Constant) and isinstance(n.value, str)}


def names(node):
    return {n.id for n in ast.walk(node) if isinstance(n, ast.Name)}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def assignment(function, variable):
    found = [n.value for n in function.body if isinstance(n, ast.Assign)
             and any(isinstance(t, ast.Name) and t.id == variable for t in n.targets)]
    require(len(found) == 1, f'В main ожидается одно присваивание {variable}.')
    return found[0]


def sql_text(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.JoinedStr):
        return ''.join('{' + ast.unparse(n.value) + '}' if isinstance(n, ast.FormattedValue)
                       else n.value for n in node.values)
    return ''


def where_matches(node, pattern):
    return any(re.search(pattern, sql_text(arg), flags=re.I)
               for call in calls(node, 'where') + calls(node, 'filter') for arg in call.args)


def ordered_rank(function):
    return any(len(call.args) >= 2
               and all(isinstance(arg, ast.Call) and name(arg.func) == 'desc'
                       and column in strings(arg)
                       for arg, column in zip(call.args[:2], ('tag_count', 'tag')))
               for call in calls(function, 'orderBy'))


def has_top_three(function):
    return (bool(calls(function, 'row_number'))
            and any(len(call.args) >= 2 and isinstance(call.args[1], (ast.List, ast.Tuple))
                    and [getattr(n, 'value', None) for n in call.args[1].elts] == [1, 2, 3]
                    for call in calls(function, 'pivot')))


def check_job(source):
    tree = ast.parse(source, filename='connection_interests.py')
    functions = {n.name: n for n in tree.body if isinstance(n, ast.FunctionDef)}
    require(set(FUNCTIONS) <= set(functions), 'Для статической проверки сохраните функции прекода: '
            + ', '.join(FUNCTIONS) + '.')
    main = functions['main']
    variables = ('date', 'days_count', 'events_base_path', 'interests_base_path',
                 'verified_tags_path', 'output_base_path')
    for index, variable in enumerate(variables, 1):
        value = assignment(main, variable)
        if variable == 'days_count' and isinstance(value, ast.Call) and name(value.func) == 'int' and len(value.args) == 1:
            value = value.args[0]
        require(isinstance(value, ast.Subscript) and isinstance(value.value, ast.Attribute)
                and value.value.attr == 'argv' and name(value.value.value) == 'sys'
                and isinstance(value.slice, ast.Constant) and value.slice.value == index,
                f'Аргумент {variable} должен браться из sys.argv[{index}].')

    path_function = functions['input_event_paths']
    require(any(call.args and ('depth' in names(call.args[0])) for call in calls(path_function, 'range'))
            and bool(calls(path_function, 'timedelta'))
            and any(isinstance(n, ast.BinOp) and isinstance(n.op, ast.Sub) for n in ast.walk(path_function))
            and 'base_path' in names(path_function) and any('date=' in s for s in strings(path_function)),
            'input_event_paths должен строить пути от base_path за depth дней назад, начиная с date.')
    messages = assignment(main, 'messages')
    require(any([name(arg) for arg in call.args] == ['events_base_path', 'date', 'days_count']
                for call in calls(messages, 'input_event_paths')) and bool(calls(messages, 'parquet'))
            and where_matches(messages, r"event_type\s*=\s*['\"]message['\"]"),
            'messages должен читать message-события за date/days_count через input_event_paths.')
    direct = assignment(main, 'direct_messages')
    posts = assignment(main, 'posts')
    require('messages' in names(direct) and where_matches(direct, r'event\.message_to\s+is\s+not\s+null'),
            'direct_messages должен отбирать личные сообщения (message_to is not null).')
    require('messages' in names(posts) and where_matches(posts, r'event\.message_channel_to\s+is\s+not\s+null'),
            'posts должен отбирать сообщения каналов (message_channel_to is not null).')
    subscriptions = assignment(main, 'subscriptions')
    require(any(len(call.args) == 1 and name(call.args[0]) == 'events_base_path'
                for call in calls(subscriptions, 'parquet'))
            and where_matches(subscriptions, r"event_type\s*=\s*['\"]subscription['\"]")
            and where_matches(subscriptions, r'date\s*<=\s*[\'\"]?\{date\}'),
            'Подписки нужно читать из всей истории events_base_path до date включительно.')
    interests = assignment(main, 'interests')
    require(any(call.args and sql_text(call.args[0]) == '{interests_base_path}/date={date}'
                for call in calls(interests, 'parquet')),
            'interests должен читать interests_base_path/date=date.')
    verified = assignment(main, 'verified_tags')
    require(any(call.args and name(call.args[0]) == 'verified_tags_path' for call in calls(verified, 'parquet')),
            'verified_tags должен читать переданный актуальный verified_tags_path.')
    result = assignment(main, 'result')
    require(any([name(arg) for arg in call.args] == ['contact_interests', 'subs_interests']
                for call in calls(result, 'join_result')), 'result должен объединять обе части через join_result.')
    require(any(call.args and sql_text(call.args[0]) == '{output_base_path}/date={date}'
                and 'result' in names(call) and any(isinstance(n, ast.Attribute) and n.attr == 'write'
                                                  for n in ast.walk(call))
                for call in calls(main, 'parquet')), 'Запишите result в output_base_path/date=date через write.parquet.')

    contacts = functions['get_contacts']
    require(any(call.args and calls(call.args[0], 'array')
                and {'event.message_from', 'event.message_to'} <= strings(call.args[0])
                for call in calls(contacts, 'explode'))
            and bool(calls(contacts, 'distinct') + calls(contacts, 'dropDuplicates')),
            'get_contacts должен учитывать оба направления и удалять повторные пары контактов.')
    contact = functions['get_contact_interests']
    require(any(call.args and calls(call.args[0], 'array') for call in calls(contact, 'explode'))
            and {'like', 'dislike'} <= strings(contact)
            and any('contact_id' in strings(call) for call in calls(contact, 'countDistinct'))
            and any({'user_id', 'tag'} <= strings(call) for call in calls(contact, 'groupBy')),
            'Объедините top-1/2/3 каждой реакции и считайте различные contact_id для каждого user_id/tag.')
    require(ordered_rank(contact) and has_top_three(contact),
            'Теги контактов ранжируются по tag_count DESC, tag DESC, с top-1/2/3.')
    subs = functions['get_subs_interests']
    require(any('verified_tags' in names(call) and bool({'left_semi', 'leftsemi', 'inner'} & strings(call))
                for call in calls(subs, 'join')),
            'Отфильтруйте теги подписок соединением с verified_tags.')
    require(any(bool({'*', 'tag'} & strings(call)) for call in calls(subs, 'count')),
            'Считайте появления тегов в постах через count, а не countDistinct(user_id, tag).')
    require(ordered_rank(subs) and has_top_three(subs), 'Для подписок ожидаются частоты тегов и top-1/2/3.')
    joined = functions['join_result']
    require(any('subs_interests' in names(call) and bool({'full_outer', 'full', 'outer'} & strings(call))
                for call in calls(joined, 'join')),
            'join_result должен сохранять пользователей обеих частей через full outer join.')
