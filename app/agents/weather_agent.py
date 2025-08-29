import os
import json
import logging
import re
from datetime import datetime, timezone
from typing import Any, Optional, Tuple

import httpx
from browser_use import Agent, ChatOpenAI

from ..models import WeatherData

logger = logging.getLogger(__name__)


class WeatherAgent:
    """AI Agent for fetching weather data using browser automation."""

    def __init__(self):
        self.agent: Optional[Agent] = None
        self._initialize_agent()

    def _initialize_agent(self):
        try:
            # Model can be controlled via env; defaults to gpt-4o-mini
            model = os.getenv("BROWSER_USE_MODEL", "gpt-4o-mini")

            # IMPORTANT: pass an LLM object, not a string
            llm = ChatOpenAI(model=model)

            self.agent = Agent(
                task="Weather data fetcher",
                llm=llm,
            )
            logger.info("Weather agent initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize weather agent: {e}")
            raise

    def _sanitize_input(self, text: str) -> str:
        if not text:
            return ""
        # Keep letters, spaces, hyphens, apostrophes
        sanitized = re.sub(r"[^a-zA-Z\s\-']", "", text.strip())
        return sanitized[:50]

    def _validate_location(self, town: str, country: str) -> Tuple[bool, str, str, str]:
        if not town or not country:
            return False, "Both town and country are required", "", ""
        town_s = self._sanitize_input(town)
        country_s = self._sanitize_input(country)
        if len(town_s) < 2:
            return False, "Town name must be at least 2 characters", "", ""
        if len(country_s) < 2:
            return False, "Country name must be at least 2 characters", "", ""
        return True, "", town_s, country_s

    async def get_weather_data(self, town: str, country: str) -> Optional[WeatherData]:
        """
        Use the browser agent to fetch weather and return a WeatherData object.
        The agent is instructed to return strict JSON to make parsing robust.
        """
        ok, msg, town_s, country_s = self._validate_location(town, country)
        if not ok:
            logger.warning(f"Invalid location input: {msg}")
            return None

        logger.info(f"Fetching weather data for {town_s}, {country_s}")

        task = f"""
        Go to weather.com or openweathermap.org and search for current weather in {town_s}, {country_s}.
        Extract exactly these fields and return **only** this JSON, no extra text:

        {{
          "location": "<resolved location name>",
          "temperature": "<number + unit, e.g., 22°C or 71°F>",
          "wind": "<speed + unit (+ optional direction), e.g., 10 km/h N>",
          "humidity": "<percent, e.g., 55%>"
        }}

        Do not include explanations or markdown, only valid JSON.
        """

        try:
            result = await self.agent.run(task)  # type: ignore[arg-type]
        except Exception as e:
            logger.error(f"Agent error: {e}")
            return None

        if not result:
            logger.warning(f"No result returned by agent for {town_s}, {country_s}")
            return None

        try:
            logger.debug(f"Raw agent result (truncated): {str(result)[:2000]}")
        except Exception:
            pass

        return self._parse_weather_result(result, town_s, country_s)

    def _parse_weather_result(self, result: Any, town: str, country: str) -> Optional[WeatherData]:
        """
        Parse the agent result; prefer JSON, fall back to regex heuristics.
        """
        try:
            result_str = str(result).strip()

            # 1) Try JSON first
            try:
                obj = json.loads(result_str)
                temperature = obj.get("temperature") or "N/A"
                wind = obj.get("wind") or "N/A"
                humidity = obj.get("humidity") or "N/A"
                # location is not used to override inputs, but we keep it around if you want to display it
                _location = obj.get("location") or f"{town.title()}, {country.title()}"
                return WeatherData(
                    town=town.title(),
                    country=country.title(),
                    temperature=temperature,
                    wind=wind,
                    humidity=humidity,
                    timestamp=datetime.now(timezone.utc).isoformat(),
                )
            except json.JSONDecodeError:
                pass

            # 2) Fallback: regex extraction
            temp_match = re.search(r'(\d+(?:\.\d+)?)\s*°?\s*([CF])', result_str, re.IGNORECASE)
            temperature = f"{temp_match.group(1)}°{temp_match.group(2).upper()}" if temp_match else "N/A"

            wind_match = re.search(
                r'wind[:\s]*(\d+(?:\.\d+)?)\s*(mph|kmh|km/h|m/s)(?:\s*[NSEW]{1,2})?',
                result_str,
                re.IGNORECASE
            )
            wind = f"{wind_match.group(1)} {wind_match.group(2)}" if wind_match else "N/A"

            humidity_match = re.search(r'humidity[:\s]*(\d+)\s*%', result_str, re.IGNORECASE)
            humidity = f"{humidity_match.group(1)}%" if humidity_match else "N/A"

            # Emergency heuristic: grab first 3 numbers
            if temperature == "N/A" and wind == "N/A" and humidity == "N/A":
                numbers = re.findall(r'\d+(?:\.\d+)?', result_str)
                if len(numbers) >= 3:
                    temperature = f"{numbers[0]}°C"
                    wind = f"{numbers[1]} km/h"
                    humidity = f"{numbers[2]}%"

            return WeatherData(
                town=town.title(),
                country=country.title(),
                temperature=temperature,
                wind=wind,
                humidity=humidity,
                timestamp=datetime.now(timezone.utc).isoformat(),
            )
        except Exception as e:
            logger.error(f"Error parsing weather result: {e}")
            return None


# ---------- Zero-dependency API fallback (Open-Meteo) ----------

async def get_weather_open_meteo(town: str, country: str) -> Optional[WeatherData]:
    """
    Fallback path that does not rely on the browser agent.
    Uses Open-Meteo Geocoding + Forecast APIs (no API key).
    Humidity is not provided in current_weather, so it's set to 'N/A'.
    """
    try:
        q = f"{town}, {country}"
        async with httpx.AsyncClient(timeout=30.0) as client:
            # 1) Geocode
            georesp = await client.get(
                "https://geocoding-api.open-meteo.com/v1/search",
                params={"name": q, "count": 1, "language": "en", "format": "json"},
            )
            geo = georesp.json()
            if not geo.get("results"):
                return None
            r0 = geo["results"][0]
            lat, lon = r0["latitude"], r0["longitude"]

            # 2) Weather
            wresp = await client.get(
                "https://api.open-meteo.com/v1/forecast",
                params={"latitude": lat, "longitude": lon, "current_weather": True, "windspeed_unit": "kmh"},
            )
            w = wresp.json()
            cur = w.get("current_weather")
            if not cur:
                return None

            temperature = f"{cur['temperature']}°C"
            wind = f"{cur['windspeed']} km/h"
            humidity = "N/A"

            return WeatherData(
                town=town.title(),
                country=country.title(),
                temperature=temperature,
                wind=wind,
                humidity=humidity,
                timestamp=datetime.now(timezone.utc).isoformat(),
            )
    except Exception as e:
        logger.error(f"Open-Meteo fallback error: {e}")
        return None
