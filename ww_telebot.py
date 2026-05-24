import os
import time
import threading
import requests
from flask import Flask

# 1. Telegram Bot Configuration
TOKEN = os.getenv("BOT_TOKEN", "8140465766:AAFcZkbv2uii6m0LVudr55cRHb0eG13t870").strip()

# Fixes the "botbot" URL issue dynamically
CLEAN_TOKEN = TOKEN if TOKEN.startswith("bot") else f"bot{TOKEN}"
URL = f"https://api.telegram.org/{CLEAN_TOKEN}/"

def telegram_bot_loop():
    """Main long-polling loop tracking user messages with heavy debugging"""
    offset = 0
    print("🚀 DEBUG: Telegram bot poller thread started successfully...")
    
    while True:
        try:
            print(f"📡 DEBUG: Sending getUpdates request to Telegram (Offset: {offset})...")
            response = requests.get(
                URL + "getUpdates",
                params={
                    "timeout": 30,
                    "offset": offset
                },
                timeout=35
            )

            print(f"📥 DEBUG: HTTP Response Code from getUpdates: {response.status_code}")
            if response.status_code != 200:
                print(f"❌ API Error: Status {response.status_code}. Raw content: {response.text}")
                time.sleep(5)
                continue

            data = response.json()
            print(f"🔍 DEBUG: Full JSON payload received: {data}")
            
            if not data.get("ok", False):
                print(f"❌ Telegram API Error Description: {data.get('description', 'Unknown error')}")
                time.sleep(5)
                continue
            
            if "result" not in data:
                print("⚠️ DEBUG: 'result' key missing from Telegram response.")
                time.sleep(5)
                continue

            updates = data["result"]
            print(f"📊 DEBUG: Found {len(updates)} new update(s) in this batch.")

            for update in updates:
                offset = update["update_id"] + 1
                message = update.get("message")
                if not message:
                    print(f"ℹ️ DEBUG: Skipped update ID {update.get('update_id')} (Not a standard text message).")
                    continue

                chat_id = message["chat"]["id"]
                user = message.get("from", {}).get("username", "Unknown User")
                text = message.get("text", "").strip()
                text_lower = text.lower()

                print(f"📥 RECEIVED MESSAGE from @{user} (ID: {chat_id}): '{text}'")
                print(f"⚙️ DEBUG: Normalized lower-case text evaluated as: '{text_lower}'")

                # Minimal Auto reply logic
                if text_lower == "hi":
                    reply = "Helloooo"
                    print(f"🎯 DEBUG: Match found for 'hi'! Attempting to send reply: '{reply}'")
                    
                    # Send reply
                    print(f"📤 DEBUG: Dispatching sendMessage request to Chat ID {chat_id}...")
                    send_response = requests.get(
                        URL + "sendMessage",
                        params={
                            "chat_id": chat_id,
                            "text": reply
                        }
                    )
                    print(f"📥 DEBUG: sendMessage HTTP Response Code: {send_response.status_code}")
                    print(f"📄 DEBUG: sendMessage JSON response: {send_response.text}")
                else:
                    print(f"🙅‍♂️ DEBUG: Message '{text_lower}' did not match 'hi'. No action taken.")

        except Exception as e:
            print(f"⚠️ Loop error caught in try-except block: {e}")
            import traceback
            traceback.print_exc()
            time.sleep(5)
            
        time.sleep(1)


# 2. Flask Web Infrastructure (Keeps Render web service alive)
app = Flask(__name__)

import sys
import logging
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

@app.route("/")
def home():
    print("🌐 DEBUG: Health check endpoint '/' hit by external service.")
    return "Telegram Bot is Running Natively with Full Debug Logs!"

if __name__ == "__main__":
    print("🛠️ DEBUG: Application initialization started...")
    
    # Spins up the fixed loop inside a background thread so it doesn't block Flask
    bot_thread = threading.Thread(target=telegram_bot_loop, daemon=True)
    bot_thread.start()
    
    # Flask runs on the main thread and opens up the required port for Render
    port = int(os.environ.get("PORT", 10000))
    print(f"🚀 DEBUG: Launching Flask server on port {port}...")
    app.run(host="0.0.0.0", port=port, debug=False)
