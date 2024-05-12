from api import socketio, app, logger


@socketio.on("connect", "/web")
def handle_connect():
    print("Connected")
