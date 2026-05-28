import logging
import os
from flask import Flask


def setup_logging(app: Flask) -> None:
    log_level = getattr(logging, app.config.get('LOG_LEVEL', 'INFO').upper(), logging.INFO)

    handler = logging.StreamHandler()
    handler.setLevel(log_level)
    formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
    )
    handler.setFormatter(formatter)

    app.logger.setLevel(log_level)
    if not app.logger.handlers:
        app.logger.addHandler(handler)

    # Also configure root logger for library messages
    logging.basicConfig(level=log_level, handlers=[handler], force=False)
