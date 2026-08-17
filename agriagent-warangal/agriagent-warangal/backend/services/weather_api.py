"""
Weather API Service (placeholder)
Intended to pull live temperature/humidity/rainfall for Warangal district
from OpenWeatherMap, to auto-populate inputs for the Crop Recommendation
Agent instead of asking the farmer to enter them manually.
"""
import os

import requests

WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

# Approximate coordinates for Warangal city.
WARANGAL_COORDS = {"lat": 17.9689, "lon": 79.5941}


def fetch_current_weather(
    lat: float = WARANGAL_COORDS["lat"], lon: float = WARANGAL_COORDS["lon"]
) -> dict:
    """
    TODO: Fully wire up once WEATHER_API_KEY is set. Returns mock weather
    data for Warangal in the meantime.
    """
    if not WEATHER_API_KEY:
        return {
            "source": "mock",
            "location": "Warangal, Telangana",
            "temperature_c": 29.5,
            "humidity_pct": 68,
            "rainfall_mm_last_24h": 2.0,
        }

    params = {"lat": lat, "lon": lon, "appid": WEATHER_API_KEY, "units": "metric"}
    response = requests.get(BASE_URL, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()
    return {
        "source": "openweathermap",
        "location": "Warangal, Telangana",
        "temperature_c": data.get("main", {}).get("temp"),
        "humidity_pct": data.get("main", {}).get("humidity"),
        "rainfall_mm_last_24h": data.get("rain", {}).get("1h", 0.0),
    }


if __name__ == "__main__":
    print(fetch_current_weather())
