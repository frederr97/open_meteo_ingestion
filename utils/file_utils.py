import json

from pathlib import Path
from typing import Any, List, Union

class FileUtils:
    """Utility class for file operations."""

    @staticmethod
    def write_json(data: Any, filepath: Union[str, Path]) -> None:
        """
        Write data to a JSON file.
        
        Args:
            data: Data to serialize to JSON
            filepath: Path where the JSON file will be written
        """
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, "w") as f:
            json.dump(data, f)

    @staticmethod
    def read_json(filepath: Union[str, Path]) -> Any:
        """
        Read data from a JSON file.
        
        Args:
            filepath: Path to the JSON file
            
        Returns:
            Parsed JSON data
        """
        with open(filepath, "r") as f:
            return json.load(f)

    @staticmethod
    def file_exists(filepath: Union[str, Path]) -> bool:
        """Check if a file exists."""
        return Path(filepath).exists()

    @staticmethod
    def create_directory(dirpath: Union[str, Path]) -> None:
        """Create a directory if it doesn't exist."""
        Path(dirpath).mkdir(parents=True, exist_ok=True)

    @staticmethod
    def list_files(dirpath: Union[str, Path], extension: str = None) -> List[Path]:
        """
        List all files in a directory.
        
        Args:
            dirpath: Directory path
            extension: Optional file extension filter (e.g., '.json')
            
        Returns:
            List of file paths
        """
        dirpath = Path(dirpath)
        if extension:
            return list(dirpath.glob(f"*{extension}"))
        return [f for f in dirpath.iterdir() if f.is_file()]