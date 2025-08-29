import os
from dataclasses import asdict
from typing import Any, Dict

from flask import Blueprint, current_app, jsonify, render_template, request

from ..models import WeatherData
from ..agents.weather_agent import get_weather_open_meteo

bp = Blueprint('weather', __name__)


@bp.route('/')
def index():
    return render_template('index.html')


@bp.route('/weather', methods=['POST'])
def get_weather():
    try:
        data: Dict[str, Any] = request.get_json(force=True, silent=True) or {}
        town = (data.get('town') or '').strip()
        country = (data.get('country') or '').strip()

        if not town or not country:
            return jsonify({'error': 'Both town and country are required'}), 400

        async_runner = current_app.extensions['async_runner']
        weather_agent = current_app.extensions['weather_agent']
        recent_searches = current_app.extensions['recent_searches']

        use_agent = os.getenv("USE_AGENT", "true").lower() == "true"

        weather_data: WeatherData | None = None

        if use_agent:
            # Give Playwright + site navigation enough time
            weather_data = async_runner.run(
                weather_agent.get_weather_data(town, country),
                timeout=120  # seconds
            )

        if not weather_data:
            # Fallback to Open-Meteo (no API key)
            weather_data = async_runner.run(
                get_weather_open_meteo(town, country),
                timeout=60
            )

        if weather_data:
            recent_searches.appendleft(weather_data)
            return jsonify({'success': True, 'data': asdict(weather_data)})

        return jsonify({
            'success': False,
            'error': 'Could not fetch weather data for the specified location'
        }), 404

    except Exception as e:
        current_app.logger.exception(f"Error in /weather endpoint: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@bp.route('/recent', methods=['GET'])
def get_recent():
    recent_searches = current_app.extensions['recent_searches']
    return jsonify({
        'success': True,
        'data': [asdict(x) for x in list(recent_searches)]
    })


@bp.errorhandler(404)
def not_found(_):
    return jsonify({'error': 'Endpoint not found'}), 404


@bp.errorhandler(500)
def internal_error(_):
    return jsonify({'error': 'Internal server error'}), 500
