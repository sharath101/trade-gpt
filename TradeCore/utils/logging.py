import logging
from logging.config import dictConfig


def get_logger(name, level):
    logging_config = dict(
        version=1,
        formatters={
            "f": {"format": "%(asctime)s %(name)-12s %(levelname)-8s %(message)s"}
        },
        handlers={
            "h": {
                "class": "logging.StreamHandler",
                "formatter": "f",
                "level": level,
            }
        },
        root={
            "handlers": ["h"],
            "level": level,
        },
    )

    dictConfig(logging_config)

    logger = logging.getLogger(name)

    return logger
