import logging
import os
from collections import deque

from dotenv import load_dotenv
from flask import Flask

from .config import configure_logging, load_secret_key
from .routes.views import bp as weather_bp
from .agents.weather_agent import WeatherAgent
from .utils.async_runner import AsyncRunner


def create_app():
    load_dotenv()

    app = Flask(__name__, template_folder='templates')
    app.secret_key = load_secret_key()

    configure_logging(app)

    # Shared components (singletons)
    app.extensions = getattr(app, 'extensions', {})
    app.extensions['async_runner'] = AsyncRunner()         # background event loop
    app.extensions['weather_agent'] = WeatherAgent()       # browser_use agent
    app.extensions['recent_searches'] = deque(maxlen=10)   # simple in-memory cache

    # Blueprints
    app.register_blueprint(weather_bp)

    # Health log
    app.logger.info("Weather App initialized successfully")
    return app
