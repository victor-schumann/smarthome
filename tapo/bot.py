#!/usr/bin/env python3
import os
import asyncio
import signal
import contextlib
from tapo import ApiClient
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
)
from telegram.request import HTTPXRequest
from dotenv import load_dotenv

# --- Load environment ---
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = int(os.getenv("TELEGRAM_CHAT_ID"))
TAPO_IP = os.getenv("TAPO_IP")          # e.g. "192.168.1.55"
TAPO_MODEL = os.getenv("TAPO_MODEL")    # "p100" or "p110"
TAPO_USER = os.getenv("TAPO_EMAIL") or os.getenv("TAPO_USERNAME")
TAPO_PASS = os.getenv("TAPO_PASSWORD")

# ------------------- IRRIGATION LOGIC -------------------

async def toggle_tapo(duration: int) -> str:
    if not (TAPO_IP and TAPO_MODEL and TAPO_USER and TAPO_PASS):
        return "❌ Missing TAPO_IP, TAPO_MODEL, TAPO_EMAIL/USERNAME, or TAPO_PASSWORD in .env"

    try:
        client = ApiClient(TAPO_USER, TAPO_PASS)
        device = await getattr(client, TAPO_MODEL.lower())(TAPO_IP)

        info = await device.get_device_info()
        is_on = bool(getattr(info, "device_on", False))

        if is_on:
            await device.off()
            action = "ON → OFF → ON"
        else:
            await device.on()
            action = "OFF → ON → OFF"

        # Keep irrigation running for given duration
        await asyncio.sleep(duration)

        # Restore original state
        if is_on:
            await device.on()
        else:
            await device.off()

        return f"🌱 Irrigation ran for {duration}s.."

    except Exception as e:
        return f"❌ Error talking to Tapo device: {e}"

# ------------------- TELEGRAM HANDLERS -------------------

async def home(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != TELEGRAM_CHAT_ID:
        return
    keyboard = [
        [InlineKeyboardButton("💧 Irrigation", callback_data="irrigation")],
        [InlineKeyboardButton("❌ Cancel", callback_data="cancel")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("🏠 Home Menu:", reply_markup=reply_markup)

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "cancel":
        await query.edit_message_text("❌ Cancelled.")
        return

    # Irrigation submenu
    if data == "irrigation":
        keyboard = [
            [InlineKeyboardButton("5s", callback_data="irrigation:5"),
             InlineKeyboardButton("20s", callback_data="irrigation:20")],
            [InlineKeyboardButton("30s", callback_data="irrigation:30"),
             InlineKeyboardButton("60s", callback_data="irrigation:60")],
            [InlineKeyboardButton("❌ Cancel", callback_data="cancel")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("💧 Choose irrigation duration:", reply_markup=reply_markup)
        return

    # Handle irrigation duration
    if data.startswith("irrigation:"):
        _, sec = data.split(":")
        sec = int(sec)

        await query.edit_message_text(f"🌱 Starting irrigation for {sec} seconds...")

        try:
            output = await toggle_tapo(sec)
        except Exception as e:
            output = f"❌ Error running irrigation: {e}"

        await context.bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=output
        )
        return

# ------------------- MAIN -------------------

async def main():
    request = HTTPXRequest(connect_timeout=30, read_timeout=30)
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).request(request).build()
    app.add_handler(CommandHandler("home", home))
    app.add_handler(CallbackQueryHandler(callback_handler))

    stop_event = asyncio.Event()

    def _signal_handler(*_):
        stop_event.set()

    for sig in (signal.SIGINT, signal.SIGTERM):
        with contextlib.suppress(NotImplementedError):
            signal.signal(sig, lambda *a: _signal_handler())

    async with app:
        await app.start()
        await app.updater.start_polling(
            drop_pending_updates=True,
            allowed_updates=None
        )
        print("🤖 Smarthome bot running... Ctrl+C to stop")
        await stop_event.wait()
        await app.updater.stop()
        await app.stop()

if __name__ == "__main__":
    asyncio.run(main())
