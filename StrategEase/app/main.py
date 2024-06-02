import app.config as config
from flask import Flask

app = Flask(__name__)

from app.routes import *

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=config.PORT)
