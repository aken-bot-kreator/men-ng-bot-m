import os
import telebot
import yt_dlp

TOKEN = 8704054237:AAHW9QMqFQPcInceEvlZ703u5-uBIw3ir-4

bot = telebot.TeleBot(TOKEN)

DOWNLOAD_FOLDER = "downloads"

if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)


@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(
        message,
        "🎵 Universal Media Bot\n\n"
        "YouTube / TikTok / Instagram link yuboring."
    )


# Video yuklash

def download_video(url):

    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'outtmpl': f'{DOWNLOAD_FOLDER}/%(title)s.%(ext)s',
        'merge_output_format': 'mp4',
        'quiet': True,
        'noplaylist': True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        file_path = ydl.prepare_filename(info)

        if not file_path.endswith('.mp4'):
            base = os.path.splitext(file_path)[0]
            mp4_path = base + '.mp4'

            if os.path.exists(mp4_path):
                file_path = mp4_path

        return file_path


# Audio yuklash

def download_audio(url):

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': f'{DOWNLOAD_FOLDER}/%(title)s.%(ext)s',
        'quiet': True,
        'noplaylist': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '320',
        }],
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        title = info['title']
        return f'{DOWNLOAD_FOLDER}/{title}.mp3'


@bot.message_handler(func=lambda m: True)
def downloader(message):

    url = message.text.strip()

    if "http" not in url:
        bot.reply_to(message, "❌ To‘g‘ri link yuboring")
        return

    wait = bot.reply_to(message, "⏳ Yuklanmoqda...")

    try:

        # Audio so‘rasa
        if "mp3" in url.lower():
            audio_path = download_audio(url)

            with open(audio_path, 'rb') as audio:
                bot.send_audio(message.chat.id, audio)

            os.remove(audio_path)

        else:
            video_path = download_video(url)

            with open(video_path, 'rb') as video:
                bot.send_video(message.chat.id, video)

            os.remove(video_path)

        bot.delete_message(message.chat.id, wait.message_id)

    except Exception as e:
        bot.reply_to(message, f"❌ Xato:\n{e}")


print("BOT ISHLADI")
bot.infinity_polling(skip_pending=True)
