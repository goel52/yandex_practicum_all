import json
import os
from datetime import datetime
from typing import List
from urllib.parse import quote_plus as quote

from bson.objectid import ObjectId
from pymongo.mongo_client import MongoClient


class MongoConnect:
    def __init__(self,
                 cert_path: str,
                 user: str,
                 pw: str,
                 hosts: List[str],
                 rs: str,
                 auth_db: str,
                 main_db: str
                 ) -> None:
        self.user = user
        self.pw = pw
        self.hosts = hosts
        self.replica_set = rs
        self.auth_db = auth_db
        self.main_db = main_db
        self.cert_path = cert_path

    def url(self) -> str:
        return 'mongodb://{user}:{pw}@{hosts}/?replicaSet={rs}&authSource={auth_src}'.format(
            user=quote(self.user),
            pw=quote(self.pw),
            hosts=','.join(self.hosts),
            rs=self.replica_set,
            auth_src=self.auth_db)

    def client(self):
        return MongoClient(self.url(), tlsCAFile=self.cert_path)[self.main_db]


def run(data_path: str, mongo_connect: MongoConnect, collection_name: str):

    dbs = mongo_connect.client()

    existing = dbs.list_collection_names()
    if collection_name not in existing:
        dbs.create_collection(collection_name)

    d = []
    with open(data_path) as f:
        d = json.load(f)

    for doc in d:
        doc['_id'] = ObjectId(doc['_id'])
        doc['update_ts'] = datetime.utcnow().replace(microsecond=0)

        filter = {'_id': doc['_id']}
        existing = list(dbs.get_collection(collection_name).find(filter=filter))

        if len(existing) == 0:
            dbs.get_collection(collection_name).insert_one(doc)
        else:
            dbs.get_collection(collection_name).replace_one(filter, doc)

    cnt = dbs.get_collection(collection_name).count_documents({})

    return {
        'statusCode': 200,
        'body': {
            'state': 'CollectionInitialized',
            'cnt': cnt
        },
    }


def handler(event, context):
    cwd = os.getcwd()
    data_path = f'{cwd}/users.json'

    cert_path = str(os.getenv('MONGO_DB_CERTIFICATE_PATH'))
    db_user = str(os.getenv('MONGO_DB_USER'))
    db_pw = str(os.environ.get('MONGO_DB_PASSWORD'))
    rs = str(os.getenv('MONGO_DB_REPLICA_SET'))
    db = str(os.getenv('MONGO_DB_DATABASE_NAME'))
    hosts = str(os.getenv('MONGO_DB_HOSTS')).split(';')

    connector = MongoConnect(cert_path, db_user, db_pw, hosts, rs, db, db)
    return run(data_path, connector, 'users')


# Для отладки.
if __name__ == '__main__':
    resp = handler(None, None)
    print(resp)
