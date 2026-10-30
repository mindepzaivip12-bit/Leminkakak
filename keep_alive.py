from flask import Flask
from threading import Thread
import time
import requests
import os

app = Flask('')

@app.route('/')
def home():
    return "Bot đang chạy 24/7!"

def run():
    # Render cấp PORT tự động
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()
