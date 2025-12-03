import telebot
from flask import Flask, request
import os
import random

# 1. Configuration
BOT_TOKEN = os.environ.get('BOT_TOKEN')
URL = os.environ.get('RENDER_EXTERNAL_URL') 

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

# --- BOT LOGIC ---

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    # Plain text instructions
    instructions = (
        "👋 I am ready!\n\n"
        "Send /pair followed by your list to generate matches.\n\n"
        "Example:\n"
        "/pair\n"
        "09060396364 – Kelvin\n"
        "09072478435 – Charles"
    )
    bot.reply_to(message, instructions)

@bot.message_handler(commands=['pair'])
def pair_players(message):
    # 1. Clean the input (Remove "/pair")
    text = message.text.replace("/pair", "").strip()
    
    if not text:
        bot.reply_to(message, "⚠️ Please provide a list of players.")
        return

    # 2. Split by Newlines (Standard strict splitting)
    raw_lines = text.splitlines()
    
    # 3. Clean the list (Filter empty lines)
    players = [line.strip() for line in raw_lines if line.strip()]

    if len(players) < 2:
        bot.reply_to(message, "⚠️ You only sent 1 player! I need at least 2 to make a match.")
        return

    # 4. Shuffle
    random.shuffle(players)

    # 5. Create Message (Plain Text Format)
    response = "🎮 TOURNAMENT MATCHES 🎮\n\n"
    match_count = 1
    
    for i in range(0, len(players), 2):
        p1 = players[i]
        
        if i + 1 < len(players):
            p2 = players[i+1]
            
            # EXACT FORMAT YOU REQUESTED:
            response += f"Match {match_count}:\n"
            response += f"📞 {p1}\n"
            response += f"\nVs\n\n"
            response += f"📞 {p2}\n"
            response += "------------------\n" # Separator for clarity
            match_count += 1
        else:
            response += f"🚨 BYE (No Opponent):\n📞 {p1}\n"

    # 6. Send as Plain Text (No parse_mode = No crashes on special chars)
    bot.reply_to(message, response)

# --- WEBHOOK CONFIGURATION ---

@app.route('/' + BOT_TOKEN, methods=['POST'])
def getMessage():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200

@app.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url=URL + "/" + BOT_TOKEN)
    return "✅ Webhook reset!", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))