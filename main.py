from flask import Flask
import keep_alive
import threading
from bots import bot1  # Import bot1

app = Flask(__name__)

@app.route("/")
def home():
    return "Multi-Bot Host Online!"

def start_all_bots():
    threading.Thread(target=bot1.run_bot1).start()

keep_alive.keep_alive()
start_all_bots()
