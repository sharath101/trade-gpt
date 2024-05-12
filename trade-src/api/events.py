from api import app, logger, socketio


@socketio.on("connect")
def handle_connect():
    pass
