import requests
import json
from datetime import datetime

import openmeteo_requests

import pandas as pd
import requests_cache
from retry_requests import retry

def fetch_weather_data(latitude: float, longitude: float, start_date: str, end_date: str) -> dict:
    """
    Fetch weather data from Open-Meteo API.
    
    Args:
        latitude: Location latitude
        longitude: Location longitude
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
    
    Returns:
        Dictionary containing the API response
    """
    # Setup the Open-Meteo API client with cache and retry on error
    cache_session = requests_cache.CachedSession('.cache', expire_after = -1)
    retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
    openmeteo = openmeteo_requests.Client(session = retry_session)

    base_url = "https://archive-api.open-meteo.com/v1/archive"
    
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": start_date,
        "end_date": end_date,
        "hourly": ["temperature_2m", "apparent_temperature", "relative_humidity_2m", "dew_point_2m", "precipitation", "rain", "snowfall", "snow_depth", "weather_code", "wind_speed_10m", "wind_direction_10m"],
        "timezone": "UTC"
    }
    
    try:
        responses = openmeteo.weather_api(base_url, params = params)
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None
