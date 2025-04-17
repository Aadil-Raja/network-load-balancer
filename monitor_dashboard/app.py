from flask import Flask, render_template, request, jsonify
import requests
import subprocess
import random
import time
from threading import Thread
from collections import defaultdict

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
            r = requests.get(url, timeout=5)  # allow more time for slower servers
            response_time = r.elapsed.total_seconds()
            if response_time > 1.5:
                status[name] = "🟡 Online (Slow)"
            else:
                status[name] = "🟢 Online"
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
# Helper: Generate IP Pool
# -------------------------
def generate_ip_pool(total_requests, repeat_range=(2, 3)):
    ip_pool = []
    used_ips = []
    while len(ip_pool) < total_requests:
        ip = f"{random.randint(1, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)}"
        repeat_count = random.randint(*repeat_range)
        for _ in range(repeat_count):
            if len(ip_pool) < total_requests:
                ip_pool.append(ip)
            else:
                break
        used_ips.append(ip)
    return ip_pool

# -------------------------
# Route 3: Simulate Requests via NGINX
# -------------------------
@app.route("/simulate", methods=["POST"])
def simulate():
    count = int(request.json.get("count"))
    results = [None] * count
    server_count = defaultdict(int)
    fake_ips = generate_ip_pool(count, repeat_range=(2, 3))

    def send_request(i, ip):
        headers = {'X-Forwarded-For': ip}
        start = time.time()
        try:
            r = requests.get("http://127.0.0.1:8080", headers=headers, timeout=5)
            duration = round(time.time() - start, 2)
            response = r.text
        except:
            duration = round(time.time() - start, 2)
            response = "Error or Server Offline"

        # Count the server based on response text
        if "Server 1" in response:
            server_count["Server 1"] += 1
        elif "Server 2" in response:
            server_count["Server 2"] += 1
        elif "Server 3" in response:
            server_count["Server 3"] += 1

        results[i] = {
            "request": i + 1,
            "response": f"{response} (IP: {ip}, Time: {duration}s)"
        }

    threads = []
    for i in range(count):
        t = Thread(target=send_request, args=(i, fake_ips[i]))
        t.start()
        threads.append(t)
        time.sleep(0.05)

    for t in threads:
        t.join()

    return jsonify({"results": results, "summary": dict(server_count)})

# -------------------------
# Route 4: Set Load Balancing Algorithm
# -------------------------
@app.route("/set-algorithm", methods=["POST"])
def set_algorithm():
    data = request.get_json()
    algorithm = data.get("algorithm")

    if algorithm == "round_robin":
        directive = ""
    elif algorithm == "least_conn":
        directive = "least_conn;"
    elif algorithm == "ip_hash":
        directive = "ip_hash;"
    else:
        return jsonify({"message": "Invalid algorithm"}), 400

    new_conf = f"""
worker_processes  1;

events {{
    worker_connections  1024;
}}

http {{
    log_format hashlog '$remote_addr - $proxy_add_x_forwarded_for';

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
            set_real_ip_from 127.0.0.1;
            real_ip_header X-Forwarded-For;
            proxy_pass http://backend_servers;
        }}
    }}
}}
"""
    try:
        nginx_path = "/home/aadilraja/network-load-balancer/config/nginx.conf"
        with open(nginx_path, "w") as f:
            f.write(new_conf)

        subprocess.run(["sudo", "nginx", "-s", "reload"])
        return jsonify({"message": f"Algorithm '{algorithm}' applied and NGINX reloaded ✅"})

    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500

# -------------------------
# Run the App
# -------------------------
if __name__ == "__main__":
    app.run(port=5050)