from flask import Flask

import app.config as config

app = Flask(__name__)


from app.routes import *

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=config.PORT, debug=config.DEBUG)
