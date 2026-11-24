import os

from dotenv import load_dotenv

load_dotenv()  # must run before flask_app is imported so SECRET_KEY / DB_* are set

from flask_app import app, socketio
from flask_app.controllers import user_controller  # noqa: F401 - registers all routes

if __name__ == "__main__":
    socketio.run(
        app,
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8008)),
        debug=os.environ.get("FLASK_DEBUG", "0") == "1",
        allow_unsafe_werkzeug=True,
    )