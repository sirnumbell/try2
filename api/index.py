import os
import telebot
import google.generativeai as genai
from flask import Flask, request

# Данные берем из переменных среды Vercel
BOT_TOKEN = "8586072127:AAE9tfgdgyBcIHd3T9tCF3bCp5SbC-GyTfA"
GOOGLE_KEY = os.environ.get("GOOGLE_KEY")

app = Flask(__name__)
bot = telebot.TeleBot(BOT_TOKEN, threaded=False)

# Настройка ИИ
if GOOGLE_KEY:
    genai.configure(api_key=GOOGLE_KEY)
    # Используем базовое имя модели
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    model = None

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
        bot.reply_to(message, "❌ Ошибка: Ключ GOOGLE_KEY не найден в настройках Vercel.")
        return
    
    try:
        # Прямой вызов генерации
        response = model.generate_content(message.text)
        
        if response.text:
            bot.reply_to(message, response.text)
        else:
            bot.reply_to(message, "ИИ не смог сформировать ответ. Попробуй другой вопрос.")
            
    except Exception as e:
        # Если снова будет 404, мы увидим подробности
        error_msg = str(e)
        bot.reply_to(message, f"❌ Ошибка API: {error_msg[:100]}")

@app.route('/')
def index():
    return "Bot is running!"
