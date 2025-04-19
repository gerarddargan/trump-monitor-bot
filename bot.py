import os
import time
import hashlib
import requests
from bs4 import BeautifulSoup

# === CONFIG ===
URL = "https://trumpdinner.gettrumpmemes.com"
BOT_TOKEN = os.getenv("BOT_TOKEN") or "your_telegram_bot_token"
CHAT_ID = os.getenv("CHAT_ID") or "your_user_id"
CHECK_INTERVAL = 60  # seconds

def get_page_snapshot(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")

        # Full HTML text
        html_content = soup.prettify()

        # Also include JS content inside <script> tags (might contain embedded backend data)
        script_data = "\n".join([s.get_text() for s in soup.find_all("script")])

        full_snapshot = html_content + script_data
        return full_snapshot

    except Exception as e:
        return f"ERROR: {e}"

def hash_content(content):
    return hashlib.sha256(content.encode("utf-8")).hexdigest()

def send_telegram_message(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": msg}
    requests.post(url, data=payload)

def monitor():
    print("Monitoring started...")
    previous_hash = None

    while True:
        try:
            snapshot = get_page_snapshot(URL)
            current_hash = hash_content(snapshot)

            if previous_hash and current_hash != previous_hash:
                send_telegram_message(f"⚠️ Change detected on {URL}")
                print("Change detected. Notification sent.")

            previous_hash = current_hash
            time.sleep(CHECK_INTERVAL)

        except Exception as e:
            send_telegram_message(f"❌ Bot error: {e}")
            print("Error:", e)
            time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    monitor()
