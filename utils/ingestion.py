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

    def load_config_json(self, *config_types):
        """
        Load one or more configuration files from the config directory.

        Args:
            *config_types: Names of config files to load without the .json extension.
                If none are provided, all JSON files in the config folder are loaded.

        Returns:
            dict: Mapping config name to parsed JSON content. Missing or invalid files
                return an empty dict for that config.
        """

        # Define the path to the "config" folder
        config_dir = Path(__file__).parent.parent / "config"

        if config_types:
            files = {config_type: f"{config_type}.json" for config_type in config_types}
        else:
            files = {path.stem: path.name for path in config_dir.glob("*.json")}

        config_data = {}
        for config_type, file_name in files.items():
            config_path = config_dir / file_name

            try:
                with open(config_path, "r") as f:
                    config_data[config_type] = json.load(f)

            except FileNotFoundError:
                print(f"Config file not found: {config_path}")
                config_data[config_type] = {}

            except json.JSONDecodeError as e:
                print(f"Error parsing JSON file {config_path}: {e}")
                config_data[config_type] = {}

        return config_data