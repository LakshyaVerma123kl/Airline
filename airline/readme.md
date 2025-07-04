Airline Market Demand Analyzer
Overview
The Airline Market Demand Analyzer is a Flask-based web application designed to collect, process, and analyze flight data to generate actionable market insights for the Australian airline industry. It integrates with APIs like OpenSky Network and AviationStack, scrapes flight comparison sites, and generates synthetic data when needed. The application provides a user-friendly dashboard with visualizations and AI-powered insights into price trends, demand patterns, route performance, airline market share, seasonal trends, and market competition.
Features

Data Collection: Fetches real-time flight data from APIs and supplements with synthetic data for Australian routes.
Data Analysis: Generates insights on price volatility, demand patterns, route popularity, airline performance, seasonal trends, and market competition.
Visualizations: Interactive charts (price distribution, route demand, market share, etc.) using Plotly.
Database Management: Stores flight data, market insights, and route analysis in a SQLite database.
Web Interface: Flask-based dashboard with HTML/CSS front-end for data exploration and insights.
Data Export: Supports exporting insights and flight data in JSON, CSV, or text formats.

Prerequisites

Python 3.8+
SQLite (included with Python)
A modern web browser for the dashboard
Optional: API keys for OpenSky Network, AviationStack, and OpenAI (for advanced AI insights)

Installation

Clone the Repository:
git clone <repository-url>
cd airline-market-demand-analyzer

Set Up a Virtual Environment:
python -m venv venv
source venv/bin/activate # On Windows: venv\Scripts\activate

Install Dependencies:
pip install -r requirements.txt

Configure Environment Variables:Create a .env file in the project root and add the following:
FLASK_ENV=development
SECRET_KEY=your-secret-key-change-in-production
AVIATIONSTACK_API_KEY=your-aviationstack-api-key
OPENAI_API_KEY=your-openai-api-key # Optional
LOG_LEVEL=INFO

Initialize the Database:Run the database initialization and populate it with sample data:
python populate_db.py

Usage

Run the Application:
python app.py

The application will start on http://0.0.0.0:5000.

Access the Dashboard:Open a web browser and navigate to http://localhost:5000 to view the main dashboard. Explore additional pages:

/routes: Route analysis
/insights: AI-generated market insights

API Endpoints:

POST /api/collect-data: Trigger data collection and processing.
GET /api/dashboard-data: Retrieve dashboard data and visualizations.
GET /api/route-analysis: Get route-specific analysis.
GET /api/filter-data: Filter flight data by price, airline, origin, etc.
GET /api/export-data: Export flight data as CSV.

Generate Synthetic Data (if API data is unavailable):
python populate_db.py

Project Structure
airline-market-demand-analyzer/
├── **init**.py
├── app.py # Flask application
├── config.py # Configuration settings
├── data_processor.py # Data collection and processing
├── ai_insights.py # AI-powered insights generation
├── scraper.py # API integration and web scraping
├── database.py # Database operations
├── utils.py # Utility functions for visualizations
├── models.py # Data models
├── populate_db.py # Script to populate database
├── templates/ # HTML templates
│ ├── index.html
│ ├── routes.html
│ ├── insights.html
│ ├── 404.html
│ └── 500.html
├── static/ # CSS, JS, and other static files
│ ├── css/
│ └── js/
├── airline_data.db # SQLite database
└── requirements.txt # Python dependencies

Dependencies
See requirements.txt for a complete list of Python dependencies. Key libraries include:

Flask: Web framework
Pandas: Data processing
Plotly: Data visualization
Requests: API calls
BeautifulSoup4: Web scraping
SQLite3: Database management

Configuration
The config.py file contains settings for:

API endpoints and keys (OpenSky, AviationStack, OpenAI)
Database configuration
Rate limiting
Australian cities and airlines
Price ranges and demand factors
Logging settings

Modify config.py or use environment variables to customize settings.
Notes

API Keys: Obtain keys from AviationStack and OpenAI (optional) for full functionality. Without keys, the application falls back to synthetic data.
Data Retention: Data older than 30 days is automatically cleaned (configurable in config.py).
Logging: Logs are written to airline_analyzer.log for debugging and monitoring.
Future Features: Price alerts (ENABLE_PRICE_ALERTS) are planned but currently disabled.

Contributing
Contributions are welcome! Please:

Fork the repository
Create a feature branch
Submit a pull request with clear descriptions of changes

License
This project is licensed under the MIT License.
Author
Lakshya Verma
