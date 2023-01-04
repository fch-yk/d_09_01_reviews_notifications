import contextlib
import datetime
import logging
import pprint
import time

import requests
from environs import Env

logger = logging.getLogger(__file__)


def main():
    logging.basicConfig()
    logger.setLevel(logging.DEBUG)
    env = Env()
    env.read_env()
    devman_token = env("DEVMAN_TOKEN")
    url = "https://dvmn.org/api/long_polling/"
    headers = {"Authorization": f"Token {devman_token}"}
    # timestamp = datetime.datetime(2023, 1, 1).timestamp()
    # timestamp = datetime.datetime.now().timestamp()
    timestamp = None
    timeout = 15

    while True:
        try:
            payload = {"timestamp": timestamp}
            response = requests.get(
                url,
                headers=headers,
                params=payload,
                timeout=timeout
            )
            response.raise_for_status()
            response_card = response.json()
            last_attempt_timestamp = response_card["last_attempt_timestamp"]
            pprint.pprint(response_card)
            print("last_attempt_timestamp:", last_attempt_timestamp)
            print(
                "last attempt date:",
                datetime.datetime.fromtimestamp(last_attempt_timestamp)
            )
        except requests.exceptions.ReadTimeout:
            logger.debug("Response timeout.")
        except requests.exceptions.ConnectionError:
            logger.debug("Connection error.")
            time.sleep(5)


if __name__ == "__main__":
    with contextlib.suppress(KeyboardInterrupt):
        main()
