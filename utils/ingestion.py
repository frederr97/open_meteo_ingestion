import requests
import time

class IngestionManager:
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
