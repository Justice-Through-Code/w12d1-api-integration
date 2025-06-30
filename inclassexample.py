import requests
import time
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import os

class WeatherDataCollector:
    """
    A production-ready weather data collector with error handling,
    rate limiting, and robust data validation.
    """
    
    def __init__(self, api_key: str, base_url: str = "http://api.openweathermap.org/data/2.5"):
        self.api_key = api_key
        self.base_url = base_url
        self.session = requests.Session()  # Reuse connections
        self.last_request_time = 0
        self.min_request_interval = 1.0  # Minimum seconds between requests
        
        # Set up logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
    def _respect_rate_limit(self):
        """Ensure we don't exceed API rate limits."""
        time_since_last = time.time() - self.last_request_time
        if time_since_last < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last
            time.sleep(sleep_time)
        self.last_request_time = time.time()
    
    def _make_api_request(self, endpoint: str, params: Dict) -> Optional[Dict]:
        """
        Make a robust API request with error handling and retries.
        """
        self._respect_rate_limit()
        
        params['appid'] = self.api_key
        url = f"{self.base_url}/{endpoint}"
        
        max_retries = 3
        retry_delays = [1, 2, 4]  # Exponential backoff
        
        for attempt in range(max_retries):
            try:
                response = self.session.get(url, params=params, timeout=10)
                
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 429:  # Rate limited
                    self.logger.warning(f"Rate limited. Waiting before retry...")
                    time.sleep(60)  # Wait 1 minute
                    continue
                elif response.status_code == 401:
                    self.logger.error("Invalid API key")
                    return None
                else:
                    self.logger.warning(f"API returned status {response.status_code}")
                    
            except requests.exceptions.RequestException as e:
                self.logger.warning(f"Request failed (attempt {attempt + 1}): {e}")
                
            # Wait before retry (except on last attempt)
            if attempt < max_retries - 1:
                time.sleep(retry_delays[attempt])
        
        self.logger.error(f"Failed to fetch data after {max_retries} attempts")
        return None
    
    def get_current_weather(self, city: str, country_code: str = None) -> Optional[Dict]:
        """
        Fetch current weather data for a specific location.
        """
        location = city
        if country_code:
            location += f",{country_code}"
            
        params = {
            'q': location,
            'units': 'metric'
        }
        
        raw_data = self._make_api_request('weather', params)
        if raw_data:
            return self._validate_and_clean_current_weather(raw_data)
        return None
    
    def _validate_and_clean_current_weather(self, raw_data: Dict) -> Optional[Dict]:
        """
        Validate and clean the weather data before storage.
        """
        try:
            cleaned_data = {
                'timestamp': datetime.now().isoformat(),
                'city': raw_data['name'],
                'country': raw_data['sys']['country'],
                'temperature': float(raw_data['main']['temp']),
                'feels_like': float(raw_data['main']['feels_like']),
                'humidity': int(raw_data['main']['humidity']),
                'pressure': float(raw_data['main']['pressure']),
                'weather_main': raw_data['weather'][0]['main'],
                'weather_description': raw_data['weather'][0]['description'],
                'wind_speed': float(raw_data.get('wind', {}).get('speed', 0)),
                'wind_direction': int(raw_data.get('wind', {}).get('deg', 0)),
                'cloudiness': int(raw_data['clouds']['all']),
                'visibility': int(raw_data.get('visibility', 10000)),
                'api_timestamp': datetime.fromtimestamp(raw_data['dt']).isoformat()
            }
            
            # Validate reasonable ranges
            if not (-50 <= cleaned_data['temperature'] <= 60):
                self.logger.warning(f"Temperature out of range: {cleaned_data['temperature']}")
                return None
                
            if not (0 <= cleaned_data['humidity'] <= 100):
                self.logger.warning(f"Humidity out of range: {cleaned_data['humidity']}")
                return None
            
            return cleaned_data
            
        except (KeyError, ValueError, TypeError) as e:
            self.logger.error(f"Data validation failed: {e}")
            return None
