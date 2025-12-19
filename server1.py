# -*- coding: utf-8 -*- 
import os
import json
import csv
import warnings
from datetime import datetime
from collections import deque
from flask import Flask, jsonify, request, render_template, send_file
from flask_cors import CORS
from statsmodels.tsa.holtwinters import SimpleExpSmoothing

warnings.filterwarnings("ignore")

# ---------------- Config ----------------
APP_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_FILE = os.path.join(APP_DIR, "sensor_data.csv")

FLASK_PORT = int(os.environ.get("FLASK_PORT", 5000))
MAX_HISTORY = 500
data_history = deque(maxlen=MAX_HISTORY)

# Create CSV if not exists
if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["timestamp", "gas", "temperature", "humidity", "magnitude", "protocol"])

app = Flask(__name__)
CORS(app)

# ✅ FIXED: /sensor now stores data instead of only printing it
@app.route('/sensor', methods=['POST'])
def sensor_data():
    try:
        data = request.get_json()
        print("Received from Arduino:", data)

        record = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
           "sensor_data": {
                "gas": float(data.get("gas", 0)),
                "temperature": float(data.get("temperature", 0)),
                "humidity": float(data.get("humidity", 0)),
                "magnitude": float(data.get("magnitude", 0))
            }
        }

        data_history.append(record)
        append_csv_record(record, protocol="HTTP")

        return {"status": "success", "message": "Data stored", "record": record}, 200
    except Exception as e:
        print("[SENSOR RECEIVE ERROR]", e)
        return {"status": "error", "message": str(e)}, 400


# ---------------- Helper Functions ----------------
def append_csv_record(rec, protocol="HTTP"):
    """Append record to CSV."""
    try:
        with open(CSV_FILE, "a", newline="") as f:
            w = csv.writer(f)
            w.writerow([
                rec["timestamp"],
                rec["sensor_data"]["gas"],
                rec["sensor_data"]["temperature"],
                rec["sensor_data"]["humidity"],
                rec["sensor_data"]["magnitude"],
                protocol
            ])
    except Exception as e:
        print("[CSV ERROR]", e)


def check_threats(rec):
    """Threat classification (Gas Leakage, Fire Risk, Rock Fall)."""
    threats = []
    try:
        gas = float(rec["sensor_data"]["gas"])
        temp = float(rec["sensor_data"]["temperature"])
        hum = float(rec["sensor_data"]["humidity"])
        mag = float(rec["sensor_data"]["magnitude"])

        if gas > 850:
            threats.append({"level": "danger", "text": "Gas Leakage"})
        if temp > 35 and hum < 25:
            threats.append({"level": "danger", "text": "Fire Risk"})
        if mag > 5.5:
            threats.append({"level": "danger", "text": "Rock Fall"})

    except Exception as e:
        print("[THREAT CHECK ERROR]", e)
    return threats


def get_forecast_list(key, lookback=None, steps=3):
    """SimpleExpSmoothing forecast for key from data_history."""
    try:
        if lookback is None:
            lookback = list(data_history)
        values = [float(d["sensor_data"].get(key, 0)) for d in lookback if key in d["sensor_data"]]
        if len(values) >= 5:
            model = SimpleExpSmoothing(values)
            fit = model.fit(smoothing_level=0.6, optimized=False)
            f = fit.forecast(steps)
            return [round(float(x), 2) for x in f]
    except Exception as e:
        print("[FORECAST ERROR]", e)
    return []


# ---------------- Flask Routes ----------------
@app.route("/")
def index():
    return render_template("index2.html", port=FLASK_PORT)

@app.route("/api/data", methods=["GET"])
def api_data():
    """Returns recent readings + forecast separately for dashboard."""
    limit = 15
    recent_data = list(data_history)[-limit:]

    forecast = {
        "gas": get_forecast_list("gas"),
        "temperature": get_forecast_list("temperature"),
        "humidity": get_forecast_list("humidity"),
        "magnitude": get_forecast_list("magnitude")
    }

    return jsonify({
        "status": "success",
        "data": recent_data,   # only real data
        "forecast": forecast,  # forecast separately
        "protocol": "HTTP"
    })


@app.route("/api/send", methods=["POST"])
def api_send():
    """Receive sensor data via HTTP POST."""
    try:
        data = request.get_json(force=True)
        print("[RAW HTTP]", data)

        record = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "sensor_data": {
                "gas": float(data.get("gas", 0)),
                "temperature": float(data.get("temperature", 0)),
                "humidity": float(data.get("humidity", 0)),
                "magnitude": float(data.get("magnitude", 0))
            }
        }

        data_history.append(record)
        append_csv_record(record, protocol="HTTP")

        return jsonify({"status": "success", "message": "Data received", "record": record})
    except Exception as e:
        print("[HTTP RECEIVE ERROR]", e)
        return jsonify({"status": "error", "message": str(e)}), 400


@app.route("/api/alerts", methods=["GET"])
def api_alerts():
    """Returns alerts based on latest record."""
    latest = list(data_history)[-1] if len(data_history) > 0 else None
    if not latest:
        return jsonify({"status": "success", "alerts": []})
    threats = check_threats(latest)
    alerts = []
    for t in threats:
        alerts.append({
            "timestamp": latest["timestamp"],
            "level": t["level"],
            "text": t["text"],
            "data": latest["sensor_data"]
        })
    return jsonify({"status": "success", "alerts": alerts})


@app.route("/api/csv", methods=["GET"])
def api_csv():
    """Download CSV data."""
    if os.path.exists(CSV_FILE):
        return send_file(CSV_FILE, as_attachment=True, download_name="sensor_data.csv")
    return jsonify({"status": "error", "message": "CSV not found"}), 404


# ---------------- Run Flask ----------------
if __name__ == "__main__":
    print(f"[START] Flask HTTP server running on http://0.0.0.0:{FLASK_PORT}")
    app.run(host="0.0.0.0", port=FLASK_PORT, debug=True)
