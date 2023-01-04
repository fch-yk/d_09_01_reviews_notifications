import datetime
import requests
from environs import Env
import pprint


def main():
    env = Env()
    env.read_env()
    devman_token = env("DEVMAN_TOKEN")
    url = "https://dvmn.org/api/long_polling/"
    headers = {"Authorization": f"Token {devman_token}"}
    # timestamp = datetime.datetime(2023, 1, 1).timestamp()
    # timestamp = datetime.datetime.now().timestamp()
    timestamp = None

    while True:
        payload = {"timestamp": timestamp}
        response = requests.get(
            url,
            headers=headers,
            params=payload,
            timeout=60
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
        break


if __name__ == "__main__":
    main()
