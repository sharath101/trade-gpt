import socketio as s
from flask_cors import CORS
from flask_socketio import SocketIO

socketio = SocketIO()
cors = CORS()
client_manager = s.RedisManager()
