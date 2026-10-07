class StgMessageProcessor:
    def __init__(self,
                 consumer,
                 producer,
                 redis_client,
                 stg_repository,
                 batch_size,
                 logger) -> None:
        self._consumer = consumer
        self._producer = producer
        self._redis = redis_client
        self._stg_repository = stg_repository
        self._batch_size = batch_size
        self._logger = logger

    def run(self):
        pass
