import os
import logging
from logging.config import dictConfig
from dotenv import load_dotenv

load_dotenv()

DISCORD_API_SECRET = os.getenv("DISCORD_API_TOKEN")

LOGGING_CFG = {
    "version": 1,
    "disabled_existing_loggers": False,
    "formatters":{
        "verbose":{
            "format": "%(levelname)-10s - %(asctime)s - %(module)-15s : %(message)s"
        },
        "standart":{
            "format": "%(levelname)-10s - %(name)-15s : %(message)s"
        }
    },
    "handlers":{
        "console":{
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "standart"
        },
        "console2":{
            "level": "WARNING",
            "class": "logging.StreamHandler",
            "formatter": "standart"
        },
        "file":{
            "level": "INFO",
            "class": "logging.FileHandler",
            "filename": "logs/data.log",
            "mode": "w",
            "formatter": "verbose"
        }
    },
    "loggers":{
        "bot": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False
        },
        "discord": {
            "handlers": ["console2", "file"],
            "level": "INFO",
            "propagate": False
        }
    }   
}
dictConfig(LOGGING_CFG)