import serial
import requests
import time
import json

# --- Adjust these ---
SERIAL_PORT = "COM18"    # Your Arduino COM port
BAUD_RATE = 9600
SERVER_URL = "http://10.201.0.170:5000/api/send"   # ✅ Use /api/send (not /sensor)
# ---------------------

# Open serial port
ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
time.sleep(2)  # give Arduino time to reset

print("✅ Bridge started. Listening for JSON from Arduino...")

while True:
    try:
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8').strip()
            if not line:
                continue

            print("📥 Raw from Arduino:", line)

            try:
                # ✅ Try to parse JSON directly (Arduino must send JSON!)
                data = json.loads(line)
            except json.JSONDecodeError:
                print("⚠️ Skipping non-JSON line:", line)
                continue

            # ✅ Make sure expected keys exist
            required_keys = ["gas", "temperature", "humidity", "magnitude"]
            if not all(k in data for k in required_keys):
                print("⚠️ Missing expected keys in:", data)
                continue

            # ✅ Send JSON directly to Flask
            response = requests.post(SERVER_URL, json=data)
            print("📤 Sent to Flask:", data, "| Status:", response.status_code)

    except Exception as e:
        print("🔥 Error:", e)
        time.sleep(1)
