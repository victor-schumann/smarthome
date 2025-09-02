#!/usr/bin/env python3
import os
import subprocess
import requests
from dotenv import load_dotenv

# --- Load env vars ---
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = int(os.getenv("TELEGRAM_CHAT_ID"))
CPU_TEMP_MAX = float(os.getenv("CPU_TEMP_MAX", "70"))  # default 70'C

def get_cpu_temp() -> float:
    """Return CPU temperature in °C as float."""
    try:
        output = subprocess.check_output(["vcgencmd", "measure_temp"]).decode()
        # output looks like: temp=49.4'C
        value = output.replace("temp=", "").replace("'C", "")
        return float(value)
    except Exception:
        return -1.0

def send_telegram(msg: str):
    """Send a Telegram message."""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": msg}
    try:
        requests.post(url, data=payload, timeout=10)
    except Exception as e:
        print(f"Error sending message: {e}")

def main():
    temp = get_cpu_temp()
    if temp < 0:
        return  # couldn't read temp
    
    if temp >= CPU_TEMP_MAX:
        send_telegram(f"⚠️ CPU temperature too high: {temp:.1f}°C (max {CPU_TEMP_MAX}°C)")

if __name__ == "__main__":
    main()
