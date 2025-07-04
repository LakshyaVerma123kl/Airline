"""
Airline Market Demand Analyzer - Main Flask Application
Author: Lakshya Verma
"""

import os
import json
import logging
from flask import Flask, render_template, request, jsonify
from plotly.utils import PlotlyJSONEncoder
from dotenv import load_dotenv

# Load environment variables first
load_dotenv()

from config import Config
from data_processor import DataProcessor
from utils import create_charts

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = Config.SECRET_KEY

# Validate configuration on startup
try:
    Config.validate_required_config()
    logger.info("✅ All required configuration loaded successfully!")
except ValueError as e:
    logger.error(f"❌ Configuration error: {e}")
    # For production, you might want to exit gracefully
    # For now, we'll continue but log the error

# Initialize global processor
try:
    processor = DataProcessor()
    logger.info("✅ Data processor initialized successfully!")
except Exception as e:
    logger.error(f"❌ Error initializing data processor: {e}")
    processor = None

@app.route('/')
def index():
    """Main dashboard page"""
    try:
        return render_template('index.html')
    except Exception as e:
        logger.error(f"Error rendering index.html: {e}")
        return jsonify({'status': 'error', 'message': 'Template rendering failed'}), 500

@app.route('/health')
def health_check():
    """Health check endpoint for deployment monitoring"""
    return jsonify({
        'status': 'healthy',
        'message': 'Airline Market Demand Analyzer is running',
        'processor_status': 'initialized' if processor else 'not initialized'
    })

@app.route('/routes')
def routes_page():
    """Routes analysis page"""
    try:
        return render_template('routes.html')
    except Exception as e:
        logger.error(f"Error rendering routes.html: {e}")
        return jsonify({'status': 'error', 'message': 'Template rendering failed'}), 500

@app.route('/insights')
def insights_page():
    """AI Insights page"""
    try:
        return render_template('insights.html')
    except Exception as e:
        logger.error(f"Error rendering insights.html: {e}")
        return jsonify({'status': 'error', 'message': 'Template rendering failed'}), 500

@app.route('/api/collect-data', methods=['POST'])
def collect_data():
    """API endpoint to trigger data collection"""
    if not processor:
        return jsonify({
            'status': 'error',
            'message': 'Data processor not initialized'
        }), 500
    
    try:
        result = processor.collect_and_process_data()
        return jsonify({
            'status': 'success',
            'message': f'Collected {result["total_flights"]} flights',
            'insights_count': len(result['insights'])
        })
    except Exception as e:
        logger.error(f"Error collecting data: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/dashboard-data')
def get_dashboard_data():
    """Get dashboard data"""
    if not processor:
        return jsonify({
            'status': 'error',
            'message': 'Data processor not initialized'
        }), 500
    
    try:
        df = processor.db_manager.get_flight_data()
        insights = processor.ai_generator.generate_insights(df)
        
        # Create visualizations
        charts = create_charts(df)
        
        return jsonify({
            'status': 'success',
            'data': {
                'total_flights': len(df),
                'avg_price': round(df['price'].mean(), 2) if not df.empty else 0,
                'avg_demand': round(df['demand_score'].mean(), 2) if not df.empty else 0,
                'total_routes': len(df['route'].unique()) if not df.empty else 0,
                'insights': [
                    {
                        'type': insight.insight_type,
                        'description': insight.description,
                        'value': float(insight.value),  # Ensure JSON-serializable
                        'trend': insight.trend
                    } for insight in insights
                ],
                'charts': charts
            }
        })
    except Exception as e:
        logger.error(f"Error getting dashboard data: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/route-analysis')
def route_analysis():
    """Get route analysis data"""
    if not processor:
        return jsonify({
            'status': 'error',
            'message': 'Data processor not initialized'
        }), 500
    
    try:
        df = processor.db_manager.get_flight_data()
        
        if df.empty:
            return jsonify({
                'status': 'success',
                'data': {
                    'routes': [],
                    'price_trends': {},
                    'demand_analysis': {}
                }
            })
        
        # Route analysis
        route_stats = df.groupby('route').agg({
            'price': ['mean', 'min', 'max', 'count'],
            'demand_score': 'mean'
        }).round(2)
        
        routes_data = []
        for route in route_stats.index:
            routes_data.append({
                'route': route,
                'avg_price': float(route_stats.loc[route, ('price', 'mean')]),
                'min_price': float(route_stats.loc[route, ('price', 'min')]),
                'max_price': float(route_stats.loc[route, ('price', 'max')]),
                'flight_count': int(route_stats.loc[route, ('price', 'count')]),
                'demand_score': float(route_stats.loc[route, ('demand_score', 'mean')])
            })
        
        # Sort by flight count
        routes_data.sort(key=lambda x: x['flight_count'], reverse=True)
        
        return jsonify({
            'status': 'success',
            'data': {
                'routes': routes_data,
                'total_routes': len(routes_data)
            }
        })
        
    except Exception as e:
        logger.error(f"Error in route analysis: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/filter-data')
def filter_data():
    """Filter data based on user criteria"""
    if not processor:
        return jsonify({
            'status': 'error',
            'message': 'Data processor not initialized'
        }), 500
    
    try:
        # Get filter parameters
        min_price = request.args.get('min_price', type=float)
        max_price = request.args.get('max_price', type=float)
        airline = request.args.get('airline')
        origin = request.args.get('origin')
        destination = request.args.get('destination')
        
        df = processor.db_manager.get_flight_data()
        
        # Apply filters
        if min_price is not None:
            df = df[df['price'] >= min_price]
        if max_price is not None:
            df = df[df['price'] <= max_price]
        if airline:
            df = df[df['airline'] == airline]
        if origin:
            df = df[df['origin'] == origin]
        if destination:
            df = df[df['destination'] == destination]
        
        # Create filtered charts
        charts = create_charts(df)
        
        return jsonify({
            'status': 'success',
            'data': {
                'total_flights': len(df),
                'charts': charts,
                'filtered_data': df.to_dict('records')
            }
        })
        
    except Exception as e:
        logger.error(f"Error filtering data: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/export-data')
def export_data():
    """Export data to CSV"""
    if not processor:
        return jsonify({
            'status': 'error',
            'message': 'Data processor not initialized'
        }), 500
    
    try:
        df = processor.db_manager.get_flight_data()
        
        # Create CSV content
        csv_content = df.to_csv(index=False)
        
        return jsonify({
            'status': 'success',
            'csv_data': csv_content,
            'filename': f'airline_data_{processor.db_manager.get_current_timestamp()}.csv'
        })
        
    except Exception as e:
        logger.error(f"Error exporting data: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    try:
        return render_template('404.html'), 404
    except Exception as e:
        logger.error(f"Error rendering 404.html: {e}")
        return jsonify({'status': 'error', 'message': 'Page not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    try:
        return render_template('500.html'), 500
    except Exception as e:
        logger.error(f"Error rendering 500.html: {e}")
        return jsonify({'status': 'error', 'message': 'Internal server error'}), 500

if __name__ == '__main__':
    # Create directories (for local development)
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)
    
    # Get port from environment variable or default to 5000
    port = int(os.environ.get('PORT', 5000))
    
    # Run the app
    app.run(
        debug=Config.is_development(),
        host='0.0.0.0',
        port=port
    )