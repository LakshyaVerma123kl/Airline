"""
Configuration settings for Airline Market Demand Analyzer
"""

import os
from datetime import timedelta

class Config:
    """Application configuration"""
    
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-change-in-production'
    
    # Database settings
    DATABASE = 'airline_data.db'
    DATABASE_URL = os.environ.get('DATABASE_URL') or f'sqlite:///{DATABASE}'
    
    # API Configuration
    OPENSKY_API_BASE = 'https://opensky-network.org/api'
    AVIATIONSTACK_API_KEY = os.environ.get('AVIATIONSTACK_API_KEY')
    AVIATIONSTACK_API_BASE = 'http://api.aviationstack.com/v1'
    AVIATIONSTACK_API_KEY = '54a5ffea2c6db23b236d3bfa8af7e051'
    # OpenAI Configuration (optional)
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    
    # Rate limiting
    API_RATE_LIMIT = 100  # requests per minute
    
    # Data collection settings
    MAX_FLIGHTS_PER_REQUEST = 50
    DATA_RETENTION_DAYS = 30
    
    # Cache settings
    CACHE_TYPE = 'simple'
    CACHE_DEFAULT_TIMEOUT = 300  # 5 minutes
    
    # Australian cities for route generation
    AUSTRALIAN_CITIES = [
        'Sydney', 'Melbourne', 'Brisbane', 'Perth', 'Adelaide', 
        'Gold Coast', 'Canberra', 'Darwin', 'Hobart', 'Cairns',
        'Townsville', 'Geelong', 'Newcastle', 'Wollongong', 'Sunshine Coast'
    ]
    
    # Airlines operating in Australia
    AUSTRALIAN_AIRLINES = [
        'Qantas', 'Virgin Australia', 'Jetstar', 'Tigerair Australia',
        'Regional Express', 'Alliance Airlines', 'Bonza'
    ]
    
    # Price ranges for different route types
    PRICE_RANGES = {
        'domestic_short': (79, 199),      # Under 2 hours
        'domestic_medium': (149, 299),    # 2-4 hours
        'domestic_long': (199, 399),      # 4+ hours
        'international_short': (299, 599), # To New Zealand
        'international_long': (599, 1299)  # To Asia/US/Europe
    }
    
    # Demand factors
    DEMAND_FACTORS = {
        'peak_season': 1.3,    # Dec-Feb, Jun-Aug
        'shoulder_season': 1.1, # Mar-May, Sep-Nov
        'low_season': 0.8,     # May, Aug-Sep
        'weekend': 1.2,
        'weekday': 0.9,
        'business_route': 1.4,  # Major city pairs
        'leisure_route': 1.1    # Tourist destinations
    }
    
    # Logging configuration
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = 'airline_analyzer.log'
    
    # Feature flags
    ENABLE_AI_INSIGHTS = True
    ENABLE_REAL_TIME_DATA = True
    ENABLE_DATA_EXPORT = True
    ENABLE_PRICE_ALERTS = False  # Future feature
    
    @staticmethod
    def get_database_path():
        """Get the full path to the database file"""
        return os.path.join(os.getcwd(), Config.DATABASE)
    
    @staticmethod
    def is_development():
        """Check if running in development mode"""
        return os.environ.get('FLASK_ENV') == 'development'
    
    @staticmethod
    def get_api_timeout():
        """Get API timeout based on environment"""
        return 10 if Config.is_development() else 30