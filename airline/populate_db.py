from scraper import DataScraper
from database import DatabaseManager

scraper = DataScraper()
db = DatabaseManager()
flights = scraper.generate_flight_data()
db.save_flight_data(flights)
print(f"Saved {len(flights)} flights to database.")