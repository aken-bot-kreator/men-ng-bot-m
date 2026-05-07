import os
import telebot
import yt_dlp
from telebot import types





TOKEN = '8704054237:AAHW9QMqFQPcInceEvlZ703u5-uBIW3ir-4'
bot = telebot.TeleBot(TOKEN)

# Yuklamalar uchun vaqtinchalik papka
if not os.path.exists('downloads'):
    os.makedirs('downloads')

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "👋 Salom! Men universal yuklovchiman.\n\n"
                          "🔗 Menga YouTube, Instagram yoki TikTok linkini yuboring,\n"
                          "men sizga uni yuklab beraman!")

@bot.message_handler(func=lambda m: True)
def handle_link(message):
    url = message.text
    if "http" not in url:
        bot.reply_to(message, "❌ Iltimos, to'g'ri link yuboring!")
        return

    msg = bot.reply_to(message, "⏳ Fayl tayyorlanmoqda, kuting...")

    # Umumiy sozlamalar
    ydl_opts = {
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True,
        'nocheckcertificate': True,
        'geo_bypass': True,
        # Brauzer simulyatsiyasi (blokdan o'tish uchun)
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)

            # Faylni yuborish
            with open(file_path, 'rb') as f:
                if info.get('ext') in ['mp4', 'mkv', 'webm']:
                    bot.send_video(message.chat.id, f, caption=f"✅ Yuklab olindi: {info['title']}")
                else:
                    bot.send_document(message.chat.id, f, caption=f"✅ Yuklab olindi: {info['title']}")

            # Xotirani tozalash
            os.remove(file_path)
            bot.delete_message(message.chat.id, msg.message_id)

    except Exception as e:
        bot.edit_message_text(f"❌ Xatolik: Havola noto'g'ri yoki ushbu sayt qo'llab-quvvatlanmaydi.", message.chat.id, msg.message_id)

bot.polling(none_stop=True)
