from flask import Flask
import time
import random
app = Flask(__name__)
@app.route("/")
def index():
    delay = random.uniform(1.5, 2)    
    time.sleep(delay)
    return f"Hello from Server 3! (Delay: {delay:.2f}s)"
if __name__ == "__main__":
    app.run(port=5003,threaded=True)
