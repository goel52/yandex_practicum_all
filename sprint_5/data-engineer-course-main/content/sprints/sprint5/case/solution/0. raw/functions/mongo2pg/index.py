import os

from bson.objectid import ObjectId

from collection_loader import CollectionLoader
from mongo_connect import MongoConnect
from pg_connect import PgConnect
from pg_saver import PgSaver


def parse_object_ids(obj):
    if isinstance(obj, dict):
        data = {}
        for (k, v) in obj.items():
            data[k] = parse_object_ids(v)
        return data
    elif hasattr(obj, "__iter__") and not isinstance(obj, str):
        return [parse_object_ids(v) for v in obj]
    elif isinstance(obj, ObjectId):
        return str(obj)
    else:
        return obj


def run_copy(collection_loader: CollectionLoader, pg_saver: PgSaver, collection: str) -> int:
    data = collection_loader.get_documents(collection)
    print(f"found {len(data)} documents to sync form {collection}")

    pg_saver.init_collection(collection)

    for d in data:
        d_parsed_ids = parse_object_ids(d)
        pg_saver.save_object(collection, str(d["_id"]), d_parsed_ids)

    return len(data)


def handler(event, context):
    cert_path = str(os.getenv('MONGO_DB_CERTIFICATE_PATH'))
    db_user = str(os.getenv('MONGO_DB_USER'))
    db_pw = str(os.environ.get('MONGO_DB_PASSWORD'))
    rs = str(os.getenv('MONGO_DB_REPLICA_SET'))
    db = str(os.getenv('MONGO_DB_DATABASE_NAME'))
    hosts = str(os.getenv('MONGO_DB_HOSTS')).split(';')
    mongo_connect = MongoConnect(cert_path, db_user, db_pw, hosts, rs, db, db)
    collection_loader = CollectionLoader(mongo_connect)

    host = str(os.getenv('PG_WAREHOUSE_HOST'))
    port = int(str(os.getenv('PG_WAREHOUSE_PORT')))
    db_name = str(os.getenv('PG_WAREHOUSE_DATABASE_NAME'))
    user = str(os.getenv('PG_WAREHOUSE_USER'))
    password = str(os.environ.get('PG_WAREHOUSE_PASSWORD'))
    pg_connect = PgConnect(host, port, db_name, user, password)
    pg_saver = PgSaver(pg_connect)

    users_loaded = run_copy(collection_loader, pg_saver, 'users')
    restaurants_loaded = run_copy(collection_loader, pg_saver, 'restaurants')
    orders_loaded = run_copy(collection_loader, pg_saver, 'orders')

    return {
        'statusCode': 200,
        'body': {
            'users_loaded': users_loaded,
            'restaurants_loaded': restaurants_loaded,
            'orders_loaded': orders_loaded
        },
    }


# Для отладки.
if __name__ == '__main__':
    resp = handler(None, None)
    print(resp)
