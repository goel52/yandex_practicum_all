from datetime import datetime
from typing import Dict

from bson.objectid import ObjectId


class DictUtil:
    @staticmethod
    def to_dict(obj, classkey=None) -> Dict:
        if isinstance(obj, dict):
            data = {}
            for (k, v) in obj.items():
                data[k] = DictUtil.to_dict(v, classkey)
            return data
        elif isinstance(obj, ObjectId):
            return str(obj)  # type: ignore
        elif isinstance(obj, datetime):
            return obj.strftime("%Y-%m-%d %H:%M:%S")  # type: ignore
        elif hasattr(obj, "_ast"):
            return DictUtil.to_dict(obj._ast())
        elif hasattr(obj, "__iter__") and not isinstance(obj, str):
            return [DictUtil.to_dict(v, classkey) for v in obj]  # type: ignore
        elif hasattr(obj, "__dict__"):
            data = dict([(key, DictUtil.to_dict(value, classkey))
                         for key, value in obj.__dict__.items()
                         if not callable(value) and not key.startswith('_')])
            if classkey is not None and hasattr(obj, "__class__"):
                data[classkey] = obj.__class__.__name__  # type: ignore
            return data
        else:
            return obj  # type: ignore
