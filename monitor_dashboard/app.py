from flask import Flask, render_template, request, jsonify
import requests
import subprocess

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
# Route 4: Set Load Balancing Algorithm
# -------------------------
@app.route("/set-algorithm", methods=["POST"])
def set_algorithm():
    data = request.get_json()
    algorithm = data.get("algorithm")

    # Determine directive for NGINX upstream
    if algorithm == "round_robin":
        directive = ""  # round robin is default
    elif algorithm == "least_conn":
        directive = "least_conn;"
    elif algorithm == "ip_hash":
        directive = "ip_hash;"
    else:
        return jsonify({"message": "Invalid algorithm"}), 400

    # Generate updated nginx.conf
    new_conf = f"""
worker_processes  1;

events {{
    worker_connections  1024;
}}

http {{
    upstream backend_servers {{
        {directive}
        server 127.0.0.1:5001;
        server 127.0.0.1:5002;
        server 127.0.0.1:5003;
    }}

    server {{
        listen 8080;
        server_name localhost;

        location / {{
            proxy_pass http://backend_servers;
        }}
    }}
}}
"""

    try:
        nginx_path = "/home/YOUR_USERNAME/network-load-balancer/configs/nginx.conf"  # <-- Replace YOUR_USERNAME
        with open(nginx_path, "w") as f:
            f.write(new_conf)

        # Reload NGINX
        subprocess.run(["sudo", "nginx", "-s", "reload"])
        return jsonify({"message": f"Algorithm '{algorithm}' applied and NGINX reloaded ✅"})

    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500


# -------------------------
# Run the App
# -------------------------
if __name__ == "__main__":
    app.run(port=5050)
