import telebot
from telebot import types
import requests
from flask import Flask
from threading import Thread
import os

# --- CREDENTIALS ---
BOT_TOKEN = '8230498036:AAHHvVrqjPAVzPuww0a2Y7ZPz8YJINHGLS4'
GOOGLE_API_KEY = 'AIzaSyBdww3w_lvPXCnBmVe3FWc4yV-jtgfOxc4'
SEARCH_ENGINE_ID = '2287c31f5b9174d59'

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask('')

# Health check route for Render
@app.route('/')
def home():
    return "Bot is Online!"

def run():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

# Handle /start command
@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        "👋 *Hello! Welcome to PDF Finder Bot.*\n\n"
        "I can help you find PDF files and Web links instantly.\n\n"
        "💡 *How to use:* Just type the name of the book or topic.\n"
        "Example: `Atomic Habits`"
    )
    bot.send_message(message.chat.id, welcome_text, parse_mode='Markdown')

# Handle text messages
@bot.message_handler(func=lambda message: True)
def ask_search_type(message):
    query = message.text
    markup = types.InlineKeyboardMarkup()
    
    # Buttons
    btn_pdf = types.InlineKeyboardButton("📄 Search PDF", callback_data=f"pdf|{query}")
    btn_web = types.InlineKeyboardButton("🌐 Web Search", callback_data=f"web|{query}")
    
    markup.add(btn_pdf, btn_web)
    
    bot.reply_to(
        message, 
        f"🔍 *Search for:* `{query}`\nSelect search type:", 
        reply_markup=markup, 
        parse_mode='Markdown'
    )

# Handle Button Clicks
@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    data = call.data.split('|')
    search_type = data[0]
    query = data[1]
    
    if search_type == "pdf":
        final_query = f"{query} filetype:pdf"
    else:
        final_query = query

    url = f"https://www.googleapis.com/customsearch/v1?key={GOOGLE_API_KEY}&cx={SEARCH_ENGINE_ID}&q={final_query}"
    
    bot.answer_callback_query(call.id, "Searching...")
    
    try:
        response = requests.get(url).json()
        items = response.get('items', [])
        
        if not items:
            bot.edit_message_text("❌ No results found.", call.message.chat.id, call.message.message_id)
            return

        reply = f"✅ *{search_type.upper()} Results:* `{query}`\n\n"
        for i, item in enumerate(items[:5], 1):
            reply += f"{i}. *{item['title']}*\n🔗 [Download/View]({item['link']})\n\n"
        
        bot.edit_message_text(
            reply, 
            call.message.chat.id, 
            call.message.message_id, 
            parse_mode='Markdown', 
            disable_web_page_preview=True
        )
    except Exception as e:
        bot.edit_message_text("⚠️ An error occurred.", call.message.chat.id, call.message.message_id)

if __name__ == "__main__":
    keep_alive()
    print("🚀 Bot is running...")
    bot.infinity_polling()
