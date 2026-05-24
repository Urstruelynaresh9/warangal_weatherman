import os
import time
import requests
from datetime import datetime, timedelta

# 1. Telegram Bot Configuration
TOKEN = os.getenv("BOT_TOKEN", "8140465766:AAFcZkbv2uii6m0LVudr55cRHb0eG13t870")
URL = f"https://api.telegram.org/bot{TOKEN}/"

def get_coordinates(village_name):
    """
    Get coordinates using OpenStreetMap Nominatim API
    Hardcoded to search in Telangana, India for better results
    """
    try:
        # Hardcoded Telangana + India to prioritize local results
        search_query = f"{village_name}, Telangana, India"
        
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            "q": search_query,
            "format": "json",
            "limit": 1
        }
        headers = {
            "User-Agent": "warangal-weatherman-bot"
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=10)
        data = response.json()
        
        if not data:
            print(f"❌ Location '{village_name}' not found in Telangana.")
            return None, None, None
        
        place = data[0]
        latitude = float(place["lat"])
        longitude = float(place["lon"])
        display_name = place["display_name"]
        
        print(f"✅ Location found: {display_name}")
        return latitude, longitude, display_name
    except Exception as e:
        print(f"⚠️ Error getting coordinates: {str(e)}")
        return None, None, None

def get_weather(latitude, longitude, location):
    """Fetch live weather data using Open-Meteo API"""
    try:
        weather_url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "current_weather": True
        }
        
        response = requests.get(weather_url, params=params, timeout=10)
        data = response.json()
        
        current = data["current_weather"]
        temperature = current["temperature"]
        windspeed = current["windspeed"]
        weather_time = current["time"]
        
        # Convert UTC time to IST (GMT+5:30)
        utc_time = datetime.strptime(weather_time, "%Y-%m-%dT%H:%M")
        ist_time = utc_time + timedelta(hours=5, minutes=30)
        formatted_time = ist_time.strftime("%Y-%m-%d %I:%M %p IST")
        
        print(f"✅ Weather data retrieved for {location}: {temperature}°C")
        
        weather_text = f"""============================
WARANGAL WEATHERMAN BOT
============================
Weather Update for {location}
━━━━━━━━━━━━━━━━━━━━━━
⏰ Time: {formatted_time}
🌡️ Temperature: {temperature}°C
💨 Wind Speed: {windspeed} km/h
━━━━━━━━━━━━━━━━━━━━━━"""

        return weather_text
    except Exception as e:
        print(f"⚠️ Error fetching weather: {str(e)}")
        return f"⚠️ Error fetching weather: {str(e)}"

def telegram_bot_loop():
    """Main long-polling loop for Telegram bot"""
    offset = 0
    print("\n" + "="*60)
    print("⛅ WARANGAL WEATHERMAN BOT ⛅")
    print("="*60)
    print("🤖 Warangal Weather Bot starting...")
    print(f"📡 Using long polling to listen for messages")
    print(f"🔗 Bot token: {TOKEN[:20]}...")
    print("✅ Bot is ready to receive messages!\n")
    
    # Delete any existing webhook to avoid 409 Conflict
    try:
        webhook_response = requests.get(URL + "deleteWebhook", timeout=10)
        if webhook_response.status_code == 200:
            print("✓ Webhook deleted successfully\n")
    except Exception as e:
        print(f"⚠️ Could not delete webhook: {e}\n")

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
                print(f"❌ API Error: {response.status_code}")
                time.sleep(5)
                continue

            data = response.json()
            
            if not data.get("ok", False):
                print(f"❌ API Error: {data.get('description', 'Unknown error')}")
                time.sleep(5)
                continue
            
            if "result" not in data:
                time.sleep(1)
                continue

            for update in data["result"]:
                offset = update["update_id"] + 1
                message = update.get("message")

                if not message:
                    continue

                chat_id = message["chat"]["id"]
                text = message.get("text", "").strip()
                text_lower = text.lower()

                # Extract user details
                user_info = message.get("from", {})
                username = user_info.get("username", "Unknown User")
                first_name = user_info.get("first_name", "User")

                print("\n" + "="*60)
                print(f"📥 NEW MESSAGE from @{username} ({first_name})")
                print(f"💬 Message: '{text}'")
                print("="*60)

                # Process village name
                if text.strip():
                    print(f"🔍 Searching weather for: {text}")
                    latitude, longitude, location = get_coordinates(text)
                    
                    if latitude and longitude:
                        reply = get_weather(latitude, longitude, location)
                    else:
                        reply = f"❌ Could not find location: '{text}'. Please try another village/city name."
                else:
                    reply = f"❌ Please send a village or city name to get weather information."

                # Send reply to Telegram
                try:
                    requests.get(
                        URL + "sendMessage",
                        params={
                            "chat_id": chat_id,
                            "text": reply
                        }
                    )
                    print(f"✅ Reply sent!\n")
                except Exception as e:
                    print(f"❌ Error sending reply: {e}\n")

            time.sleep(1)

        except Exception as e:
            print(f"⚠️ Error in polling loop: {e}")
            time.sleep(5)

if __name__ == "__main__":
    telegram_bot_loop()
