import logging
import logging.config

logging_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        },
    },
    "handlers": {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
        },
    },
    "filters": {
        "exclude_endpoint_filter": {
            "()": "app.logging_filters.ExcludeEndpointFilter",
        },
    },
    "loggers": {
        "uvicorn.access": {
            "handlers": ["default"],
            "level": "INFO",
            "propagate": False,
            "filters": ["exclude_endpoint_filter"],
        },
    },
}

class ExcludeEndpointFilter(logging.Filter):
    def filter(self, record):
        excluded_endpoints = [
            "/gsi/hud",
        ]
        return not any(endpoint in record.getMessage() for endpoint in excluded_endpoints)

def init_logging_config():
    logging.config.dictConfig(logging_config)