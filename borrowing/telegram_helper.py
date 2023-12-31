import os

import requests
from dotenv import load_dotenv


def send_telegram_message(message):
    load_dotenv()
    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")

    api_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
    }
    response = requests.post(api_url, json=payload)
    if response.status_code != 200:
        print(f"Failed to send Telegram message: {response.text}")
