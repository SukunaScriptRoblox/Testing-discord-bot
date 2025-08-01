from flask import Flask
import threading
import keep_alive
from Bots import bot1, bot2  # Import both bots

app = Flask(__name__)

@app.route('/')
def home():
    return "Multi-Bot Server Running ✅"

def start_all_bots():
    threading.Thread(target=bot1.run_bot1).start()
    threading.Thread(target=bot2.run_bot2).start()

# Start flask server
keep_alive.keep_alive()

# Start all bots
start_all_bots()
