from logging.config import dictConfig
import logging
import os
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv(override=True)

# Fetch the stage type from environment variables
# Default to 'dev' if STAGE_TYPE is not set
STAGE_TYPE = os.getenv("STAGE_TYPE", "dev")

# Logging configuration
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
logger_name = f"platform-video-generation-service-{STAGE_TYPE}"
logger = logging.getLogger(logger_name)
