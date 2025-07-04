"""
Data processing module for Airline Market Demand Analyzer
"""
import logging
from typing import Dict, List, Any
from ai_insights import AIInsightGenerator
from database import DatabaseManager
from scraper import DataScraper

logger = logging.getLogger(__name__)

class DataProcessor:
    """Main data processing class"""
    
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.ai_generator = AIInsightGenerator()
        self.scraper = DataScraper()
    
    def collect_and_process_data(self) -> Dict[str, Any]:
        """Collect and process data from all sources"""
        try:
            # Collect data
            data = self.scraper.get_comprehensive_data()
            
            # Save flight data
            flights = data['synthetic_flights']
            saved_count = self.db_manager.save_flight_data(flights)
            
            # Generate insights
            df = self.db_manager.get_flight_data()
            insights = self.ai_generator.generate_insights(df)
            self.db_manager.save_market_insights(insights)
            
            return {
                'total_flights': len(flights),
                'saved_flights': saved_count,
                'insights': insights,
                'status': 'success'
            }
        except Exception as e:
            logger.error(f"Error in data collection and processing: {e}")
            return {'status': 'error', 'message': str(e)}