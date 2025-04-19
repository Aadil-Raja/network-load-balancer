from flask import Flask
import random
import time
app = Flask(__name__)

@app.route("/")
def index():
    delay = random.uniform(0.2, 0.5)  
    time.sleep(delay)
    return f"Hello from Server 1! (Delay: {delay:.2f}s)"

if __name__ == "__main__":
    app.run(port=5001,threaded=True)
