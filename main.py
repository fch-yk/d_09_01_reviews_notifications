import requests
from environs import Env
import pprint


def main():
    env = Env()
    env.read_env()
    devman_token = env("DEVMAN_TOKEN")
    url = "https://dvmn.org/api/user_reviews/"
    headers = {"Authorization": f"Token {devman_token}"}
    response = requests.get(url, headers=headers, timeout=28)
    response.raise_for_status()
    pprint.pprint(response.json())


if __name__ == "__main__":
    main()
