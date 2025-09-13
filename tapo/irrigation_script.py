#!/usr/bin/env python3
import os
import sys
import asyncio
from dotenv import load_dotenv
from tapo import ApiClient

# --- Load environment ---
load_dotenv()
TAPO_IP = os.getenv("TAPO_IP")          # e.g. "192.168.1.55"
TAPO_MODEL = os.getenv("TAPO_MODEL")    # "p100" or "p110"
TAPO_USER = os.getenv("TAPO_EMAIL") or os.getenv("TAPO_USERNAME")
TAPO_PASS = os.getenv("TAPO_PASSWORD")

async def toggle_tapo(duration: int) -> str:
    if not (TAPO_IP and TAPO_MODEL and TAPO_USER and TAPO_PASS):
        return "Missing TAPO_IP, TAPO_MODEL, TAPO_EMAIL/USERNAME, or TAPO_PASSWORD in .env"

    try:
        client = ApiClient(TAPO_USER, TAPO_PASS)
        device = await getattr(client, TAPO_MODEL.lower())(TAPO_IP)

        info = await device.get_device_info()
        is_on = bool(getattr(info, "device_on", False))

        if is_on:
            await device.off()
        else:
            await device.on()

        # Keep irrigation running for given duration
        await asyncio.sleep(duration)

        # Restore original state
        if is_on:
            await device.on()
        else:
            await device.off()

        return f"Irrigation ran for {duration}s"
    except Exception as e:
        return f"Error talking to Tapo device: {e}"

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <seconds>")
        sys.exit(1)

    try:
        seconds = int(sys.argv[1])
    except ValueError:
        print("Duration must be an integer (seconds)")
        sys.exit(1)

    result = asyncio.run(toggle_tapo(seconds))
    print(result)
