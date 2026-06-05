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
RAW_TOKEN = os.getenv("BOT_TOKEN")

if not RAW_TOKEN:
    logger.critical("🚨 CRITICAL ERROR: 'BOT_TOKEN' environment variable is missing!")
    sys.exit("Error: BOT_TOKEN environment variable not set.")

RAW_TOKEN = RAW_TOKEN.strip()

if RAW_TOKEN.lower().startswith("bot"):
    TOKEN = RAW_TOKEN[3:]
else:
    TOKEN = RAW_TOKEN

URL = f"https://api.telegram.org/bot{TOKEN}/"


def translate_to_telugu(text):
    """Translates given English text to Telugu using a free translation API client"""
    try:
        logger.debug("🔤 Translating message payload to Telugu...")
        # Using a reliable free translation endpoint
        api_url = "https://translate.googleapis.com/translate_a/single"
        params = {
            "client": "gtx",
            "sl": "en",
            "tl": "te",
            "dt": "t",
            "q": text
        }
        response = requests.get(api_url, params=params, timeout=10)
        response.raise_for_status()
        
        # Parse the nested list structure Google returns
        translated_chunks = response.json()[0]
        translated_text = "".join([chunk[0] for chunk in translated_chunks if chunk[0]])
        return translated_text
    except Exception as e:
        logger.error(f"⚠️ Translation failed, falling back to original English text. Error: {e}")
        return text


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

#========= Get Weather ========
def get_weather_back(latitude, longitude, location):
    try:

        weather_url = "https://api.open-meteo.com/v1/forecast"

        params = {
            "latitude": latitude,
            "longitude": longitude,

            # Force ECMWF model
            "models": "ecmwf_ifs025",

            "current": "temperature_2m,wind_speed_10m",

            "hourly": (
                "temperature_2m,"
                "precipitation_probability,"
                "precipitation,"
                "cloud_cover"
            ),

            "forecast_days": 2,
            "timezone": "Asia/Kolkata"
        }

        response = requests.get(
            weather_url,
            params=params,
            timeout=10
        )

        response.raise_for_status()

        data = response.json()

        # -------------------------
        # Current Weather
        # -------------------------

        current = data["current"]

        current_temp = current["temperature_2m"]
        wind_speed = current["wind_speed_10m"]

        weather_time = current["time"]

        current_dt = datetime.fromisoformat(weather_time)

        formatted_time = current_dt.strftime(
            "%Y-%m-%d %I:%M %p IST"
        )

        # -------------------------
        # Hourly Forecast
        # -------------------------

        hourly_times = data["hourly"]["time"]
        hourly_temps = data["hourly"]["temperature_2m"]

        hourly_rain_prob = data["hourly"]["precipitation_probability"]

        hourly_rain_mm = data["hourly"]["precipitation"]

        hourly_cloud = data["hourly"]["cloud_cover"]

        forecast_lines = []

        for i in range(len(hourly_times)):

            forecast_dt = datetime.fromisoformat(
                hourly_times[i]
            )

            if forecast_dt <= current_dt:
                continue

            forecast_time = forecast_dt.strftime(
                "%I:%M %p"
            )

            temp = hourly_temps[i]

            rain_prob = hourly_rain_prob[i]

            rain_mm = hourly_rain_mm[i]

            cloud = hourly_cloud[i]

            # Better rain logic
            if rain_mm >= 10:
                rain_status = "Heavy Rain 🌧"
            elif rain_mm >= 5:
                rain_status = "Moderate Rain ⛈️"
            elif rain_mm >= 1:
                rain_status = "Light Rain 🌦"
            elif rain_prob >= 60:
                rain_status = "Rain Possible ☁️"
            elif cloud >= 70:
                rain_status = "Cloudy 🌥"
            else:
                rain_status = "Dry ☀️"

            forecast_lines.append(
                f"{forecast_time}: "
                f"{temp}°C | "
                f"{rain_mm} mm | "
                f"{rain_status}"
            )

            if len(forecast_lines) >= 12:
                break

        forecast_text = "\n".join(forecast_lines)

        weather_report = f"""
===========================
⛈️ WARANGAL WEATHERMAN ⛈️
===========================
📍Village/City: {location}
━━━━━━━━━━━━━━━━━━━━━━
🕒 Time: {formatted_time}
🌡 Current Temp: {current_temp}°C
💨 Wind Speed: {wind_speed} km/h
🌍 Model: ECMWF IFS
===========================
⏳ Next 12 Hours Forecast
===========================
{forecast_text}
"""

        return weather_report.strip()

    except Exception as e:
        logger.error(
            f"💥 ECMWF fetch failed: {e}",
            exc_info=True
        )

        return f"⚠️ Error fetching weather data: {str(e)}"


def get_weather(latitude, longitude, location):
    """Fetch current weather + next 12 hour forecast using Open-Meteo API"""
    try:
        logger.debug(f"🌐 Requesting weather forecast from Open-Meteo for ({latitude}, {longitude})...")
        
        weather_url = "https://api.open-meteo.com/v1/forecast"

        params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": "temperature_2m,wind_speed_10m",
            "hourly": "temperature_2m,precipitation_probability",
            "forecast_days": 2,
            "timezone": "Asia/Kolkata"
        }

        response = requests.get(weather_url, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()

        # ---------------- CURRENT WEATHER ----------------
        current = data["current"]

        current_temp = current["temperature_2m"]
        wind_speed = current["wind_speed_10m"]
        weather_time = current["time"]

        current_dt = datetime.fromisoformat(weather_time)

        formatted_time = current_dt.strftime("%Y-%m-%d %I:%M %p IST")

        # ---------------- HOURLY FORECAST ----------------
        hourly_times = data["hourly"]["time"]
        hourly_temps = data["hourly"]["temperature_2m"]
        hourly_rain = data["hourly"]["precipitation_probability"]

        forecast_lines = []

        for i in range(len(hourly_times)):

            forecast_dt = datetime.fromisoformat(hourly_times[i])

            # Skip current/past hours
            if forecast_dt <= current_dt:
                continue

            forecast_time = forecast_dt.strftime("%I:%M %p")

            temp = hourly_temps[i]
            rain = hourly_rain[i]

            # Rain status logic
            if rain < 10:
                rain_status = "No Rain❌"
            elif rain < 30:
                rain_status = "Cloudy weather🌤"
            elif rain < 50:
                rain_status = "Lite Rain🌦"
            elif rain < 70:
                rain_status = "Moderate Rain⛈️"
            else:
                rain_status = "Moderate to Heavy Rain🌧"

            forecast_lines.append(
                f"{forecast_time}: {temp}°C - {rain_status}"
            )

            # Limit to next 12 future hours
            if len(forecast_lines) >= 12:
                break

        forecast_text = "\n".join(forecast_lines)

        logger.info(f"🌤 Weather forecast fetched successfully for {location}")

        # ---------------- FINAL MESSAGE ----------------
        weather_text = f"""
===========================
⛈️ WARANGAL WEATHERMAN ⛈️
===========================
📍Village/City:{location}
━━━━━━━━━━━━━━━━━━━━━━
🕒 Time: {formatted_time}
🌡 Current Temp: {current_temp}°C
💨 Wind Speed: {wind_speed} km/h
==========================
⏳ Next 12 Hours Forecast
==========================
{forecast_text}
"""

        return weather_text.strip()

    except Exception as e:
        logger.error(f"💥 Failed fetching weather forecast: {e}", exc_info=True)
        return f"⚠️ Error fetching weather data: {str(e)}"


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
            location_data = message.get("location")
            if location_data:
                latitude = location_data["latitude"]
                longitude = location_data["longitude"]
                display_name = f"Shared Location ({latitude:.4f}, {longitude:.4f})"
                logger.info(f"📍 User shared location: {display_name}")
                reply = get_weather(latitude, longitude, display_name)
            elif text:
                latitude, longitude, location = get_coordinates(text)
                if latitude and longitude:
                    reply = get_weather(latitude, longitude, location)
                else:
                    reply = f"❌ Could not find location matching: '{text}'. Please try another village/city name."
            else:
                reply = "❌ Please send a valid text message or share a map location."

        # TRANSLATION LOGIC:
        # Translate the generated output to Telugu before pushing it out to Telegram
        final_reply = translate_to_telugu(reply)
        #final_reply=reply

        #logger.debug(f"📤 Outbound reply endpoint target: {URL}sendMessage")
        payload = {
            "chat_id": chat_id,
            "text": final_reply
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

set_telegram_webhook()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    logger.info(f"🚀 Launching server instance on port {port}...")
    app.run(host="0.0.0.0", port=port)
