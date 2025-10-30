import os
import uuid
import shutil
import subprocess
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")

async def handle_audio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    audio = update.message.audio or update.message.voice or update.message.document
    if not audio:
        await update.message.reply_text("Please send an MP3 file.")
        return

    if not audio.mime_type.endswith("mpeg"):
        await update.message.reply_text("Only MP3 files are supported.")
        return

    if audio.file_size > 50 * 1024 * 1024:
        await update.message.reply_text("File size exceeds 50MB limit.")
        return

    await update.message.reply_text("Downloading your file...")
    file = await audio.get_file()
    input_path = "input.mp3"
    await file.download_to_drive(input_path)

    await update.message.reply_text("Separating vocals and instrumentals...")

    session_id = str(uuid.uuid4())
    output_dir = f"output/{session_id}"

    try:
        subprocess.run([
            "spleeter", "separate",
            "-p", "spleeter:2stems",
            "-o", output_dir,
            input_path
        ], check=True)
    except subprocess.CalledProcessError as e:
        await update.message.reply_text(f"Audio processing failed: {e}")
        return

    vocal_path = f"{output_dir}/input/vocals.wav"
    instrumental_path = f"{output_dir}/input/accompaniment.wav"

    await update.message.reply_audio(audio=open(vocal_path, "rb"), caption="🎤 Vocals")
    await update.message.reply_audio(audio=open(instrumental_path, "rb"), caption="🎸 Instrumental")

    await update.message.reply_text("Done! Let me know if you want to process another file.")

    # Cleanup
    os.remove(input_path)
    shutil.rmtree(output_dir)

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.AUDIO | filters.VOICE | filters.Document.AUDIO, handle_audio))
app.run_polling()