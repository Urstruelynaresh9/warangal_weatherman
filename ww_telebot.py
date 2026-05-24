import os
import sys
import logging
import requests
from datetime import datetime, timedelta
from flask import Flask, request, jsonify

# --- CONFIGURE RICH LOGGING ---
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# 1. Telegram Bot Configuration
RAW_TOKEN = os.getenv("BOT_TOKEN", "8140465766:AAFcZkbv2uii6m0LVudr55cRHb0eG13t870").strip()

# SAFEGUARD: Strip away any accidental "bot" prefix from Render env variables
if RAW_TOKEN.lower().startswith("bot"):
    TOKEN = RAW_TOKEN[3:]
else:
    TOKEN = RAW_TOKEN

URL = f"https://api.telegram.org/bot{TOKEN}/"


def get_coordinates(village_name):
    """Get coordinates using OpenStreetMap Nominatim API"""
    try:
        search_query = f"{village_name}, Telangana, India"
        logger.debug(f"🔍 Contacting OpenStreetMap for location query: '{search_query}'")
        
        url = "https://nominatim.openstreetmap.org/search"
        params = {"q": search_query, "format": "json", "limit": 1}
        headers = {"User-Agent": "warangal-weatherman-bot"}
        
        response = requests.get(url, params=params, headers=headers, timeout=10)
        data = response.json()
        
        if not data:
            logger.warning(f"❌ Location '{village_name}' not found in Telangana.")
            return None, None, None
        
        place = data[0]
        latitude = float(place["lat"])
        longitude = float(place["lon"])
        display_name = place["display_name"]
        
        logger.info(f"📍 Location resolved: {display_name} -> ({latitude}, {longitude})")
        return latitude, longitude, display_name
    except Exception as e:
        logger.error(f"⚠️ Error getting coordinates from OSM: {e}")
        return None, None, None


def get_weather(latitude, longitude, location):
    """Fetch live weather data using Open-Meteo API"""
    try:
        logger.debug(f"🌐 Requesting atmospheric data from Open-Meteo for ({latitude}, {longitude})...")
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
        
        logger.info(f"🌡️ Weather fetched cleanly for {location}: {temperature}°C")
        
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
        logger.error(f"💥 Failed parsing forecast payload: {e}")
        return f"⚠️ Error fetching weather data points: {str(e)}"


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
            logger.debug("🔔 Received non-message type update. Ignored.")
            return jsonify({"status": "ignored"}), 200

        chat_id = message["chat"]["id"]
        text = message.get("text", "").strip()

        # Extract User Details
        user_info = message.get("from", {})
        username = user_info.get("username", "No Username")
        full_name = f"{user_info.get('first_name', 'User')} {user_info.get('last_name', '')}".strip()

        logger.info(f"💬 Incoming message from {full_name} (@{username}) [Chat ID: {chat_id}]: '{text}'")

        # Command / Message Router Logic
        if not text and not message.get("location"):
            reply = "❌ Please send a valid text message (village/city name) or share a map location."
        elif text and text.lower() in ["/start", "hello", "hi"]:
            reply = "⛅ Welcome to Warangal Weatherman Bot! Send me any village or city name in Telangana to get an instant live weather forecast. Or simply share your current location! 📍"
        else:
            # Check if user shared a map location
            location_data = message.get("location")
            if location_data:
                latitude = location_data["latitude"]
                longitude = location_data["longitude"]
                display_name = f"Shared Location ({latitude:.4f}, {longitude:.4f})"
                logger.info(f"📍 User shared location: {display_name}")
                reply = get_weather(latitude, longitude, display_name)
            elif text:
                # Process geographical query strings (village/city names)
                latitude, longitude, location = get_coordinates(text)
                if latitude and longitude:
                    reply = get_weather(latitude, longitude, location)
                else:
                    reply = f"❌ Could not find location matching: '{text}'. Please try another village/city name."
            else:
                reply = "❌ Please send a valid text message or share a map location."

        # Send response back as a robust POST body
        logger.debug(f"📤 Outbound reply endpoint target: {URL}sendMessage")
        payload = {
            "chat_id": chat_id,
            "text": reply
        }
        send_response = requests.post(f"{URL}sendMessage", json=payload, timeout=10)
        
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
        logger.debug(f"Clearing conflicts at target: {URL}deleteWebhook")
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
