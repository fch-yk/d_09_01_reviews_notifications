import contextlib
import logging
import pprint
import time

import requests
import telegram
from environs import Env

logger = logging.getLogger(__file__)


def main():
    logging.basicConfig()
    logger.setLevel(logging.DEBUG)
    env = Env()
    env.read_env()
    devman_token = env("DEVMAN_TOKEN")
    bot_token = env("REVIEW_BOT_TOKEN")
    chat_id = env("TELEGRAM_USER_ID")
    bot = telegram.Bot(token=bot_token)
    url = "https://dvmn.org/api/long_polling/"
    headers = {"Authorization": f"Token {devman_token}"}
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
            timestamp = response_card["last_attempt_timestamp"]
            pprint.pprint(response_card)
            if response_card["status"] == "found":
                bot.send_message(
                    text="The teacher reviewed your work!",
                    chat_id=chat_id
                )
            logger.debug("last_attempt_timestamp: %s", timestamp)
        except requests.exceptions.ReadTimeout:
            logger.debug("Response timeout.")
        except requests.exceptions.ConnectionError:
            logger.debug("Connection error.")
            time.sleep(5)


if __name__ == "__main__":
    with contextlib.suppress(KeyboardInterrupt):
        main()
