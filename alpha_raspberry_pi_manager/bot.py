#!/usr/bin/env python3
import os
import asyncio
import signal
import contextlib
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, ContextTypes
)
from telegram.request import HTTPXRequest

# Import CPU info
from cpu_info import format_cpu_info

# --- Load environment ---
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = int(os.getenv("TELEGRAM_CHAT_ID"))

# ------------------- TELEGRAM HANDLER -------------------

async def cpu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != TELEGRAM_CHAT_ID:
        return
    await update.message.reply_text(format_cpu_info())

# ------------------- MAIN -------------------

async def main():
    request = HTTPXRequest(connect_timeout=30, read_timeout=30)
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).request(request).build()
    app.add_handler(CommandHandler("cpu", cpu))

    stop_event = asyncio.Event()

    def _signal_handler(*_):
        stop_event.set()

    for sig in (signal.SIGINT, signal.SIGTERM):
        with contextlib.suppress(NotImplementedError):
            signal.signal(sig, lambda *a: _signal_handler())

    async with app:
        await app.start()
        await app.updater.start_polling(drop_pending_updates=True)
        print("🤖 CPU bot running... Ctrl+C to stop")
        await stop_event.wait()
        await app.updater.stop()
        await app.stop()

if __name__ == "__main__":
    asyncio.run(main())
