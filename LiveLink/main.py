from app import Config, create_app, socketio

if __name__ == "__main__":
    app = create_app()
    socketio.run(app, host="0.0.0.0", port=Config.LiveLink.PORT)
