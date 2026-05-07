import os
import telebot
import yt_dlp
from telebot import types

TOKEN = '8704054237:AAHW9QMqFQPcInceEvlZ703u5-uBIW3ir-4'
bot = telebot.TeleBot(TOKEN)

AD_TEXT = "" 

if not os.path.exists('downloads'):
    os.makedirs('downloads')

def main_markup():
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🎬 Video (MP4)", callback_data="v_video"))
    markup.add(types.InlineKeyboardButton("🎵 Musiqa (MP3)", callback_data="a_audio"))
    return markup

user_links = {}

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "✨ Xush kelibsiz!\n📥 Link yuboring va formatni tanlang!", parse_mode="Markdown")

@bot.message_handler(func=lambda m: "http" in m.text)
def handle_url(message):
    user_links[message.chat.id] = message.text
    bot.reply_to(message, "💎 Formatni tanlang:", reply_markup=main_markup())

@bot.callback_query_handler(func=lambda call: True)
def download(call):
    chat_id = call.message.chat.id
    url = user_links.get(chat_id)
    is_audio = call.data == "a_audio"
    if not url: return

    bot.edit_message_text("⚡️ Yuklanmoqda...", chat_id, call.message.message_id)
    
    ydl_opts = {
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'format': 'bestaudio/best' if is_audio else 'best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }] if is_audio else [],
        'quiet': True
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            f_path = ydl.prepare_filename(info)
            if is_audio: f_path = f_path.rsplit('.', 1)[0] + '.mp3'
            with open(f_path, 'rb') as f:
                if is_audio: bot.send_audio(chat_id, f)
                else: bot.send_video(chat_id, f)
            os.remove(f_path)
    except Exception:
        bot.send_message(chat_id, "❌ Xatolik yuz berdi!")
    bot.delete_message(chat_id, call.message.message_id)

bot.polling(none_stop=True) 
