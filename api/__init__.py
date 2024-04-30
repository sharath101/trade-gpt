from flask import Flask
import os

app = Flask(__name__)
logger = app.logger
logger.setLevel("DEBUG")
app.config.from_pyfile("config.py")

from api import routes

if not os.path.isdir(app.config["DATA"]):
    os.mkdir(os.path.join(app.config["DATA"]))
