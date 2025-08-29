from dataclasses import dataclass, asdict
from datetime import datetime, timezone
import json

@dataclass
class WeatherData:
    """Data class for weather information."""
    town: str
    country: str
    temperature: str
    wind: str
    humidity: str
    timestamp: str

    def to_json(self) -> str:
        return json.dumps(asdict(self), indent=2)

    @staticmethod
    def now_iso_utc() -> str:
        return datetime.now(timezone.utc).isoformat()
