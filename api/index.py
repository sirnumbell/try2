import os
import telebot
import google.generativeai as genai
from flask import Flask, request

# --- НАСТРОЙКИ ---
BOT_TOKEN = "8586072127:AAE9tfgdgyBcIHd3T9tCF3bCp5SbC-GyTfA"
GOOGLE_KEY = "AIzaSyAK-so76Jlcplwp6gHLJmVwQAu2ouA31DI"

# Инициализация ИИ
genai.configure(api_key=GOOGLE_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# Инициализация бота
# threaded=False критически важен для работы внутри Flask на Vercel
bot = telebot.TeleBot(BOT_TOKEN, threaded=False)
app = Flask(__name__)

@app.route('/', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return '', 200
    else:
        return 'Forbidden', 403

@app.route('/')
def index():
    return "Bot is running and waiting for messages!"

# --- ЛОГИКА ОБРАБОТКИ СООБЩЕНИЙ ---
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    try:
        # Запрашиваем ответ у ИИ (stream=False для стабильности на Vercel)
        response = model.generate_content(message.text, stream=False)
        
        if response and response.text:
            bot.reply_to(message, response.text)
        else:
            bot.reply_to(message, "ИИ промолчал. Попробуй другой вопрос.")
            
    except Exception as e:
        # Если будет ошибка, бот напишет её причину прямо в чат
        error_text = str(e)
        print(f"Ошибка: {error_text}")
        bot.reply_to(message, f"❌ Произошла ошибка: {error_text[:100]}")

# Для локального тестирования (на Vercel не используется)
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
