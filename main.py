import telebot
import requests

# --- Enter your credentials here ---
BOT_TOKEN = '8230498036:AAHHvVrqjPAVzPuww0a2Y7ZPz8YJINHGLS4'
GOOGLE_API_KEY = 'AIzaSyBdww3w_lvPXCnBmVe3FWc4yV-jtgfOxc4'
SEARCH_ENGINE_ID = '2287c31f5b9174d59'

bot = telebot.TeleBot(BOT_TOKEN)

# When the user starts the bot
@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        "📚 *Welcome to PDF Finder Bot!*\n\n"
        "Please type the name of the book you are looking for.\n"
        "Example: `Wings of Fire`"
    )
    bot.send_message(message.chat.id, welcome_text, parse_mode='Markdown')

# Search Logic
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    query = message.text
    # Adding 'filetype:pdf' to restrict search to PDF files
    search_query = f"{query} filetype:pdf"
    
    status_msg = bot.reply_to(message, "🔍 Searching, please wait...")

    # Google Custom Search API URL
    url = f"https://www.googleapis.com/customsearch/v1?key={GOOGLE_API_KEY}&cx={SEARCH_ENGINE_ID}&q={search_query}"

    try:
        response = requests.get(url)
        data = response.json()
        
        # Check for API errors
        if 'error' in data:
            error_msg = data['error'].get('message', 'Unknown Error')
            bot.edit_message_text(f"❌ API Error: {error_msg}", message.chat.id, status_msg.message_id)
            print(f"Detailed API Error: {data}")
            return

        items = data.get('items')

        if not items:
            bot.edit_message_text("😔 Sorry, no files were found. Please check your search engine settings.", message.chat.id, status_msg.message_id)
            return

        # Prepare links
        response_text = f"✅ Results found for *'{query}'*:\n\n"
        for i, item in enumerate(items[:5], 1): 
            title = item.get('title')
            link = item.get('link')
            response_text += f"📄 {i}. *{title}*\n🔗 [Download]({link})\n\n"

        bot.edit_message_text(response_text, message.chat.id, status_msg.message_id, parse_mode='Markdown', disable_web_page_preview=True)

    except Exception as e:
        bot.edit_message_text("⚠️ A technical error occurred.", message.chat.id, status_msg.message_id)
        print(f"System Error: {e}")

# Keep the bot running
print("✅ Bot is running successfully...")
bot.infinity_polling()
