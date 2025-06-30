import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional
from contextlib import contextmanager

class WeatherDatabase:
    """
    A robust database interface for weather data storage and retrieval.
    """
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database with required tables and indexes."""
        with self.get_connection() as conn:
            # Read and execute schema file
            schema_sql = """
            -- Core weather readings table
            CREATE TABLE IF NOT EXISTS weather_readings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                city TEXT NOT NULL,
                country TEXT NOT NULL,
                temperature REAL NOT NULL,
                feels_like REAL,
                humidity INTEGER,
                pressure REAL,
                weather_main TEXT,
                weather_description TEXT,
                wind_speed REAL,
                wind_direction INTEGER,
                cloudiness INTEGER,
                visibility INTEGER,
                api_timestamp TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE IF NOT EXISTS locations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                city TEXT NOT NULL,
                country TEXT NOT NULL,
                latitude REAL,
                longitude REAL,
                timezone TEXT,
                is_active BOOLEAN DEFAULT 1,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(city, country)
            );
            
            CREATE TABLE IF NOT EXISTS collection_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                endpoint TEXT NOT NULL,
                location_id INTEGER,
                status TEXT NOT NULL,
                error_message TEXT,
                response_time_ms INTEGER,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (location_id) REFERENCES locations (id)
            );
            
            -- Create indexes
            CREATE INDEX IF NOT EXISTS idx_weather_readings_timestamp 
            ON weather_readings(timestamp);
            
            CREATE INDEX IF NOT EXISTS idx_weather_readings_city 
            ON weather_readings(city, country);
            
            CREATE INDEX IF NOT EXISTS idx_collection_log_timestamp 
            ON collection_log(timestamp);
            """
            
            conn.executescript(schema_sql)
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
    
    def store_weather_reading(self, weather_data: Dict) -> bool:
        """
        Store a weather reading in the database.
        """
        try:
            with self.get_connection() as conn:
                conn.execute("""
                    INSERT INTO weather_readings (
                        timestamp, city, country, temperature, feels_like,
                        humidity, pressure, weather_main, weather_description,
                        wind_speed, wind_direction, cloudiness, visibility, api_timestamp
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    weather_data['timestamp'],
                    weather_data['city'],
                    weather_data['country'],
                    weather_data['temperature'],
                    weather_data['feels_like'],
                    weather_data['humidity'],
                    weather_data['pressure'],
                    weather_data['weather_main'],
                    weather_data['weather_description'],
                    weather_data['wind_speed'],
                    weather_data['wind_direction'],
                    weather_data['cloudiness'],
                    weather_data['visibility'],
                    weather_data['api_timestamp']
                ))
                return True
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return False
    
    def get_recent_readings(self, city: str, country: str, hours: int = 24) -> List[Dict]:
        """
        Retrieve recent weather readings for a specific location.
        """
        with self.get_connection() as conn:
            cursor = conn.execute("""
                SELECT * FROM weather_readings 
                WHERE city = ? AND country = ? 
                AND datetime(timestamp) > datetime('now', '-{} hours')
                ORDER BY timestamp DESC
            """.format(hours), (city, country))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def log_collection_attempt(self, endpoint: str, location_id: Optional[int], 
                             status: str, error_message: Optional[str] = None,
                             response_time_ms: Optional[int] = None):
        """
        Log a data collection attempt for monitoring purposes.
        """
        with self.get_connection() as conn:
            conn.execute("""
                INSERT INTO collection_log (
                    timestamp, endpoint, location_id, status, 
                    error_message, response_time_ms
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                datetime.now().isoformat(),
                endpoint,
                location_id,
                status,
                error_message,
                response_time_ms
            ))
