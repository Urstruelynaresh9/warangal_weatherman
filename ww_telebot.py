import os
import sys
import logging
import requests
from bs4 import BeautifulSoup
from flask import Flask, request, jsonify

# --- CONFIGURE RICH LOGGING ---
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

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
        logger.debug(f"🌐 Fetching external weather data for Station ID: {station_id}...")
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
        logger.error(f"💥 Error pulling weather from external portal: {e}")
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


# 2. Flask Web Infrastructure
app = Flask(__name__)

@app.route("/")
def home():
    logger.debug("❤️ Health check ping received on root '/'")
    return "Warangal Weather Bot is Running via Webhook!", 200

@app.route("/webhook", methods=["POST"])
def telegram_webhook():
    """Listens for updates pushed directly by Telegram"""
    logger.debug("📥 Received a POST request on /webhook")
    try:
        update = request.get_json()
        if not update:
            logger.warning("⚠️ Received an empty webhook payload.")
            return "No data received", 400

        logger.debug(f"📦 Raw JSON Payload: {update}")

        message = update.get("message")
        if not message:
            logger.debug("🔔 Received non-message type update (e.g. edited message or inline query). Ignored.")
            return jsonify({"status": "ignored"}), 200

        chat_id = message["chat"]["id"]
        text = message.get("text", "").strip()
        text_lower = text.lower()

        # Extract User Details
        user_info = message.get("from", {})
        username = user_info.get("username", "No Username")
        full_name = f"{user_info.get('first_name', 'N/A')} {user_info.get('last_name', '')}".strip()

        logger.info(f"💬 Incoming message from {full_name} (@{username}) [Chat ID: {chat_id}]: '{text}'")

        # Command / Message router logic
        if text_lower in ["/start", "hello", "hi"]:
            reply = "Welcome to Warangal Weatherman! Send me a location name (like 'Jagtial' or 'Moulali') or type 'list' to see stations."
        elif text_lower in ["w", "weather update"]:
            reply = get_weather_data()
        elif text_lower == "list":
            locations_list = "\n".join([f"• {loc}" for loc in sorted(STATION_MAP.keys())[:20]])
            reply = f"📍 Available Weather Stations:\n\n{locations_list}\n\nSend any location name to get current weather!"
        else:
            reply = get_weather_by_location(text)

        # Send reply back via an explicit POST request with proper payload parameters
        logger.debug(f"📤 Sending response back to chat {chat_id}...")
        payload = {
            "chat_id": chat_id,
            "text": reply
        }
        send_response = requests.post(URL + "sendMessage", json=payload, timeout=10)
        
        if send_response.status_code == 200:
            logger.info(f"✅ Successfully replied to Chat ID {chat_id}")
        else:
            logger.error(f"❌ Telegram API rejected message delivery: {send_response.status_code} - {send_response.text}")

    except Exception as e:
        logger.error(f"💥 Critical error processing webhook update: {e}", exc_info=True)
        
    return jsonify({"status": "success"}), 200


# --- AUTOMATIC WEBHOOK SETUP ON STARTUP ---
def set_telegram_webhook():
    render_url = "https://warangal-weatherman.onrender.com/webhook"
    logger.info("⚙️ Starting automatic webhook registration...")
    try:
        logger.debug("Clearing previous hook/polling conflicts...")
        requests.get(f"{URL}deleteWebhook", timeout=10)
        
        logger.info(f"Registering new live destination: {render_url}")
        res = requests.post(f"{URL}setWebhook", json={"url": render_url}, timeout=10)
        if res.status_code == 200:
            logger.info(f"🎉 Webhook locked into Telegram: {render_url}")
        else:
            logger.critical(f"❌ Webhook registration failed: {res.text}")
    except Exception as e:
        logger.critical(f"🚨 Network error establishing communication link: {e}")

# Run registration right as the script is contextually loaded
set_telegram_webhook()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    logger.info(f"🚀 Launching server instance on port {port}...")
    app.run(host="0.0.0.0", port=port)
