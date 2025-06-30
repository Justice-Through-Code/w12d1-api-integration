from config import Config
from weather_collector import WeatherDataCollector
from weather_database import WeatherDatabase
from dotenv import load_dotenv

load_dotenv()
config = Config.from_environment()

db = WeatherDatabase(config.database_path)

def main():
    """Main application entry point."""
    try:
        # Load configuration
        config = Config.from_environment()
        
        # Initialize components
        database = WeatherDatabase(config.database_path)
        collector = WeatherDataCollector(config.api_key)
        orchestrator = WeatherCollectionOrchestrator(collector, database)
        
        # Add some locations to monitor
        locations = [
            ('New York', 'US'),
            ('London', 'GB'),
            ('Tokyo', 'JP'),
            ('Sydney', 'AU')
        ]
        
        for city, country in locations:
            orchestrator.add_location(city, country)
        
        # Start automated collection
        orchestrator.start_scheduled_collection(interval_minutes=30)
        
        print("Weather data collection system started!")
        print("Press Ctrl+C to stop...")
        
        # Keep the main thread alive
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            orchestrator.stop_collection()
            print("System stopped gracefully")
            
    except Exception as e:
        print(f"Failed to start system: {e}")

if __name__ == "__main__":
    main()
