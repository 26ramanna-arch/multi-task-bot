import os
import subprocess
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp
from PIL import Image, ImageEnhance
import pytesseract

# --- CONFIGURATION ---
TOKEN = "YOUR_BOT_TOKEN_HERE"

# --- FUNCTIONS ---

# 1. Download Video
async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    await update.message.reply_text("📥 Downloading... please wait.")
    ydl_opts = {'format': 'best', 'outtmpl': 'video.mp4'}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    await update.message.reply_video(video=open('video.mp4', 'rb'))
    os.remove('video.mp4')

# 2. Extract Text (OCR)
async def extract_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = await update.message.photo[-1].get_file()
    await photo.download_to_drive('image.jpg')
    text = pytesseract.image_to_string(Image.open('image.jpg'))
    await update.message.reply_text(f"📝 Extracted Text:\n\n{text if text else 'No text found.'}")
    os.remove('image.jpg')

# 3. Enhance Photo (Basic Sharpness)
async def enhance_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = await update.message.photo[-1].get_file()
    await photo.download_to_drive('input.jpg')
    img = Image.open('input.jpg')
    img = ImageEnhance.Sharpness(img).enhance(2.0)
    img = ImageEnhance.Contrast(img).enhance(1.2)
    img.save('enhanced.jpg')
    await update.message.reply_photo(photo=open('enhanced.jpg', 'rb'))
    os.remove('input.jpg')
    os.remove('enhanced.jpg')

# 4. Remove Music (Mute Video)
async def mute_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    video_file = await update.message.video.get_file()
    await video_file.download_to_drive('input_v.mp4')
    # Use ffmpeg (built-in on most servers) to remove audio
    subprocess.run(['ffmpeg', '-i', 'input_v.mp4', '-an', '-vcodec', 'copy', 'muted.mp4'])
    await update.message.reply_video(video=open('muted.mp4', 'rb'))
    os.remove('input_v.mp4')
    os.remove('muted.mp4')

# --- MAIN RUNNER ---
if __name__ == '__main__':
    app = Application.builder().token(TOKEN).build()
    
    # Handlers
    app.add_handler(MessageHandler(filters.PHOTO & filters.CaptionRegex("enhance"), enhance_photo))
    app.add_handler(MessageHandler(filters.PHOTO, extract_text))
    app.add_handler(MessageHandler(filters.VIDEO, mute_video))
    app.add_handler(MessageHandler(filters.TEXT & filters.Entity("url"), download_video))
    
    print("Bot is running...")
    app.run_polling()
