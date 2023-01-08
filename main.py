import contextlib
import logging
import time

import requests
import telegram
from environs import Env

logger = logging.getLogger(__file__)


def send_review_message(bot, chat_id, new_attempt):
    lesson_title = new_attempt["lesson_title"]
    lesson_url = new_attempt["lesson_url"]
    work = ("The teacher reviewed your work "
            f"[\"{lesson_title}\"\\.]({lesson_url})"
            )
    result = (
        "The teacher liked everything, "
        "you can proceed to the next lesson\\!"
    )
    if new_attempt["is_negative"]:
        result = "Unfortunately, there were errors in your work\\."

    bot.send_message(
        text=f"{work}\n{result}",
        chat_id=chat_id,
        parse_mode=telegram.ParseMode.MARKDOWN_V2
    )


def main():
    env = Env()
    env.read_env()
    devman_token = env("DEVMAN_TOKEN")
    bot_token = env("REVIEW_BOT_TOKEN")
    chat_id = env("TELEGRAM_USER_ID")
    timeout = env.int("REVIEW_REQUEST_TIMEOUT", 100)
    debug_mode = env.bool("DEBUG_MODE", False)
    if debug_mode:
        logging.basicConfig()
        logger.setLevel(logging.DEBUG)

    bot = telegram.Bot(token=bot_token)
    url = "https://dvmn.org/api/long_polling/"
    headers = {"Authorization": f"Token {devman_token}"}
    timestamp = None

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
            reviews = response.json()
            logger.debug("The response: %s", reviews)
            if reviews["status"] == "found":
                for new_attempt in reviews["new_attempts"]:
                    send_review_message(bot, chat_id, new_attempt)

                timestamp = reviews["last_attempt_timestamp"]
            else:
                timestamp = reviews["timestamp_to_request"]

            logger.debug("timestamp for the next request: %s", timestamp)
        except requests.exceptions.ReadTimeout:
            logger.debug("Response timeout.")
        except requests.exceptions.ConnectionError:
            logger.debug("Connection error.")
            time.sleep(5)


if __name__ == "__main__":
    with contextlib.suppress(KeyboardInterrupt):
        main()
