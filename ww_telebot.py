import os
import requests
from bs4 import BeautifulSoup
from flask import Flask, request, jsonify

# 1. Telegram Bot Configuration
TOKEN = os.getenv("BOT_TOKEN", "8140465766:AAFcZkbv2uii6m0LVudr55cRHb0eG13t870")
URL = f"https://api.telegram.org/bot{TOKEN}/"

STATION_MAP = {
    "Moulali": 10001, "Sivaramapalle": 10002, "Medchal Industrial area sub-station": 10003,
    "Bornapalli": 10272, "Jagtial": 10303, "Guchibowli": 10308, "Begumpet (IMD Office)": 12007,
    # ... keep the rest of your station map entries here exactly as they are
}

def get_weather_data(station_id=10272):
    """Fetch weather data from website using station ID"""
    try:
        weather_url = f'https://tgdps.telangana.gov.in/live.jsp?s1={station_id}'
        response = requests.get(weather_url, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        table = soup.find('table')
        
        weather_data = {}
        if table:
            for row in table.find_all('tr'):
                cells = row.find_all('td')
                if len(cells) >= 2:
                    label = cells[0].get_text(strip=True)
                    value = cells[1].get_text(strip=True)
                    weather_data[label] = value
        
        location = weather_data.get('AWS Location', 'N/A')
        temp = weather_data.get('Temperature', 'N/A')
        
        return f"Weather Update for {location}:\nTemperature: {temp}°C 🌤️"
    except Exception as e:
        return f"Error fetching weather: {str(e)}"

def get_weather_by_location(location_name):
    """Fetch weather data by location name"""
    location_lower = location_name.lower().strip()
    station_id = None
    
    for loc_key, station in STATION_MAP.items():
        if loc_key.lower() == location_lower:
            station_id = station
            break
            
    if not station_id:
        for loc_key, station in STATION_MAP.items():
            if loc_key.lower() in location_lower or location_lower in loc_key.lower():
                station_id = station
                break
    
    if station_id:
        return get_weather_data(station_id)
    else:
        return f"❌ Location \"{location_name}\" not found. Type 'list' to see valid stations."


# 2. Flask Web Infrastructure (Handles Telegram Webhook Pushes)
app = Flask(__name__)

@app.route("/")
def home():
    return "Warangal Weather Bot is Running via Webhook!"

@app.route("/webhook", methods=["POST"])
def telegram_webhook():
    """Listens for updates pushed directly by Telegram"""
    try:
        update = request.get_json()
        if not update:
            return "No data received", 400

        message = update.get("message")
        if not message:
            return jsonify({"status": "ignored"}), 200

        chat_id = message["chat"]["id"]
        text = message.get("text", "").strip()
        text_lower = text.lower()

        # Extract Comprehensive User Details from Telegram payload
        user_info = message.get("from", {})
        user_id = user_info.get("id", "N/A")
        username = user_info.get("username", "No Username")
        first_name = user_info.get("first_name", "N/A")
        last_name = user_info.get("last_name", "")
        full_name = f"{first_name} {last_name}".strip()

        # 📥 PRINT USER DETAILS & MESSAGE TO TERMINAL LOGS
        print("\n" + "="*60)
        print("📥 NEW TELEGRAM MESSAGE DETECTED")
        print(f"👤 User: {full_name} (@{username})")
        print(f"🆔 User ID: {user_id} | Chat ID: {chat_id}")
        print(f"💬 Message Text: '{text}'")
        print("="*60 + "\n")

        # Auto reply logic
        if text_lower in ["w", "weather update"]:
            reply = get_weather_data()
        elif text_lower == "list":
            locations_list = "\n".join([f"• {loc}" for loc in sorted(STATION_MAP.keys())[:20]])
            reply = f"📍 Available Weather Stations:\n\n{locations_list}\n\nSend any location name to get current weather!"
        else:
            reply = get_weather_by_location(text)

        # Send reply back to Telegram
        requests.get(
            URL + "sendMessage",
            params={
                "chat_id": chat_id,
                "text": reply
            }
        )

    except Exception as e:
        print(f"⚠️ Error processing webhook update: {e}")
        
    return jsonify({"status": "success"}), 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
