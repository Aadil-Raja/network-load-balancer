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
            r = requests.get(url, timeout=10)
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
# Route 3: Simulate Requests via NGINX or HAProxy
# -------------------------
@app.route("/simulate", methods=["POST"])
def simulate():
    count = int(request.json.get("count"))
    method = request.json.get("method", "nginx")

    url = "http://127.0.0.1:8080" if method == "nginx" else "http://127.0.0.1:8081"

    results = [None] * count
    server_count = defaultdict(int)
    fake_ips = generate_ip_pool(count, repeat_range=(2, 3))

    def send_request(i, ip):
        headers = {'X-Forwarded-For': ip}
        start = time.time()
        try:
            r = requests.get(url, headers=headers, timeout=8)
            duration = round(time.time() - start, 2)
            response = r.text
        except:
            duration = round(time.time() - start, 2)
            response = "Error or Server Offline"

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
# Route 4: Set Load Balancing Algorithm for NGINX or HAProxy
# -------------------------


@app.route("/set-algorithm", methods=["POST"])
def set_algorithm():
    data = request.get_json()
    algorithm = data.get("algorithm")
    method = data.get("method", "nginx")
    print(f"Setting {algorithm} for method {method}")

    # Map algorithms to directives
    if algorithm == "round_robin":
        nginx_directive = ""
        haproxy_balance = "static-rr"
    elif algorithm == "least_conn":
        nginx_directive = "least_conn;"
        haproxy_balance = "leastconn"
    elif algorithm == "ip_hash":
        nginx_directive = "ip_hash;"
        haproxy_balance = "source"
    else:
        return jsonify({"message": "Invalid algorithm"}), 400

    # --- NGINX branch ---
    if method == "nginx":
        # 1) stop any running nginx
        subprocess.run(["sudo", "nginx", "-s", "stop"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        # 2) build & write new config
        new_conf = f"""
worker_processes  1;

events {{
    worker_connections  1024;
}}

http {{
    log_format hashlog '$remote_addr - $proxy_add_x_forwarded_for';

    upstream backend_servers {{
        {nginx_directive}
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
        nginx_path = "/home/aadilraja/network-load-balancer/config/nginx.conf"
        try:
            with open(nginx_path, "w") as f:
                f.write(new_conf)
            # 3) start nginx with the new config
            subprocess.run(["sudo", "nginx", "-c", nginx_path], check=True)
            return jsonify({"message": f"NGINX Algorithm '{algorithm}' applied ✅"})
        except Exception as e:
            return jsonify({"message": f"NGINX Error: {e}"}), 500

    # --- HAProxy branch ---
    elif method == "haproxy":
        # 1) kill any running haproxy
        subprocess.run(["sudo", "pkill", "haproxy"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        # 2) build & write new config
        haproxy_conf = f"""
global
    daemon
    maxconn 256

defaults
    mode http
    timeout connect 5000ms
    timeout client 50000ms
    timeout server 50000ms

frontend http_front
    bind *:8081
    default_backend servers

backend servers
    balance {haproxy_balance}
    hash-type consistent

    server s1 127.0.0.1:5001 check weight 1
    server s2 127.0.0.1:5002 check weight 1
    server s3 127.0.0.1:5003 check weight 1
"""
        haproxy_path = "/home/aadilraja/network-load-balancer/config/haproxy.cfg"
        try:
            with open(haproxy_path, "w") as f:
                f.write(haproxy_conf)
            # 3) start haproxy in daemon mode
            subprocess.run(["sudo", "haproxy", "-f", haproxy_path, "-D"], check=True)
            return jsonify({"message": f"HAProxy Algorithm '{algorithm}' applied ✅"})
        except Exception as e:
            return jsonify({"message": f"HAProxy Error: {e}"}), 500

    else:
        return jsonify({"message": "Invalid load balancer method"}), 400
# -------------------------
# Run the App
# -------------------------
if __name__ == "__main__":
    app.run(port=5050)