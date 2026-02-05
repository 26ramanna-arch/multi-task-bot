import os
import yt_dlp
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from PIL import Image, ImageEnhance

# 1. SETUP: This pulls your token from Replit Secrets
TOKEN = os.getenv("BOT_TOKEN")

# --- FEATURE 1: VIDEO DOWNLOADER ---
async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    chat_id = update.message.chat_id
    
    # Check if it's a link
    if "http" not in url:
        return

    status_msg = await update.message.reply_text("⏳ Processing link... please wait.")

    # Settings to bypass blocks and avoid playlists
    ydl_opts = {
        'format': 'best[ext=mp4]/best', # Get MP4 if possible
        'outtmpl': f'video_{chat_id}.mp4',
        'noplaylist': True, # CRITICAL: Stops it from trying to download 991 videos
        'quiet': True,
        # Pretend to be a normal Chrome browser
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        filename = f'video_{chat_id}.mp4'
        await update.message.reply_video(video=open(filename, 'rb'), caption="✅ Here is your video!")
        os.remove(filename) # Delete file after sending to save space
        await status_msg.delete()

    except Exception as e:
        error_text = str(e)
        if "429" in error_text:
            await update.message.reply_text("❌ YouTube Error 429: Replit's server is being rate-limited. Try again in 10 minutes or use a TikTok/Instagram link.")
        else:
            await update.message.reply_text(f"❌ Failed to download. Error: {error_text[:100]}")

# --- FEATURE 2: PHOTO ENHANCER ---
async def enhance_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.photo:
        return

    await update.message.reply_text("🪄 Enhancing photo...")
    
    # Download the photo
    photo_file = await update.message.photo[-1].get_file()
    path = "input.jpg"
    await photo_file.download_to_drive(path)
    
    # Open and process
    img = Image.open(path)
    # Increase Sharpness (2.0 = double sharpness)
    img = ImageEnhance.Sharpness(img).enhance(2.0)
    # Increase Contrast
    img = ImageEnhance.Contrast(img).enhance(1.2)
    
    enhanced_path = "enhanced.jpg"
    img.save(enhanced_path)
    
    await update.message.reply_photo(photo=open(enhanced_path, 'rb'), caption="✅ Enhanced!")
    
    # Cleanup
    os.remove(path)
    os.remove(enhanced_path)

# --- MAIN ENGINE ---
async def main_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text:
        await download_video(update, context)
    elif update.message.photo:
        await enhance_image(update, context)

if __name__ == '__main__':
    if not TOKEN:
        print("❌ ERROR: Set BOT_TOKEN in Replit Secrets first!")
    else:
        print("🚀 Bot is starting...")
        app = Application.builder().token(TOKEN).build()
        app.add_handler(MessageHandler(filters.ALL, main_handler))
        app.run_polling()
