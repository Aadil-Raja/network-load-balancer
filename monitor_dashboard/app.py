from flask import Flask, render_template
import requests

app = Flask(__name__)

# Define your backend server endpoints
servers = {
    'Server 1': 'http://127.0.0.1:5001',
    'Server 2': 'http://127.0.0.1:5002',
    'Server 3': 'http://127.0.0.1:5003',
}

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

if __name__ == "__main__":
    app.run(port=5050)
