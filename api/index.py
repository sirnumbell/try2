import os
import telebot
import google.generativeai as genai
from flask import Flask, request

# Берем настройки только из системы
BOT_TOKEN = "8586072127:AAE9tfgdgyBcIHd3T9tCF3bCp5SbC-GyTfA"
# Мы больше НЕ пишем ключ текстом сюда. 
# Бот возьмет его из той переменной GOOGLE_KEY, которую ты добавил в Vercel.
GOOGLE_KEY = os.environ.get("GOOGLE_KEY") 

app = Flask(__name__)
bot = telebot.TeleBot(BOT_TOKEN, threaded=False)

if GOOGLE_KEY:
    genai.configure(api_key=GOOGLE_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')

@app.route('/', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return '', 200
    return 'Forbidden', 403

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    if not GOOGLE_KEY:
        bot.reply_to(message, "❌ Ошибка: Ключ не найден в настройках Vercel!")
        return
    try:
        # Убираем все лишние параметры для теста
        response = model.generate_content(message.text)
        bot.reply_to(message, response.text)
    except Exception as e:
        # Бот выведет ошибку. Если там снова 400 - значит ключ в Vercel скопирован с ошибкой.
        bot.reply_to(message, f"❌ Ошибка API: {str(e)}")

@app.route('/')
def index():
    return "Bot is running!"
