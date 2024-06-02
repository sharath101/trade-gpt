from app.main import app


@app.route("/")
def home():
    return "Hello from Microservice 1!"
