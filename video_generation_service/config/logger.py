from logging.config import dictConfig
import logging
import os


LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
        },
    },
    "root": {
        "level": "INFO",
        "handlers": ["console"],
    },
    "loggers": {
        "app_logger": {
            "level": "DEBUG",
            "handlers": ["console"],
            "propagate": False,
        },
    },
}


def setup_logging():
    dictConfig(LOGGING_CONFIG)


# Exported logger instance
setup_logging()
logger_name = "platform-services-video-gen"
logger = logging.getLogger(logger_name)
