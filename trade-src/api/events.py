from api import app, logger, socketio


@socketio.on("connect", namespace="/web")
def handle_connect():
    print("Connected")
