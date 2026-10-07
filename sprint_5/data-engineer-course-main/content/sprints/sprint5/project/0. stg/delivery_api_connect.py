from logging import Logger
from typing import Dict, List
from urllib.parse import urljoin

import requests


class DeliveryApiConnect:
    COURIERS = 'couriers'
    DELIVERIES = 'deliveries'

    def __init__(self, host: str, api_key: str, nick: str, cohort: str, logger: Logger) -> None:
        self.host = host
        self.api_key = api_key
        self.nickname = nick
        self.cohort = cohort
        self.logger = logger

    def _headers(self):
        return {
            'X-Api-Key': self.api_key,
            'X-Nickname': self.nickname,
            'X-Cohort': self.cohort
        }

    def get_couriers(self, page: int) -> List[Dict]:
        headers = self._headers()
        url = urljoin(self.host, self.COURIERS)

        page_size = 50
        params = {'offset': page_size * page, 'limit': page_size}

        r = requests.get(url, params=params, headers=headers)
        self.logger.debug(r.json())

        payload = r.json()
        self.logger.debug(payload[:1])

        return payload

    def get_deliveries(self):
        pass
