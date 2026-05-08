import telebot
import yt_dlp
import os
from telebot import types

# 1. Bot tokeni
BOT_TOKEN = '8704054237:AAHW9QMqFQPcInceEvlZ703u5-uBIw3ir-4'
bot = telebot.TeleBot(BOT_TOKEN)

# 2. Yuklamalar papkasi
if not os.path.exists('downloads'):
    os.makedirs('downloads')

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Salom! YouTube linkini yuboring, men uni professional tarzda yuklab beraman.")

@bot.message_handler(func=lambda m: 'youtube.com' in m.text or 'youtu.be' in m.text)
def handle_link(message):
    markup = types.InlineKeyboardMarkup()
    # Professional yechim: Callback_data ichida linkni emas, 'm' (music) yoki 'v' (video) belgisini yuboramiz
    markup.add(types.InlineKeyboardButton("🎵 Musiqa (MP3)", callback_data="mode_m"))
    markup.add(types.InlineKeyboardButton("🎬 Video (MP4)", callback_data="mode_v"))
    bot.send_message(message.chat.id, "Formatni tanlang:", reply_markup=markup, reply_to_message_id=message.message_id)

@bot.callback_query_handler(func=lambda call: call.data.startswith('mode_'))
def download_choice(call):
    # Linkni xabarning reply qilingan qismidan olamiz
    url = call.message.reply_to_message.text
    mode = 'mp3' if call.data == 'mode_m' else 'mp4'
    
    bot.edit_message_text("Jarayon boshlandi, kuting...", call.message.chat.id, call.message.message_id)
    
    file_id = f"{call.message.chat.id}_{call.message.message_id}"
    outtmpl = f"downloads/{file_id}.%(ext)s"
    
    ydl_opts = {
        'format': 'bestaudio/best' if mode == 'mp3' else 'best[ext=mp4]/best',
        'outtmpl': outtmpl,
        'noplaylist': True,
        'quiet': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            
            with open(filename, 'rb') as f:
                if mode == 'mp3':
                    bot.send_audio(call.message.chat.id, f, caption=info.get('title'))
                else:
                    bot.send_video(call.message.chat.id, f, caption=info.get('title'))
            
            # Professional tozalash: Server xotirasini band qilmaslik uchun
            if os.path.exists(filename):
                os.remove(filename)
                
    except Exception as e:
        bot.send_message(call.message.chat.id, f"Xatolik yuz berdi: {str(e)}")
    finally:
        bot.delete_message(call.message.chat.id, call.message.message_id)

if __name__ == "__main__":
    print("Bot ishga tushdi...")
    bot.polling(none_stop=True)
