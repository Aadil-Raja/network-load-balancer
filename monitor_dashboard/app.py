from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

# Define your backend server endpoints
servers = {
    'Server 1': 'http://127.0.0.1:5001',
    'Server 2': 'http://127.0.0.1:5002',
    'Server 3': 'http://127.0.0.1:5003',
}

# -------------------------
# Route 1: Server Status Dashboard
# -------------------------
@app.route("/")
def dashboard():
    status = {}
    for name, url in servers.items():
        try:
            r = requests.get(url, timeout=1)
            if r.status_code == 200:
                status[name] = "🟢 Online"
            else:
                status[name] = "🟠 Error"
        except:
            status[name] = "🔴 Offline"
    return render_template("status.html", status=status)


# -------------------------
# Route 2: Simulation UI Page
# -------------------------
@app.route("/simulate-ui")
def simulate_ui():
    return render_template("simulator.html")


# -------------------------
# Route 3: Simulate Requests via NGINX
# -------------------------
@app.route("/simulate", methods=["POST"])
def simulate():
    count = int(request.json.get("count"))
    results = []

    for i in range(count):
        try:
            r = requests.get("http://127.0.0.1:8080", timeout=1)
            results.append({"request": i + 1, "response": r.text})
        except:
            results.append({"request": i + 1, "response": "Error or Server Offline"})

    return jsonify({"results": results})


# -------------------------
# Run the App
# -------------------------
if __name__ == "__main__":
    app.run(port=5050)
