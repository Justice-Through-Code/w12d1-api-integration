import os
from dataclasses import dataclass

@dataclass
class Config:
    """Application configuration with secure defaults.
    This class holds all the configuration values needed by your app — 
    things like API credentials, file paths, and retry settings.
    """
    api_key: str            # Required credential to authenticate with the weather API
    database_path: str      # Path to the SQLite database file for storing weather data
    log_level: str = "INFO" # Controls logging verbosity: DEBUG, INFO, WARNING, etc.
    max_retries: int = 3    # Number of retry attempts for failed API requests
    request_timeout: int = 10 # Max wait time (in seconds) before an API call is aborted
    
    @classmethod
    def from_environment(cls):
        """This method instantiates a Config object using environment variables, 
        which is ideal for production deployments or CI pipelines."""
        api_key = os.getenv('WEATHER_API_KEY') # Tries to load the WEATHER_API_KEY from the environment.
        if not api_key:
            raise ValueError("WEATHER_API_KEY environment variable required")
            
        return cls(
            api_key=api_key,
            database_path=os.getenv('DATABASE_PATH', 'weather_data.db'),
            log_level=os.getenv('LOG_LEVEL', 'INFO'),
            max_retries=int(os.getenv('MAX_RETRIES', '3')),
            request_timeout=int(os.getenv('REQUEST_TIMEOUT', '10'))
        )
