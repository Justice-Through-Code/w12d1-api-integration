import os
from dataclasses import dataclass

@dataclass
class Config:
    """Application configuration with secure defaults."""
    api_key: str
    database_path: str
    log_level: str = "INFO"
    max_retries: int = 3
    request_timeout: int = 10
    
    @classmethod
    def from_environment(cls):
        """Load configuration from environment variables."""
        api_key = os.getenv('WEATHER_API_KEY')
        if not api_key:
            raise ValueError("WEATHER_API_KEY environment variable required")
            
        return cls(
            api_key=api_key,
            database_path=os.getenv('DATABASE_PATH', 'weather_data.db'),
            log_level=os.getenv('LOG_LEVEL', 'INFO'),
            max_retries=int(os.getenv('MAX_RETRIES', '3')),
            request_timeout=int(os.getenv('REQUEST_TIMEOUT', '10'))
        )
