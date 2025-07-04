"""
Data scraping and API integration for Airline Market Demand Analyzer
"""

import requests
import json
import time
import random
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from bs4 import BeautifulSoup
import numpy as np
from dataclasses import dataclass

from config import Config
from models import FlightData, LiveFlightData

logger = logging.getLogger(__name__)

class DataScraper:
    """Data scraper for airline information"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.request_count = 0
        self.last_request_time = 0
    
    def _rate_limit(self):
        """Implement rate limiting"""
        current_time = time.time()
        if current_time - self.last_request_time < 1:  # 1 second between requests
            time.sleep(1)
        self.last_request_time = current_time
        self.request_count += 1
    
    def get_opensky_data(self) -> List[LiveFlightData]:
        """Get flight data from OpenSky Network API"""
        try:
            self._rate_limit()
            url = f"{Config.OPENSKY_API_BASE}/states/all"
            
            response = self.session.get(url, timeout=Config.get_api_timeout())
            
            if response.status_code == 200:
                data = response.json()
                flights = []
                
                if data and 'states' in data:
                    for state in data['states'][:Config.MAX_FLIGHTS_PER_REQUEST]:
                        if state and len(state) > 6:
                            try:
                                flight = LiveFlightData(
                                    callsign=state[1].strip() if state[1] else '',
                                    origin_country=state[2] if state[2] else '',
                                    longitude=state[5] if state[5] else 0,
                                    latitude=state[6] if state[6] else 0,
                                    altitude=state[7] if state[7] else None,
                                    velocity=state[9] if state[9] else None,
                                    heading=state[10] if len(state) > 10 and state[10] else None,
                                    vertical_rate=state[11] if len(state) > 11 and state[11] else None,
                                    last_update=state[4] if state[4] else None
                                )
                                if flight.is_valid():
                                    flights.append(flight)
                            except Exception as e:
                                logger.error(f"Error parsing flight data: {e}")
                                continue
                
                logger.info(f"Retrieved {len(flights)} live flights from OpenSky")
                return flights
            else:
                logger.error(f"OpenSky API error: {response.status_code}")
                return []
        except Exception as e:
            logger.error(f"Error fetching OpenSky data: {e}")
            return []
    
    def get_aviationstack_data(self) -> List[Dict]:
        """Get flight data from AviationStack API"""
        if not Config.AVIATIONSTACK_API_KEY:
            logger.warning("AviationStack API key not configured")
            return []
        
        try:
            self._rate_limit()
            url = f"{Config.AVIATIONSTACK_API_BASE}/flights"
            
            params = {
                'access_key': Config.AVIATIONSTACK_API_KEY,
                'limit': Config.MAX_FLIGHTS_PER_REQUEST,
                'flight_status': 'scheduled'  # Use 'scheduled' for consistency with your goal
            }
            
            response = self.session.get(url, params=params, timeout=Config.get_api_timeout())
            
            if response.status_code == 200:
                data = response.json()
                flights = []
                
                if 'data' in data:
                    for flight_data in data['data']:
                        flights.append({
                            'flight_number': flight_data.get('flight', {}).get('number', ''),
                            'airline': flight_data.get('airline', {}).get('name', ''),
                            'departure': flight_data.get('departure', {}),
                            'arrival': flight_data.get('arrival', {}),
                            'aircraft': flight_data.get('aircraft', {}),
                            'status': flight_data.get('flight_status', '')
                        })
                
                logger.info(f"Retrieved {len(flights)} flights from AviationStack")
                return flights
            else:
                logger.error(f"AviationStack API error: {response.status_code}")
                return []
        except Exception as e:
            logger.error(f"Error fetching AviationStack data: {e}")
            return []
    
    def scrape_flight_comparison_sites(self) -> List[Dict]:
        """Scrape flight comparison sites for supplementary data"""
        try:
            self._rate_limit()
            # Replace with a real URL (e.g., https://www.qantas.com/au/en/flight-status)
            scrape_url = "https://www.example.com/flights"  # Placeholder; adjust as needed
            response = self.session.get(scrape_url, timeout=Config.get_api_timeout())
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                routes = []
                # Example: Parse route info (adjust selectors based on target site)
                for route in soup.find_all('div', class_='route'):  # Hypothetical selector
                    origin = route.find('span', class_='origin').text.strip() if route.find('span', class_='origin') else ''
                    dest = route.find('span', class_='dest').text.strip() if route.find('span', class_='dest') else ''
                    if origin and dest:
                        routes.append({"origin": origin, "destination": dest})
                logger.info(f"Scraped {len(routes)} routes")
                return routes
            else:
                logger.error(f"Scraping Error: {response.status_code}")
                return []
        except Exception as e:
            logger.error(f"Scraping failed: {e}")
            return []
    
    def generate_synthetic_flight_data(self) -> List[FlightData]:
        """Generate synthetic flight data for Australian routes as fallback"""
        flights = []
        
        city_pairs = [
            ('Sydney', 'Melbourne'), ('Melbourne', 'Brisbane'), ('Brisbane', 'Gold Coast'),
            ('Perth', 'Adelaide'), ('Sydney', 'Brisbane'), ('Melbourne', 'Perth'),
            ('Adelaide', 'Darwin'), ('Canberra', 'Sydney'), ('Gold Coast', 'Sydney'),
            ('Brisbane', 'Cairns'), ('Sydney', 'Perth'), ('Melbourne', 'Adelaide'),
            ('Brisbane', 'Darwin'), ('Perth', 'Darwin'), ('Sydney', 'Cairns'),
            ('Melbourne', 'Gold Coast'), ('Adelaide', 'Brisbane'), ('Canberra', 'Melbourne'),
            ('Sydney', 'Adelaide'), ('Melbourne', 'Darwin'), ('Brisbane', 'Perth'),
            ('Gold Coast', 'Melbourne'), ('Cairns', 'Brisbane'), ('Darwin', 'Brisbane'),
            ('Perth', 'Brisbane'), ('Adelaide', 'Perth'), ('Sydney', 'Darwin'),
            ('Melbourne', 'Cairns'), ('Canberra', 'Brisbane'), ('Hobart', 'Melbourne')
        ]
        
        current_date = datetime.now()
        
        for origin, destination in city_pairs:
            num_flights = random.randint(1, 5)
            for _ in range(num_flights):
                airline = random.choice(Config.AUSTRALIAN_AIRLINES)
                base_price = self._calculate_base_price(origin, destination)
                price_variation = random.uniform(0.7, 1.4)
                final_price = base_price * price_variation
                demand_score = self._calculate_demand_score(origin, destination, current_date)
                flight_number = f"{airline[:2].upper()}{random.randint(100, 999)}"
                aircraft_type = random.choice(['Boeing 737', 'Airbus A320', 'Boeing 787', 'Airbus A330', 'Embraer E190'])
                duration = self._calculate_duration(origin, destination)
                distance = self._calculate_distance(origin, destination)
                
                flight = FlightData(
                    route=f"{origin} - {destination}",
                    origin=origin,
                    destination=destination,
                    airline=airline,
                    price=round(final_price, 2),
                    date=current_date.strftime('%Y-%m-%d'),
                    demand_score=round(demand_score, 2),
                    flight_number=flight_number,
                    aircraft_type=aircraft_type,
                    duration=duration,
                    distance=distance,
                    booking_class='Economy',
                    availability=random.randint(50, 200)
                )
                flights.append(flight)
        
        logger.info(f"Generated {len(flights)} synthetic flight records")
        return flights
    
    def _calculate_base_price(self, origin: str, destination: str) -> float:
        """Calculate base price for a route"""
        major_cities = ['Sydney', 'Melbourne', 'Brisbane', 'Perth']
        if origin in major_cities and destination in major_cities:
            return random.uniform(150, 350)
        elif origin in major_cities or destination in major_cities:
            return random.uniform(120, 280)
        else:
            return random.uniform(80, 200)
    
    def _calculate_demand_score(self, origin: str, destination: str, date: datetime) -> float:
        """Calculate demand score based on route and date"""
        base_demand = 0.5
        major_cities = ['Sydney', 'Melbourne', 'Brisbane', 'Perth']
        if origin in major_cities and destination in major_cities:
            base_demand += 0.2
        if date.weekday() >= 5:  # Saturday or Sunday
            base_demand += 0.1
        if date.month in [12, 1, 2, 6, 7]:  # Summer and winter holidays
            base_demand += 0.15
        random_factor = random.uniform(-0.1, 0.1)
        return max(0.1, min(0.9, base_demand + random_factor))
    
    def _calculate_duration(self, origin: str, destination: str) -> int:
        """Calculate approximate flight duration in minutes"""
        duration_map = {
            ('Sydney', 'Melbourne'): 95,
            ('Melbourne', 'Brisbane'): 140,
            ('Brisbane', 'Gold Coast'): 45,
            ('Perth', 'Adelaide'): 135,
            ('Sydney', 'Brisbane'): 110,
            ('Melbourne', 'Perth'): 210,
            ('Adelaide', 'Darwin'): 165,
            ('Canberra', 'Sydney'): 45,
            ('Sydney', 'Perth'): 310,
            ('Brisbane', 'Cairns'): 140,
            ('Sydney', 'Darwin'): 260,
            ('Melbourne', 'Darwin'): 200
        }
        key = (origin, destination)
        reverse_key = (destination, origin)
        if key in duration_map:
            return duration_map[key]
        elif reverse_key in duration_map:
            return duration_map[reverse_key]
        else:
            return random.randint(60, 300)
    
    def _calculate_distance(self, origin: str, destination: str) -> float:
        """Calculate approximate distance in kilometers"""
        distance_map = {
            ('Sydney', 'Melbourne'): 713,
            ('Melbourne', 'Brisbane'): 1374,
            ('Brisbane', 'Gold Coast'): 78,
            ('Perth', 'Adelaide'): 2130,
            ('Sydney', 'Brisbane'): 732,
            ('Melbourne', 'Perth'): 2721,
            ('Adelaide', 'Darwin'): 1530,
            ('Canberra', 'Sydney'): 248,
            ('Sydney', 'Perth'): 3278,
            ('Brisbane', 'Cairns'): 1388,
            ('Sydney', 'Darwin'): 3146,
            ('Melbourne', 'Darwin'): 3148
        }
        key = (origin, destination)
        reverse_key = (destination, origin)
        if key in distance_map:
            return distance_map[key]
        elif reverse_key in distance_map:
            return distance_map[reverse_key]
        else:
            return random.uniform(200, 3500)
    
    def get_weather_data(self, city: str) -> Dict:
        """Get weather data for a city (affects flight demand)"""
        weather_conditions = ['sunny', 'cloudy', 'rainy', 'stormy']
        temperatures = {
            'Sydney': random.randint(15, 30),
            'Melbourne': random.randint(10, 25),
            'Brisbane': random.randint(20, 35),
            'Perth': random.randint(15, 35),
            'Adelaide': random.randint(10, 30),
            'Darwin': random.randint(25, 35)
        }
        return {
            'city': city,
            'condition': random.choice(weather_conditions),
            'temperature': temperatures.get(city, random.randint(10, 35)),
            'humidity': random.randint(40, 80),
            'wind_speed': random.randint(5, 25)
        }
    
    def generate_flight_data(self) -> List[FlightData]:
        """Generate comprehensive flight data from all sources"""
        logger.info("Starting comprehensive flight data collection...")
        
        result = []
        
        try:
            # Prioritize AviationStack data
            api_flights = self.get_aviationstack_data()
            if api_flights:
                for flight in api_flights:
                    origin = flight['departure'].get('airport', 'N/A')
                    destination = flight['arrival'].get('airport', 'N/A')
                    duration = self._calculate_duration(origin, destination)
                    distance = self._calculate_distance(origin, destination)
                    base_price = self._calculate_base_price(origin, destination)
                    price_variation = random.uniform(0.7, 1.4)
                    demand_score = self._calculate_demand_score(origin, destination, datetime.now())
                    flight_data = FlightData(
                        route=f"{origin} - {destination}",
                        origin=origin,
                        destination=destination,
                        airline=flight['airline'],
                        price=round(base_price * price_variation, 2),
                        date=datetime.now().strftime('%Y-%m-%d'),
                        demand_score=round(demand_score, 2),
                        flight_number=flight['flight_number'],
                        aircraft_type=flight['aircraft'].get('code', 'N/A'),
                        duration=duration,
                        distance=distance,
                        booking_class='Economy',
                        availability=random.randint(50, 200)
                    )
                    result.append(flight_data)
            
            # Supplement with scraped routes if API data is limited
            if len(result) < Config.MAX_FLIGHTS_PER_REQUEST:
                scraped_routes = self.scrape_flight_comparison_sites()
                for route in scraped_routes:
                    if random.choice([True, False]):  # Randomly add scraped data
                        origin = route['origin']
                        destination = route['destination']
                        duration = self._calculate_duration(origin, destination)
                        distance = self._calculate_distance(origin, destination)
                        base_price = self._calculate_base_price(origin, destination)
                        price_variation = random.uniform(0.7, 1.4)
                        demand_score = self._calculate_demand_score(origin, destination, datetime.now())
                        airline = random.choice(Config.AUSTRALIAN_AIRLINES)
                        flight_number = f"{airline[:2].upper()}{random.randint(100, 999)}"
                        flight_data = FlightData(
                            route=f"{origin} - {destination}",
                            origin=origin,
                            destination=destination,
                            airline=airline,
                            price=round(base_price * price_variation, 2),
                            date=datetime.now().strftime('%Y-%m-%d'),
                            demand_score=round(demand_score, 2),
                            flight_number=flight_number,
                            aircraft_type=random.choice(['Boeing 737', 'Airbus A320']),
                            duration=duration,
                            distance=distance,
                            booking_class='Economy',
                            availability=random.randint(50, 200)
                        )
                        result.append(flight_data)
            
            # Fallback to synthetic data if both API and scraping fail or are insufficient
            if not result:
                result = self.generate_synthetic_flight_data()
            else:
                logger.info(f"Collected {len(result)} flight records from API and scraping")
            
        except Exception as e:
            logger.error(f"Error in flight data generation: {e}")
            result = self.generate_synthetic_flight_data()  # Last resort
        
        return result

if __name__ == "__main__":
    scraper = DataScraper()
    data = scraper.generate_flight_data()
    print(data)