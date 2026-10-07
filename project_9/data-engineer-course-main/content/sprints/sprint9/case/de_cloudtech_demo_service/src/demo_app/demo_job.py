from datetime import datetime
from logging import Logger


class DemoMessageProcessor:
    def __init__(self,
                 logger: Logger) -> None:
        self._logger = logger

    # функция, которая будет вызываться по расписанию.
    def run(self) -> None:
        # Пишем в лог, что джоб был запущен.
        self._logger.info(f"{datetime.utcnow()}: START")

        self._logger.info("Your code: 649542b0a6b597d27015ed71")

        # Пишем в лог, что джоб успешно завершен.
        self._logger.info(f"{datetime.utcnow()}: FINISH")
