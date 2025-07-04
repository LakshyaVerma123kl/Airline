"""
Database operations for Airline Market Demand Analyzer
"""

import sqlite3
import pandas as pd
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from contextlib import contextmanager

from config import Config
from models import FlightData, MarketInsight, RouteAnalysis

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Database operations manager"""
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or Config.get_database_path()
        self.init_database()
    
    def init_database(self):
        """Initialize database with required tables"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Flight data table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS flight_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    route TEXT NOT NULL,
                    origin TEXT NOT NULL,
                    destination TEXT NOT NULL,
                    airline TEXT NOT NULL,
                    price REAL NOT NULL,
                    date TEXT NOT NULL,
                    demand_score REAL NOT NULL,
                    flight_number TEXT,
                    aircraft_type TEXT,
                    duration INTEGER,
                    distance REAL,
                    booking_class TEXT DEFAULT 'Economy',
                    availability INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(route, airline, date, flight_number)
                )
            ''')
            
            # Market insights table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS market_insights (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    insight_type TEXT NOT NULL,
                    description TEXT NOT NULL,
                    value REAL NOT NULL,
                    trend TEXT NOT NULL,
                    confidence REAL DEFAULT 0.8,
                    category TEXT DEFAULT 'general',
                    severity TEXT DEFAULT 'medium',
                    actionable BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Route analysis table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS route_analysis (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    route TEXT NOT NULL,
                    origin TEXT NOT NULL,
                    destination TEXT NOT NULL,
                    avg_price REAL NOT NULL,
                    min_price REAL NOT NULL,
                    max_price REAL NOT NULL,
                    flight_count INTEGER NOT NULL,
                    demand_score REAL NOT NULL,
                    price_trend TEXT NOT NULL,
                    popularity_rank INTEGER,
                    seasonal_factor REAL DEFAULT 1.0,
                    competition_level TEXT DEFAULT 'medium',
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(route)
                )
            ''')
            
            # Live flight data table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS live_flights (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    callsign TEXT NOT NULL,
                    origin_country TEXT NOT NULL,
                    longitude REAL NOT NULL,
                    latitude REAL NOT NULL,
                    altitude REAL,
                    velocity REAL,
                    heading REAL,
                    vertical_rate REAL,
                    last_update INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create indexes for better performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_flight_route ON flight_data(route)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_flight_date ON flight_data(date)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_flight_airline ON flight_data(airline)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_flight_price ON flight_data(price)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_insight_type ON market_insights(insight_type)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_route_analysis_route ON route_analysis(route)')
            
            conn.commit()
            logger.info("Database initialized successfully")
    
    @contextmanager
    def get_connection(self):
        """Get database connection with context manager"""
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
        finally:
            conn.close()
    
    def save_flight_data(self, flights: List[FlightData]) -> int:
        """Save flight data to database"""
        if not flights:
            return 0
        
        saved_count = 0
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            for flight in flights:
                try:
                    cursor.execute('''
                        INSERT OR REPLACE INTO flight_data 
                        (route, origin, destination, airline, price, date, demand_score,
                         flight_number, aircraft_type, duration, distance, booking_class, availability)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        flight.route, flight.origin, flight.destination, flight.airline,
                        flight.price, flight.date, flight.demand_score, flight.flight_number,
                        flight.aircraft_type, flight.duration, flight.distance,
                        flight.booking_class, flight.availability
                    ))
                    saved_count += 1
                except sqlite3.Error as e:
                    logger.error(f"Error saving flight data: {e}")
                    continue
            
            conn.commit()
            logger.info(f"Saved {saved_count} flight records")
        
        return saved_count
    
    def get_flight_data(self, days: int = 30, limit: int = None) -> pd.DataFrame:
        """Get flight data from database"""
        with self.get_connection() as conn:
            query = '''
                SELECT * FROM flight_data 
                WHERE created_at >= datetime('now', '-{} days')
                ORDER BY created_at DESC
            '''.format(days)
            
            if limit:
                query += f' LIMIT {limit}'
            
            df = pd.read_sql_query(query, conn)
            return df
    
    def save_market_insights(self, insights: List[MarketInsight]) -> int:
        """Save market insights to database"""
        if not insights:
            return 0
        
        saved_count = 0
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            for insight in insights:
                try:
                    cursor.execute('''
                        INSERT INTO market_insights 
                        (insight_type, description, value, trend, confidence, category, severity, actionable)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        insight.insight_type, insight.description, insight.value, insight.trend,
                        insight.confidence, insight.category, insight.severity, insight.actionable
                    ))
                    saved_count += 1
                except sqlite3.Error as e:
                    logger.error(f"Error saving insight: {e}")
                    continue
            
            conn.commit()
            logger.info(f"Saved {saved_count} insights")
        
        return saved_count
    
    def get_market_insights(self, days: int = 7, category: str = None) -> List[Dict]:
        """Get market insights from database"""
        with self.get_connection() as conn:
            query = '''
                SELECT * FROM market_insights 
                WHERE created_at >= datetime('now', '-{} days')
            '''.format(days)
            
            params = []
            if category:
                query += ' AND category = ?'
                params.append(category)
            
            query += ' ORDER BY created_at DESC'
            
            cursor = conn.cursor()
            cursor.execute(query, params)
            
            columns = [desc[0] for desc in cursor.description]
            results = []
            
            for row in cursor.fetchall():
                results.append(dict(zip(columns, row)))
            
            return results
    
    def save_route_analysis(self, analyses: List[RouteAnalysis]) -> int:
        """Save route analysis to database"""
        if not analyses:
            return 0
        
        saved_count = 0
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            for analysis in analyses:
                try:
                    cursor.execute('''
                        INSERT OR REPLACE INTO route_analysis 
                        (route, origin, destination, avg_price, min_price, max_price,
                         flight_count, demand_score, price_trend, popularity_rank,
                         seasonal_factor, competition_level)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        analysis.route, analysis.origin, analysis.destination,
                        analysis.avg_price, analysis.min_price, analysis.max_price,
                        analysis.flight_count, analysis.demand_score, analysis.price_trend,
                        analysis.popularity_rank, analysis.seasonal_factor, analysis.competition_level
                    ))
                    saved_count += 1
                except sqlite3.Error as e:
                    logger.error(f"Error saving route analysis: {e}")
                    continue
            
            conn.commit()
            logger.info(f"Saved {saved_count} route analyses")
        
        return saved_count
    
    def get_route_analysis(self, route: str = None) -> pd.DataFrame:
        """Get route analysis from database"""
        with self.get_connection() as conn:
            query = 'SELECT * FROM route_analysis'
            params = []
            
            if route:
                query += ' WHERE route = ?'
                params.append(route)
            
            query += ' ORDER BY popularity_rank ASC'
            
            df = pd.read_sql_query(query, conn, params=params)
            return df
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            stats = {}
            
            # Flight data stats
            cursor.execute('SELECT COUNT(*) FROM flight_data')
            stats['total_flights'] = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(DISTINCT route) FROM flight_data')
            stats['total_routes'] = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(DISTINCT airline) FROM flight_data')
            stats['total_airlines'] = cursor.fetchone()[0]
            
            cursor.execute('SELECT AVG(price) FROM flight_data')
            avg_price = cursor.fetchone()[0]
            stats['avg_price'] = round(avg_price, 2) if avg_price else 0
            
            cursor.execute('SELECT AVG(demand_score) FROM flight_data')
            avg_demand = cursor.fetchone()[0]
            stats['avg_demand'] = round(avg_demand, 2) if avg_demand else 0
            
            # Insights stats
            cursor.execute('SELECT COUNT(*) FROM market_insights')
            stats['total_insights'] = cursor.fetchone()[0]
            
            # Recent data stats
            cursor.execute('''
                SELECT COUNT(*) FROM flight_data 
                WHERE created_at >= datetime('now', '-1 days')
            ''')
            stats['flights_last_24h'] = cursor.fetchone()[0]
            
            return stats
    
    def clean_old_data(self, days: int = None):
        """Clean old data from database"""
        days = days or Config.DATA_RETENTION_DAYS
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Clean old flight data
            cursor.execute('''
                DELETE FROM flight_data 
                WHERE created_at < datetime('now', '-{} days')
            '''.format(days))
            flights_deleted = cursor.rowcount
            
            # Clean old insights
            cursor.execute('''
                DELETE FROM market_insights 
                WHERE created_at < datetime('now', '-{} days')
            '''.format(days))
            insights_deleted = cursor.rowcount
            
            # Clean old live flight data (keep only last 24 hours)
            cursor.execute('''
                DELETE FROM live_flights 
                WHERE created_at < datetime('now', '-1 days')
            ''')
            live_flights_deleted = cursor.rowcount
            
            conn.commit()
            
            logger.info(f"Cleaned {flights_deleted} old flight records, "
                       f"{insights_deleted} old insights, "
                       f"{live_flights_deleted} old live flights")
    
    def get_top_routes(self, limit: int = 10) -> List[Dict]:
        """Get top routes by flight count"""
        with self.get_connection() as conn:
            query = '''
                SELECT route, COUNT(*) as flight_count, 
                       AVG(price) as avg_price, AVG(demand_score) as avg_demand
                FROM flight_data 
                GROUP BY route 
                ORDER BY flight_count DESC 
                LIMIT ?
            '''
            
            cursor = conn.cursor()
            cursor.execute(query, (limit,))
            
            columns = [desc[0] for desc in cursor.description]
            results = []
            
            for row in cursor.fetchall():
                result = dict(zip(columns, row))
                result['avg_price'] = round(result['avg_price'], 2)
                result['avg_demand'] = round(result['avg_demand'], 2)
                results.append(result)
            
            return results
    
    def get_price_trends(self, route: str = None, days: int = 30) -> pd.DataFrame:
        """Get price trends over time"""
        with self.get_connection() as conn:
            query = '''
                SELECT date, route, AVG(price) as avg_price, COUNT(*) as flight_count
                FROM flight_data 
                WHERE created_at >= datetime('now', '-{} days')
            '''.format(days)
            
            params = []
            if route:
                query += ' AND route = ?'
                params.append(route)
            
            query += ' GROUP BY date, route ORDER BY date DESC'
            
            df = pd.read_sql_query(query, conn, params=params)
            return df
    
    def search_flights(self, filters: Dict[str, Any]) -> pd.DataFrame:
        """Search flights with filters"""
        with self.get_connection() as conn:
            query = 'SELECT * FROM flight_data WHERE 1=1'
            params = []
            
            if filters.get('origin'):
                query += ' AND origin = ?'
                params.append(filters['origin'])
            
            if filters.get('destination'):
                query += ' AND destination = ?'
                params.append(filters['destination'])
            
            if filters.get('airline'):
                query += ' AND airline = ?'
                params.append(filters['airline'])
            
            if filters.get('min_price'):
                query += ' AND price >= ?'
                params.append(filters['min_price'])
            
            if filters.get('max_price'):
                query += ' AND price <= ?'
                params.append(filters['max_price'])
            
            if filters.get('date_from'):
                query += ' AND date >= ?'
                params.append(filters['date_from'])
            
            if filters.get('date_to'):
                query += ' AND date <= ?'
                params.append(filters['date_to'])
            
            query += ' ORDER BY created_at DESC'
            
            if filters.get('limit'):
                query += f' LIMIT {filters["limit"]}'
            
            df = pd.read_sql_query(query, conn, params=params)
            return df
    
    def get_current_timestamp(self) -> str:
        """Get current timestamp as string"""
        return datetime.now().strftime('%Y%m%d_%H%M%S')
    
    def backup_database(self, backup_path: str = None) -> str:
        """Create database backup"""
        if not backup_path:
            timestamp = self.get_current_timestamp()
            backup_path = f'backup_airline_data_{timestamp}.db'
        
        with self.get_connection() as conn:
            backup_conn = sqlite3.connect(backup_path)
            conn.backup(backup_conn)
            backup_conn.close()
        
        logger.info(f"Database backup created: {backup_path}")
        return backup_path
    
    def get_data_quality_report(self) -> Dict[str, Any]:
        """Generate data quality report"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            report = {}
            
            # Check for missing data
            cursor.execute('SELECT COUNT(*) FROM flight_data WHERE price IS NULL OR price <= 0')
            report['invalid_prices'] = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM flight_data WHERE demand_score IS NULL OR demand_score < 0 OR demand_score > 1')
            report['invalid_demand_scores'] = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM flight_data WHERE route IS NULL OR route = ""')
            report['missing_routes'] = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM flight_data WHERE airline IS NULL OR airline = ""')
            report['missing_airlines'] = cursor.fetchone()[0]
            
            # Check for duplicates
            cursor.execute('''
                SELECT COUNT(*) FROM (
                    SELECT route, airline, date, COUNT(*) as cnt
                    FROM flight_data 
                    GROUP BY route, airline, date 
                    HAVING cnt > 1
                )
            ''')
            report['duplicate_flights'] = cursor.fetchone()[0]
            
            # Data freshness
            cursor.execute('SELECT MAX(created_at) FROM flight_data')
            latest_data = cursor.fetchone()[0]
            report['latest_data_timestamp'] = latest_data
            
            if latest_data:
                latest_dt = datetime.fromisoformat(latest_data.replace('Z', '+00:00'))
                hours_old = (datetime.now() - latest_dt).total_seconds() / 3600
                report['data_age_hours'] = round(hours_old, 2)
            
            return report