from flask import Flask

app = Flask(__name__)
logger = app.logger
app.config.from_pyfile("config.py")

from api import routes
