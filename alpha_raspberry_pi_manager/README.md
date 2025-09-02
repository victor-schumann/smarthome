# Raspberry Pi CPU Info Script

This Python script retrieves CPU information from your Raspberry Pi, including:

- CPU temperature
- CPU frequency
- CPU usage per core

It uses `psutil` for CPU metrics and `vcgencmd` (Raspberry Pi tool) for temperature.

---

## Setup Instructions

### 1. Update system and install dependencies

```sh
sudo apt update
sudo apt install python3-venv -y
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
chmod +x cpu_info.py
./cpu_info.py
```
