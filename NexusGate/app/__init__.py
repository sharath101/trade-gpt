import logging
import os
from logging.config import dictConfig

from flask import Flask
from flask_bcrypt import Bcrypt
from oauthlib.oauth2 import WebApplicationClient

app = Flask("NexusGate")
bcrypt = Bcrypt(app=app)

logging_config = dict(
    version=1,
    formatters={"f": {"format": "%(asctime)s %(name)-12s %(levelname)-8s %(message)s"}},
    handlers={
        "h": {
            "class": "logging.StreamHandler",
            "formatter": "f",
            "level": logging.WARNING,
        }
    },
    root={
        "handlers": ["h"],
        "level": logging.WARNING,
    },
)

dictConfig(logging_config)
logger = logging.getLogger("NexusGate")

GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", None)

client = WebApplicationClient(GOOGLE_CLIENT_ID)

from . import auth, oauth_google, routes
