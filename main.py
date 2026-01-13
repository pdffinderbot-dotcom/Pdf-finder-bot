import telebot
import requests
from flask import Flask
from threading import Thread
import os

# --- നിങ്ങളുടെ വിവരങ്ങൾ ഇവിടെ ചേർക്കുക ---
BOT_TOKEN = '8230498036:AAHHvVrqjPAVzPuww0a2Y7ZPz8YJINHGLS4'
GOOGLE_API_KEY = 'AIzaSyBdww3w_lvPXCnBmVe3FWc4yV-jtgfOxc4'
SEARCH_ENGINE_ID = '2287c31f5b9174d59'

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask('')

# Render-ൽ സ്ലീപ്പ് മോഡ് ഒഴിവാക്കാനുള്ള Flask സർവർ
@app.route('/')
def home():
    return "PDF Finder Bot is Running!"

def run():
    # Render നൽകുന്ന പോർട്ടിൽ സർവർ പ്രവർത്തിപ്പിക്കുന്നു
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

# Start Command
@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        "✨ **PDF Finder Bot**-ലേക്ക് സ്വാഗതം! ✨\n\n"
        "നിങ്ങൾക്ക് ആവശ്യമുള്ള പുസ്തകത്തിന്റെ പേര് അയക്കൂ. "
        "ഞാൻ ഇന്റർനെറ്റിൽ സെർച്ച് ചെയ്ത് ലിങ്കുകൾ നൽകാം. 🔎\n\n"
        "💡 **Example:** `The Alchemist`"
    )
    bot.send_message(message.chat.id, welcome_text, parse_mode='Markdown')

# Search Handler
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    query = f"{message.text} filetype:pdf"
    status_msg = bot.reply_to(message, "🔍 തിരയുകയാണ്...")
    
    url = f"https://www.googleapis.com/customsearch/v1?key={GOOGLE_API_KEY}&cx={SEARCH_ENGINE_ID}&q={query}"
    
    try:
        response = requests.get(url).json()
        items = response.get('items', [])
        
        if not items:
            bot.edit_message_text("😔 ഫയലുകളൊന്നും കണ്ടെത്താനായില്ല.", message.chat.id, status_msg.message_id)
            return

        reply = "✅ **കണ്ടെത്തിയ ഫയലുകൾ:**\n\n"
        for i, item in enumerate(items[:5], 1):
            reply += f"📄 {i}. {item['title']}\n🔗 [Download Now]({item['link']})\n\n"
        
        bot.edit_message_text(reply, message.chat.id, status_msg.message_id, parse_mode='Markdown', disable_web_page_preview=True)
    except Exception as e:
        print(f"Error: {e}")
        bot.edit_message_text("⚠️ ഒരു സാങ്കേതിക തകരാർ സംഭവിച്ചു.", message.chat.id, status_msg.message_id)

# സർവറും ബോട്ടും ഒരേസമയം പ്രവർത്തിപ്പിക്കുന്നു
if __name__ == "__main__":
    keep_alive()
    print("✅ ബോട്ട് ഓൺലൈൻ ആയിക്കഴിഞ്ഞു!")
    bot.infinity_polling()
