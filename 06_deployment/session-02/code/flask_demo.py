import time

from flask import Flask
app = Flask(__name__)

@app.route("/order")
def order():
    time.sleep(3)  # Simulate a delay
    return {"order_id": 12345, "status": "confirmed"}

@app.route("/health")
def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    app.run(port=5000)