import os
import time
import threading
import requests
from flask import Flask

# 1. Telegram Bot Configuration
TOKEN = os.getenv("BOT_TOKEN", "8140465766:AAFcZkbv2uii6m0LVudr55cRHb0eG13t870")
URL = f"https://api.telegram.org/bot{TOKEN}/"

def telegram_bot_loop():
    """Main long-polling loop tracking user messages"""
    offset = 0
    print("Telegram bot poller thread started...")
    
    while True:
        try:
            response = requests.get(
                URL + "getUpdates",
                params={
                    "timeout": 100,
                    "offset": offset
                },
                timeout=110
            )

            if response.status_code != 200:
                print(f"API Error: {response.status_code}")
                time.sleep(5)
                continue

            data = response.json()
            
            if not data.get("ok", False):
                print(f"API Error: {data.get('description', 'Unknown error')}")
                time.sleep(5)
                continue
            
            if "result" not in data:
                time.sleep(5)
                continue

            for update in data["result"]:
                offset = update["update_id"] + 1
                message = update.get("message")
                if not message:
                    continue

                chat_id = message["chat"]["id"]
                user = message.get("from", {}).get("username", "Unknown User")
                text = message.get("text", "").strip()
                text_lower = text.lower()

                # LOGS INCOMING REQUEST IN RENDER TERMINAL
                print(f"📥 RECEIVED MESSAGE from @{user} (ID: {chat_id}): '{text}'")

                # Minimal Auto reply logic
                if text_lower == "hi":
                    reply = "Helloooo"
                    
                    # LOGS OUTGOING REPLY IN RENDER TERMINAL
                    print(f"📤 SENDING REPLY to (ID: {chat_id}): {reply}")

                    # Send reply
                    requests.get(
                        URL + "sendMessage",
                        params={
                            "chat_id": chat_id,
                            "text": reply
                        }
                    )

        except Exception as e:
            print(f"⚠️ Loop error: {e}")
            time.sleep(5)
            
        time.sleep(1)


# 2. Flask Web Infrastructure (Keeps Render web service alive)
app = Flask(__name__)

@app.route("/")
def home():
    return "Telegram Bot is Running Natively!"

if __name__ == "__main__":
    # Spins up the fixed loop inside a background thread so it doesn't block Flask
    bot_thread = threading.Thread(target=telegram_bot_loop, daemon=True)
    bot_thread.start()
    
    # Flask runs on the main thread and opens up the required port for Render
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
