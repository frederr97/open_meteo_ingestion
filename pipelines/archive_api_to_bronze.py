import json
import requests
import time

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
    base_url = "https://archive-api.open-meteo.com/v1/archive"
    
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": start_date,
        "end_date": end_date,
        "hourly": ["temperature_2m", "apparent_temperature", "relative_humidity_2m", "dew_point_2m", "precipitation", "rain", "snowfall", "snow_depth", "weather_code", "wind_speed_10m", "wind_direction_10m"],
        "timezone": "UTC"
    }
    
    for attempt in range(5):
        try:
            response = requests.get(base_url, params=params)
            return response.json()
        except requests.exceptions.RequestException as e:
            if attempt == 4:
                print(f"Error fetching data after 5 attempts: {e}")
                return None
            time.sleep(0.2 * (2 ** attempt))

def main():
    """Main function to run the weather data fetching pipeline."""
    latitude = 52.52
    longitude = 13.41
    start_date = "2023-01-01"
    end_date = "2023-01-02"
    
    response = fetch_weather_data(latitude, longitude, start_date, end_date)
    
    if response:
        print("Weather data fetched successfully")
        with open("weather_data.json", "w") as f:
            json.dump(response, f, indent=2, default=str)
        print("Data written to weather_data.json")
    else:
        print("Failed to fetch weather data")

if __name__ == "__main__":
    main()