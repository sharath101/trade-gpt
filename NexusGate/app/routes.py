from database import users

from . import app, logger


@app.route("/")
def index():
    return '<a class="button" href="/log">Google Login</a>'
