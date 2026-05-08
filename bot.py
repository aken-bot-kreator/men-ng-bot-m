import telebot
import yt_dlp
import os
import logging
from telebot import types

# 1. Loglash (Xatolarni terminalda ko'rish uchun)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(name)

# 2. Bot tokeni
BOT_TOKEN = '8704054237:AAHW9QMqFQPcInceEvlZ703u5-uBIw3ir-4'
bot = telebot.TeleBot(BOT_TOKEN)

# Yuklamalar papkasini yaratish
if not os.path.exists('downloads'):
    os.makedirs('downloads', exist_ok=True)

# Foydalanuvchi linklarini vaqtincha saqlash
user_links = {}

# 3. Yuklash sozlamalari
def get_ydl_opts(mode, chat_id):
    if mode == 'video':
        return {
            'format': 'best[ext=mp4]/best',
            'outtmpl': f'downloads/{chat_id}_%(title).50s.%(ext)s',
            'noplaylist': True,
            'quiet': True
        }
    else:
        return {
            'format': 'bestaudio/best',
            'outtmpl': f'downloads/{chat_id}_%(title).50s.%(ext)s',
            'postprocessors': [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3','preferredquality': '192'}],
            'quiet': True
        }

# 4. Start komandasi
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "🌟 Professional Yuklovchi Bot!\n\nInstagram yoki TikTok linkini yuboring.")

# 5. Linklarni qabul qilish
@bot.message_handler(func=lambda m: m.text and m.text.startswith('http'))
def handle_link(message):
    url = message.text
    if any(x in url.lower() for x in ['youtube.com', 'youtu.be', 'shorts']):
        bot.reply_to(message, "⚠️ Kechirasiz, YouTube taqiqlangan.")
        return

    user_links[message.chat.id] = url
    
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("🎥 Video", callback_data="down_video"),
        types.InlineKeyboardButton("🎵 MP3 Audio", callback_data="down_audio")
    )
    bot.send_message(message.chat.id, "Nima sifatida yuklab beray?", reply_markup=markup)

# 6. Yuklash va yuborish (Asosiy jarayon)
@bot.callback_query_handler(func=lambda call: True)
def process_download(call):
    chat_id = call.message.chat.id
    url = user_links.get(chat_id)

    if not url:
        bot.answer_callback_query(call.id, "❌ Link topilmadi!")
        return

    mode = 'video' if call.data == "down_video" else 'audio'
    status_msg = bot.send_message(chat_id, "⏳ Yuklanmoqda... Iltimos kuting.")
    opts = get_ydl_opts(mode, chat_id)
    
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            
            if mode == 'audio':
                base, ext = os.path.splitext(filename)
                filename = base + ".mp3"

        with open(filename, 'rb') as f:
            if mode == 'video':
                bot.send_video(chat_id, f, caption="✅ Video tayyor!")
            else:
                bot.send_audio(chat_id, f, caption="✅ Musiqa tayyor!")
        
        # Serverni tozalash
        if os.path.exists(filename):
            os.remove(filename)
        bot.delete_message(chat_id, status_msg.message_id)

    except Exception as e:
        logger.error(f"Xato: {e}")
        bot.send_message(chat_id, "❌ Xatolik yuz berdi. Havola noto'g'ri bo'lishi mumkin.")

if name == "main":
    bot.infinity_polling()
