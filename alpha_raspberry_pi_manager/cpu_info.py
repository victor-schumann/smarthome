#!/usr/bin/env python3
import subprocess
import psutil

def get_cpu_temp() -> str:
    """Get CPU temperature on Raspberry Pi."""
    try:
        output = subprocess.check_output(["vcgencmd", "measure_temp"]).decode()
        return output.strip().replace("temp=", "")
    except Exception:
        return "N/A"

def get_cpu_freq() -> str:
    """Get current and max CPU frequency."""
    try:
        freq = psutil.cpu_freq()
        return f"{freq.current:.0f}MHz ({freq.max:.0f})"
    except Exception:
        return "N/A"

def get_cpu_usage() -> str:
    """Get per-core CPU usage percentages as a list."""
    try:
        usage = psutil.cpu_percent(interval=1, percpu=True)
        return f"{usage} %"
    except Exception:
        return "N/A"

def format_cpu_info() -> str:
    """Compact CPU info string with line breaks."""
    return (
        f"🌡 | {get_cpu_temp()}\n"
        f"⏱ | {get_cpu_freq()}\n"
        f"📊 | {get_cpu_usage()}"
    )

if __name__ == "__main__":
    print(format_cpu_info())
