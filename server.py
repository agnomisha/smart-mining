from flask import Flask, request

app = Flask(__name__)

@app.route('/sensor', methods=['POST'])
def sensor_data():
    data = request.get_json()
    print("Received from Arduino:", data)
    return {"status": "OK"}, 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
