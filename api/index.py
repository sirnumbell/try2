import os
import telebot
import google.generativeai as genai
from flask import Flask, request

# Данные из настроек Vercel
BOT_TOKEN = "8586072127:AAE9tfgdgyBcIHd3T9tCF3bCp5SbC-GyTfA"
GOOGLE_KEY = os.environ.get("GOOGLE_KEY")

app = Flask(__name__)
bot = telebot.TeleBot(BOT_TOKEN, threaded=False)

# Настройка ИИ с принудительным выбором версии
if GOOGLE_KEY:
    genai.configure(api_key=GOOGLE_KEY)
    # Инициализируем модель через актуальный метод
    model = genai.GenerativeModel(
        model_name='gemini-1.5-flash'
    )
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
    if not model:
        bot.reply_to(message, "❌ Ошибка: Модель ИИ не инициализирована (проверьте GOOGLE_KEY).")
        return
    
    try:
        # Самый простой способ генерации без лишних аргументов
        response = model.generate_content(message.text)
        
        if response and response.text:
            bot.reply_to(message, response.text)
        else:
            bot.reply_to(message, "ИИ не смог дать ответ на этот запрос.")
            
    except Exception as e:
        # Теперь мы увидим более детальную ошибку
        bot.reply_to(message, f"❌ Ошибка API: {str(e)[:150]}")

@app.route('/')
def index():
    return "Bot status: Running"
