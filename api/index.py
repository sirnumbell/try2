import os
import telebot
import google.generativeai as genai
from flask import Flask, request

# Настройки
BOT_TOKEN = "8586072127:AAE9tfgdgyBcIHd3T9tCF3bCp5SbC-GyTfA"
GOOGLE_KEY = "AIzaSyDnyckWdUCI_sVGwx3uqX-tNCVJ92_p8jg"

# Инициализация
genai.configure(api_key=GOOGLE_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')
bot = telebot.TeleBot(BOT_TOKEN, threaded=False)
app = Flask(__name__)

@app.route('/', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return ''
    else:
        return 'Invalid request', 403

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    try:
        response = model.generate_content(message.text)
        bot.reply_to(message, response.text)
    except Exception as e:
        bot.reply_to(message, "Ошибка нейросети. Попробуй позже.")

@app.route('/')
def index():
    return "Bot is running!"
