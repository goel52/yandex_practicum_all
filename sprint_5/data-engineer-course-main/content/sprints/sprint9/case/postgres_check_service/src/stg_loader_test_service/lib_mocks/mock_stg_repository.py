from datetime import datetime

from stg_loader.repository import StgRepository


class MockStgRepository(StgRepository):
    def __init__(self) -> None:
        pass

    def order_events_insert(self,
                            object_id: int,
                            object_type: str,
                            sent_dttm: datetime,
                            payload: str
                            ) -> None:
        pass
