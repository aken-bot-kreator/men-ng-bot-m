import os
import telebot
import yt_dlp

TOKEN = '8704054237:AAHW9QMqFQPcInceEvlZ703u5-uBIw3ir-4'
ADMIN_ID = 5016370205

bot = telebot.TeleBot(TOKEN)

if not os.path.exists('downloads'):
    os.makedirs('downloads')

def send_error_to_admin(error_msg, username="Noma'lum"):
    try:
        text = f"🚨 Botda Xatolik!\n\n👤 Foydalanuvchi: @{username}\nXato matni: {error_msg}"
        bot.send_message(ADMIN_ID, text)
    except Exception as e:
        print(f"Adminga xabar yuborishda xato: {e}")

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "👋 Salom! Menga musiqa nomini yoki YouTube/TikTok linkini yuboring, men sizga yuklab beraman!")

@bot.message_handler(func=lambda message: True, content_types=['text'])
def handle_text(message):
    chat_id = message.chat.id
    user_input = message.text
    username = message.from_user.username or "NoUsername"
    
    status_msg = bot.send_message(chat_id, "🔍 Qidirilmoqda/Yuklanmoqda, iltimos kuting...")
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'quiet': True,
        'noplaylist': True
    }
    
    if not (user_input.startswith('http://') or user_input.startswith('https://')):
        ydl_opts['default_search'] = 'ytsearch1'
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(user_input, download=True)
            video_info = info['entries'] if 'entries' in info else info
            
            title = video_info.get('title', 'musiqa')
            filename = ydl.prepare_filename(video_info)
            
            with open(filename, 'rb') as audio:
                bot.send_audio(chat_id, audio, caption=f"🎵 {title}")
            
            if os.path.exists(filename):
                os.remove(filename)
            bot.delete_message(chat_id, status_msg.message_id)
            
    except Exception as e:
        bot.edit_message_text("❌ Kechirasiz, musiqa topilmadi.", chat_id, status_msg.message_id)
        send_error_to_admin(str(e), username)

@bot.message_handler(content_types=['voice', 'audio'])
def handle_voice(message):
    chat_id = message.chat.id
    username = message.from_user.username or "NoUsername"
    status_msg = bot.send_message(chat_id, "🎙 Ovozli xabar qabul qilindi...")
    try:
        bot.edit_message_text("❌ Ovozli qidiruv (Sazan) tizimi faqat serverda ishlaydi.", chat_id, status_msg.message_id)
    except Exception as e:
        send_error_to_admin(str(e), username)

# Muammoli qator olib tashlandi, eng ishonchli ishga tushirish:
print("Bot 100% muvaffaqiyatli ishga tushdi...")
bot.infinity_polling()