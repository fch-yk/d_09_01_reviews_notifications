import contextlib
import logging
import time

import requests
import telegram
from environs import Env

logger = logging.getLogger(__file__)


def send_review_message(bot, chat_id, new_attempt):
    result = (
        "The teacher liked everything, "
        "you can proceed to the next lesson."
    )
    lesson_title = new_attempt["lesson_title"]
    work = f"The teacher reviewed your work \"{lesson_title}\"."
    if new_attempt["is_negative"]:
        result = "Unfortunately, there were errors in your work."
    bot.send_message(text=f"{work}\n{result}", chat_id=chat_id)


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
            if response_card["status"] == "found":
                for new_attempt in response_card["new_attempts"]:
                    send_review_message(bot, chat_id, new_attempt)

            timestamp = response_card["last_attempt_timestamp"]
            logger.debug("last_attempt_timestamp: %s", timestamp)
        except requests.exceptions.ReadTimeout:
            logger.debug("Response timeout.")
        except requests.exceptions.ConnectionError:
            logger.debug("Connection error.")
            time.sleep(5)


if __name__ == "__main__":
    with contextlib.suppress(KeyboardInterrupt):
        main()
