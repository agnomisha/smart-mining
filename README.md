# Smart Mining Safety System 🚀

This project is a real-time **IoT-based mining safety system** designed to protect miners by monitoring environmental conditions and structural stability. Using **5G technology** for ultra-low latency, the system collects data from multiple sensors, classifies potential threats (Fire, Gas Leaks, Rockfalls), and performs **Time Series Forecasting** to predict future risks.

---

## 🛠 Features

* [cite_start]**Real-time Monitoring**: Tracks CO₂, Temperature, Humidity, and Vibration (Acceleration Magnitude)[cite: 8, 9, 16].
* **5G Optimized**: Designed for fast communication and low latency between the hardware and the cloud server.
* **Threat Classification**: 
    * **Gas Leakage**: Triggered when gas levels exceed 850.
    * **Fire Risk**: Triggered when temperature is above 35°C and humidity is below 25%.
    * **Rock Fall**: Detected via vibration magnitude spikes exceeding 5.5.
* **AI Forecasting**: Uses **Simple Exponential Smoothing** to predict future sensor values based on historical data.
* **Interactive Dashboard**: A web interface to visualize live data trends and receive real-time alerts.
* **Data Logging**: Automatically saves all incoming data to a CSV file for long-term analysis and download.

---

## 🏗 System Architecture

1.  [cite_start]**Hardware (Edge)**: An Arduino collects data from MQ135, DHT11, and ADXL335 sensors[cite: 1, 2, 3].
2.  **Communication**: Sensor data is transmitted via HTTP POST requests to the `/sensor` or `/api/send` endpoints.
3.  **Backend (Server)**: A Flask-based Python server processes incoming data, runs threat detection logic, and performs time series analysis.
4.  **Frontend (Dashboard)**: A web interface displays recent readings and forecasts separately for the operator.

---

## 📂 File Structure

* [cite_start]`arduinocode.ino`: Firmware for the Arduino to read sensors, calculate CO₂ ppm using a moving average filter, and determine G-force magnitude[cite: 4, 8, 16, 19].
* `server1.py`: Flask backend containing the API, forecasting logic, and threat detection.
* `sensor_data.csv`: Local database for storing historical sensor readings including timestamps and protocols.

---

## 🚀 Getting Started

### 1. Hardware Setup
Connect your sensors to the following pins as defined in the firmware:
* [cite_start]**MQ135 (Gas)**: Pin A0.
* [cite_start]**DHT11 (Temp/Hum)**: Pin 2[cite: 2].
* [cite_start]**ADXL335 (Accel)**: X-Pin (A1), Y-Pin (A2), Z-Pin (A3)[cite: 3].

### 2. Backend Installation
Ensure you have Python 3.x installed, then install the required dependencies:
```bash
pip install flask flask-cors statsmodels
