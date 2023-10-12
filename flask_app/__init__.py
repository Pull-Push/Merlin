from flask import Flask
from flask_socketio import SocketIO

socketio = SocketIO(ping_timeout=30, ping_interval=15)

app = Flask(__name__)
app.config["SECRET_KEY"] = "Merlin TEST"
socketio = SocketIO(app)
