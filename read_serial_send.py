import serial
import requests
import time
import json

# --- Adjust these ---
SERIAL_PORT = "COM18"   # Replace with your Arduino port (e.g., /dev/ttyUSB0 on Linux)
BAUD_RATE = 9600
SERVER_URL = "http://10.77.204.170:5000/sensor"
# ---------------------

ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
time.sleep(2)  # wait for Arduino to reset

while True:
    try:
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8').strip()
            if line:
                print("Sensor data:", line)
                
                data = {"value": line}
                response = requests.post(SERVER_URL, json=data)
                print("Sent to server:", response.status_code)
    except Exception as e:
        print("Error:", e)
        time.sleep(1)
