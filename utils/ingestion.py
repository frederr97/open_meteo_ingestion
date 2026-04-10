import requests
import time
import json
from pathlib import Path

class Ingestion:
    """Manager class for handling data ingestion operations."""

    def __init__(self):
        """Initialize the IngestionManager."""
        pass
    
    def get_request(self, source, params=None, retries=5, backoff_factor=0.2):
        """
        Fetch JSON data from a given source with retries.
        
        Args:
            source: Data source URL or endpoint
            params: Optional query parameters for the request
            retries: Number of retry attempts on failure
            backoff_factor: Base backoff delay in seconds
            
        Returns:
            Parsed JSON response, or None if the request failed
        """
        for attempt in range(retries):
            try:
                response = requests.get(source, params=params)
                response.raise_for_status()
                return response.json()
            except requests.exceptions.RequestException as e:
                if attempt == retries - 1:
                    print(f"Error fetching data after {retries} attempts: {e}")
                    return None
                time.sleep(backoff_factor * (2 ** attempt))

    def load_cities(self):
        """
        Load cities and their coordinates from config file.
        
        Returns:
            Dictionary with city names as keys and dicts with latitude/longitude as values
        """
        config_path = Path(__file__).parent.parent / "config" / "cities.json"
        try:
            with open(config_path) as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Config file not found: {config_path}")
            return {}
        except json.JSONDecodeError as e:
            print(f"Error parsing config file: {e}")
            return {}
