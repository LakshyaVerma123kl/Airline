"""
Utility functions for Airline Market Demand Analyzer
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.utils import PlotlyJSONEncoder
import json
import logging

logger = logging.getLogger(__name__)

# Define a custom color palette for differentiation (works for both dark and light themes)
CUSTOM_COLORS = [
    '#1f77b4',  # Blue
    '#ff7f0e',  # Orange
    '#2ca02c',  # Green
    '#d62728',  # Red
    '#9467bd',  # Purple
    '#8c564b',  # Brown
    '#e377c2',  # Pink
    '#7f7f7f',  # Gray
    '#bcbd22',  # Olive
    '#17becf'   # Cyan
]

def create_charts(df: pd.DataFrame) -> dict:
    """Create visualizations for dashboard with custom colors"""
    charts = {}
    
    if df.empty:
        logger.warning("Empty DataFrame provided to create_charts, returning empty charts")
        return charts
    
    try:
        # Price distribution chart
        price_fig = px.histogram(
            df,
            x='price',
            nbins=30,
            title='Price Distribution',
            labels={'price': 'Ticket Price ($)'},
            template='plotly_dark',
            color_discrete_sequence=[CUSTOM_COLORS[0]]  # Single color for histogram
        )
        charts['price_distribution'] = json.loads(json.dumps(price_fig.to_dict(), cls=PlotlyJSONEncoder))
        
        # Demand by route chart
        route_demand = df.groupby('route')['demand_score'].mean().sort_values(ascending=False).head(10)
        demand_fig = px.bar(
            x=route_demand.values,
            y=route_demand.index,
            orientation='h',
            title='Top 10 Routes by Demand',
            labels={'x': 'Average Demand Score', 'y': 'Route'},
            template='plotly_dark',
            color=route_demand.index,  # Color by route
            color_discrete_sequence=CUSTOM_COLORS  # Apply custom color palette
        )
        charts['route_demand'] = json.loads(json.dumps(demand_fig.to_dict(), cls=PlotlyJSONEncoder))
        
        # Airline market share
        airline_counts = df['airline'].value_counts()
        market_share_fig = px.pie(
            names=airline_counts.index,
            values=airline_counts.values,
            title='Airline Market Share',
            template='plotly_dark',
            color_discrete_sequence=CUSTOM_COLORS  # Apply custom color palette
        )
        charts['market_share'] = json.loads(json.dumps(market_share_fig.to_dict(), cls=PlotlyJSONEncoder))
        
        # Price trends over time for top routes
        try:
            df['date'] = pd.to_datetime(df['date'])
            unique_dates = df['date'].nunique()
            top_routes = df['route'].value_counts().head(5).index
            
            # Check if we have enough date variation for trends
            if unique_dates > 1:
                price_trends = df[df['route'].isin(top_routes)].groupby(['date', 'route'])['price'].mean().reset_index()
                
                # Only create chart if we have data points
                if not price_trends.empty:
                    price_trend_fig = px.line(
                        price_trends,
                        x='date',
                        y='price',
                        color='route',
                        title='Price Trends for Top 5 Routes',
                        labels={'price': 'Average Price ($)', 'date': 'Date'},
                        template='plotly_dark',
                        color_discrete_sequence=CUSTOM_COLORS
                    )
                    charts['price_trends'] = json.loads(json.dumps(price_trend_fig.to_dict(), cls=PlotlyJSONEncoder))
                else:
                    logger.info("No price trends data available after grouping")
            else:
                logger.info(f"Insufficient date variation for price trends - only {unique_dates} unique dates")
                
                # Alternative: Show price variation by route instead
                route_price_stats = df.groupby('route')['price'].agg(['mean', 'min', 'max']).reset_index()
                route_price_stats = route_price_stats.sort_values('mean', ascending=False).head(10)
                
                price_range_fig = px.bar(
                    route_price_stats,
                    x='route',
                    y='mean',
                    title='Average Prices by Route (Top 10)',
                    labels={'route': 'Route', 'mean': 'Average Price ($)'},
                    template='plotly_dark',
                    color='route',
                    color_discrete_sequence=CUSTOM_COLORS
                )
                
                # Add error bars to show price range
                price_range_fig.update_traces(
                    error_y=dict(
                        type='data',
                        array=route_price_stats['max'] - route_price_stats['mean'],
                        arrayminus=route_price_stats['mean'] - route_price_stats['min'],
                        visible=True
                    )
                )
                
                charts['price_by_route'] = json.loads(json.dumps(price_range_fig.to_dict(), cls=PlotlyJSONEncoder))
                
        except Exception as e:
            logger.error(f"Error creating price trends chart: {e}")
            logger.error(f"Date column info: {df['date'].dtype if 'date' in df.columns else 'No date column'}")
            logger.error(f"Date range: {df['date'].min()} to {df['date'].max()}" if 'date' in df.columns else "No date data")
        
    except Exception as e:
        logger.error(f"Error in create_charts: {e}")
        return charts
    
    # Seasonal demand patterns - Fixed version (moved to end)
    try:
        df['month'] = df['date'].dt.month
        monthly_demand = df.groupby('month')['demand_score'].mean().reset_index()
        
        # Only create seasonal chart if we have data for multiple months
        if len(monthly_demand) > 1:
            month_names = {
                1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun',
                7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'
            }
            monthly_demand['month_name'] = monthly_demand['month'].map(month_names)
            seasonal_fig = px.bar(
                monthly_demand,
                x='month_name',
                y='demand_score',
                title='Seasonal Demand Patterns',
                labels={'month_name': 'Month', 'demand_score': 'Average Demand Score'},
                template='plotly_dark',
                color='month_name',  # Color by month
                color_discrete_sequence=CUSTOM_COLORS  # Apply custom color palette
            )
            charts['seasonal_demand'] = json.loads(json.dumps(seasonal_fig.to_dict(), cls=PlotlyJSONEncoder))
        else:
            logger.info("Insufficient data for seasonal analysis - only one month available")
            
            # Alternative: Show demand by day of week instead
            df['day_of_week'] = df['date'].dt.day_name()
            daily_demand = df.groupby('day_of_week')['demand_score'].mean().reset_index()
            
            # Order days properly
            day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            daily_demand['day_of_week'] = pd.Categorical(daily_demand['day_of_week'], categories=day_order, ordered=True)
            daily_demand = daily_demand.sort_values('day_of_week')
            
            daily_fig = px.bar(
                daily_demand,
                x='day_of_week',
                y='demand_score',
                title='Demand Patterns by Day of Week',
                labels={'day_of_week': 'Day of Week', 'demand_score': 'Average Demand Score'},
                template='plotly_dark',
                color='day_of_week',
                color_discrete_sequence=CUSTOM_COLORS
            )
            charts['daily_demand'] = json.loads(json.dumps(daily_fig.to_dict(), cls=PlotlyJSONEncoder))
            
    except Exception as e:
        logger.error(f"Error creating seasonal/daily demand chart: {e}")
    
    return charts