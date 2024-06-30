from app import create_app, socketio
from config import Config

if __name__ == "__main__":
    app = create_app()
    socketio.run(app, host="0.0.0.0", port=Config.Backtestify.PORT)
