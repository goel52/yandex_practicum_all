from datetime import datetime, timedelta
from typing import Dict, List

from mongo_connect import MongoConnect


class CollectionLoader:
    def __init__(self, mc: MongoConnect) -> None:
        self.dbs = mc.client()

    def get_documents(self, collection_name: str) -> List[Dict]:
        default_load_period = datetime.utcnow() - timedelta(days=1)
        filter = {'update_ts': {'$gt': default_load_period.strftime("%Y-%m-%d %H:%M:%S")}}
        docs = list(self.dbs.get_collection(collection_name).find(filter=filter))
        return docs
