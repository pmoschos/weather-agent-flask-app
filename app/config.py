import logging
import os
from logging.handlers import RotatingFileHandler

def load_secret_key():
    return os.getenv('FLASK_SECRET_KEY') or os.urandom(24)

def configure_logging(app):
    log_level = os.getenv('LOG_LEVEL', 'INFO').upper()

    app.logger.setLevel(log_level)

    # Stream handler
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(log_level)
    stream_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ))

    # Rotating file handler
    file_handler = RotatingFileHandler(
        filename=os.getenv('LOG_FILE', 'weather_app.log'),
        maxBytes=2 * 1024 * 1024,
        backupCount=3
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ))

    # Attach handlers (avoid duplicates)
    if not app.logger.handlers:
        app.logger.addHandler(stream_handler)
        app.logger.addHandler(file_handler)
    else:
        # Replace handlers in case Flask already set defaults
        app.logger.handlers = [stream_handler, file_handler]
