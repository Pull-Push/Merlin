import eventlet
from flask_app import app, socketio
from flask_app.controllers import user_controller

from eventlet import wsgi

if __name__ == "__main__":
    wsgi.server(eventlet.listen (('127.0.0.1',8008)), app)
