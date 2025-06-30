import schedule
import threading
from datetime import datetime, timedelta
from typing import List
import time
import WeatherDataCollector
import WeatherDatabase

class WeatherCollectionOrchestrator:
    """
    Orchestrates automated weather data collection across multiple locations.
    """
    
    def __init__(self, collector: WeatherDataCollector, database: WeatherDatabase):
        self.collector = collector
        self.database = database
        self.is_running = False
        self.collection_thread = None
        
    def add_location(self, city: str, country: str) -> bool:
        """Add a new location to monitor."""
        try:
            with self.database.get_connection() as conn:
                conn.execute("""
                    INSERT OR IGNORE INTO locations (city, country, is_active)
                    VALUES (?, ?, 1)
                """, (city, country))
                return True
        except sqlite3.Error:
            return False
    
    def get_active_locations(self) -> List[Dict]:
        """Get all active monitoring locations."""
        with self.database.get_connection() as conn:
            cursor = conn.execute("""
                SELECT id, city, country FROM locations WHERE is_active = 1
            """)
            return [dict(row) for row in cursor.fetchall()]
    
    def collect_for_location(self, location: Dict):
        """Collect weather data for a specific location."""
        start_time = time.time()
        
        try:
            weather_data = self.collector.get_current_weather(
                location['city'], 
                location['country']
            )
            
            if weather_data:
                success = self.database.store_weather_reading(weather_data)
                response_time = int((time.time() - start_time) * 1000)
                
                status = 'success' if success else 'storage_error'
                self.database.log_collection_attempt(
                    'current_weather',
                    location['id'],
                    status,
                    response_time_ms=response_time
                )
            else:
                self.database.log_collection_attempt(
                    'current_weather',
                    location['id'],
                    'api_error',
                    error_message='Failed to retrieve weather data'
                )
                
        except Exception as e:
            self.database.log_collection_attempt(
                'current_weather',
                location['id'],
                'error',
                error_message=str(e)
            )
    
    def collect_all_locations(self):
        """Collect weather data for all active locations."""
        locations = self.get_active_locations()
        print(f"Collecting data for {len(locations)} locations...")
        
        for location in locations:
            self.collect_for_location(location)
            time.sleep(1)  # Rate limiting between locations
    
    def start_scheduled_collection(self, interval_minutes: int = 30):
        """Start automated data collection on a schedule."""
        # Schedule collection every interval_minutes
        schedule.every(interval_minutes).minutes.do(self.collect_all_locations)
        
        # Also schedule an immediate collection
        schedule.every().minute.do(self.collect_all_locations).tag('immediate')
        
        self.is_running = True
        
        def run_scheduler():
            while self.is_running:
                schedule.run_pending()
                time.sleep(1)
        
        self.collection_thread = threading.Thread(target=run_scheduler)
        self.collection_thread.daemon = True
        self.collection_thread.start()
        
        # Run immediate collection once, then remove the tag
        schedule.clear('immediate')
        
        print(f"Started automated collection every {interval_minutes} minutes")
    
    def stop_collection(self):
        """Stop the automated collection system."""
        self.is_running = False
        schedule.clear()
        if self.collection_thread:
            self.collection_thread.join(timeout=5)
        print("Stopped automated collection")
