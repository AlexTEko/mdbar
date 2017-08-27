import time
from threading import Thread
from datetime import datetime

import jwt
import requests

import logging

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

# token expiration time in seconds
EXPIRATION = 3600
API_URL = "https://api-demo.exante.eu/md/1.0"


class MDApiConnector():
    token = (None, None)
    algo = "HS256"

    def __init__(self, client_id, app_id, key):
        self.client_id = client_id
        self.app_id = app_id
        self.key = key

    def __get_token(self):
        now = datetime.now()

        # if there is token and it's not expired yet
        if self.token[0] and (now - self.token[1]).total_seconds() < EXPIRATION:
            return self.token[0]

        claims = {
            "iss": self.client_id,
            "sub": self.app_id,
            "aud": ["symbols", "ohlc", "crossrates"],
            "iat": int(now.timestamp()),
            "exp": int(now.timestamp()) + EXPIRATION
        }

        new_token = str(jwt.encode(claims, self.key, self.algo), 'utf-8')
        self.token = (new_token, now)

        return new_token

    def __request(self, endpoint, params=None):
        token = self.__get_token()
        try:
            result = requests.get(API_URL + endpoint,
                                  headers={"Authorization": "Bearer %s" % token},
                                  params=params)
            result.raise_for_status()
            return result.json()
        except requests.exceptions.HTTPError:
            return 'HTTPError'

    def get_stocks(self):
        stocks = self.__request("/types/STOCK")
        return {x['ticker']: {"id": x["id"], "exchange": x["exchange"], "description": x["description"]}
                for x in stocks if x.get("country") == "US"}

    def get_last_ohlc_bar(self, symbolId):
        # NB: we use internal symbolId, not ticker

        # 86400 (sec) - day duration
        ohlc = self.__request("/ohlc/%s/60" % symbolId, {"size": 1})
        return ohlc[0]

    def get_crosstates(self, base, to):
        return self.__request("/crossrates/{}/{}".format(base, to))