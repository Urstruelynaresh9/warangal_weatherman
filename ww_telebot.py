import os
import requests
from flask import Flask, request, jsonify
import telebot

TOKEN = "8140465766:AAFcZkbv2uii6m0LVudr55cRHb0eG13t870" # Use os.environ.get('BOT_TOKEN') in production!
BOT_URL = f"https://api.telegram.org/bot{TOKEN}/"

# If you are using pyTelegramBotAPI:
bot = telebot.TeleBot(TOKEN, threaded=False) # Turn off internal threading

app = Flask(__name__)

# --- YOUR TELEGRAM BOT HANDLERS GO HERE ---
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Welcome to Warangal Weatherman!")

# ... (rest of your bot handlers) ...


# --- NATIVE WEBHOOK ROUTE ---
@app.route('/webhook', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return 'OK', 200
    else:
        return 'Invalid Content-Type', 403


# --- BASE ROUTE FOR RENDER HEALTH CHECKS ---
@app.route('/')
def index():
    return "Warangal Weatherman Bot is running!", 200


# --- AUTOMATIC WEBHOOK SETUP ON STARTUP ---
def set_telegram_webhook():
    # Replace this with your actual live Render URL
    render_url = "https://warangal-weatherman.onrender.com/webhook"
    
    # First, clear any lingering polling/webhook states
    requests.get(f"{BOT_URL}deleteWebhook")
    
    # Set the new webhook URL
    response = requests.post(f"{BOT_URL}setWebhook", json={"url": render_url})
    if response.status_code == 200:
        print("🎉 Telegram Webhook successfully set to:", render_url)
    else:
        print("❌ Failed to set webhook:", response.text)

# Trigger the webhook setup when the script loads
set_telegram_webhook()

if __name__ == '__main__':
    # For local testing only. Render uses WSGI (gunicorn) to run 'app'
    app.run(host='0.0.0.0', port=10000)
