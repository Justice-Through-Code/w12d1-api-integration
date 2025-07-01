from config import Config
from weather_data_collector import WeatherDataCollector
from weather_database import WeatherDatabase
# from dotenv import load_dotenv
from datetime import datetime
import tkinter as tk
from tkinter import ttk

# load_dotenv()
# config = Config.from_environment()

# db = WeatherDatabase(config.database_path)

db = WeatherDatabase("data/weather.db")

sample_reading = {
    "timestamp": datetime.now().isoformat(),
    "city": "New York",
    "country": "US",
    "temperature": 75.2,
    "feels_like": 76.5,
    "humidity": 60,
    "pressure": 1012.3,
    "weather_main": "Clear",
    "weather_description": "clear sky",
    "wind_speed": 5.2,
    "wind_direction": 180,
    "cloudiness": 0,
    "visibility": 10000,
    "api_timestamp": datetime.utcnow().isoformat()
}

success = db.store_weather_reading(sample_reading)
print("Insert success:", success)

# Get recent readings
readings = db.get_recent_readings("New York", "US", hours=24)
print("Recent readings:", readings)


def show_data_gui(data):
    root = tk.Tk()
    root.title("Weather Readings")

    tree = ttk.Treeview(root, columns=list(data[0].keys()), show="headings")
    for col in data[0].keys():
        tree.heading(col, text=col)
        tree.column(col, width=100)

    for row in data:
        tree.insert("", "end", values=list(row.values()))

    tree.pack(expand=True, fill="both")
    root.mainloop()

readings = db.get_recent_readings("New York", "US")
if readings:
    show_data_gui(readings)

# def main():
#     """Main application entry point."""
#     try:
#         # Load configuration
#         config = Config.from_environment()
        
#         # Initialize components
#         database = WeatherDatabase(config.database_path)
#         collector = WeatherDataCollector(config.api_key)
#         orchestrator = WeatherCollectionOrchestrator(collector, database)
        
#         # Add some locations to monitor
#         locations = [
#             ('New York', 'US'),
#             ('London', 'GB'),
#             ('Tokyo', 'JP'),
#             ('Sydney', 'AU')
#         ]
        
#         for city, country in locations:
#             orchestrator.add_location(city, country)
        
#         # Start automated collection
#         orchestrator.start_scheduled_collection(interval_minutes=30)
        
#         print("Weather data collection system started!")
#         print("Press Ctrl+C to stop...")
        
#         # Keep the main thread alive
#         try:
#             while True:
#                 time.sleep(1)
#         except KeyboardInterrupt:
#             orchestrator.stop_collection()
#             print("System stopped gracefully")
            
#     except Exception as e:
#         print(f"Failed to start system: {e}")

# if __name__ == "__main__":
#     main()
