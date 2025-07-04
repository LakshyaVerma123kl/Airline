"""
AI-powered market insights generator for Airline Market Demand Analyzer
Author: Lakshya Verma
"""

import pandas as pd
import numpy as np
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import json
import statistics

from config import Config
from models import MarketInsight, FlightData, TrendType, DemandLevel, InsightCategory

logger = logging.getLogger(__name__)

class AIInsightGenerator:
    """Generate AI-powered market insights from flight data"""
    
    def __init__(self):
        self.openai_api_key = Config.OPENAI_API_KEY
        self.insights_cache = {}
        self.last_analysis_time = None
    
    def generate_insights(self, data: pd.DataFrame) -> List[MarketInsight]:
        """Generate comprehensive market insights from flight data"""
        if data.empty:
            return []
        
        insights = []
        
        # Price analysis insights
        insights.extend(self._analyze_price_trends(data))
        
        # Demand analysis insights
        insights.extend(self._analyze_demand_patterns(data))
        
        # Route analysis insights
        insights.extend(self._analyze_route_performance(data))
        
        # Airline analysis insights
        insights.extend(self._analyze_airline_performance(data))
        
        # Seasonal analysis insights
        insights.extend(self._analyze_seasonal_patterns(data))
        
        # Competition analysis insights
        insights.extend(self._analyze_market_competition(data))
        
        # Predictive insights
        insights.extend(self._generate_predictive_insights(data))
        
        logger.info(f"Generated {len(insights)} market insights")
        return insights
    
    def _analyze_price_trends(self, data: pd.DataFrame) -> List[MarketInsight]:
        """Analyze price trends and patterns"""
        insights = []
        
        try:
            # Overall price statistics
            avg_price = data['price'].mean()
            median_price = data['price'].median()
            price_std = data['price'].std()
            
            # Price volatility analysis
            volatility = price_std / avg_price if avg_price > 0 else 0
            
            volatility_insight = MarketInsight(
                insight_type="Price Volatility",
                description=f"Market shows {'high' if volatility > 0.3 else 'moderate' if volatility > 0.15 else 'low'} price volatility at {volatility:.1%}",
                value=volatility,
                trend=TrendType.VOLATILE if volatility > 0.3 else TrendType.STABLE,
                confidence=0.85,
                category=InsightCategory.PRICE,
                severity='high' if volatility > 0.3 else 'medium'
            )
            insights.append(volatility_insight)
            
            # Price distribution analysis
            price_ranges = {
                'budget': (0, 150),
                'mid_range': (150, 300),
                'premium': (300, float('inf'))
            }
            
            for category, (min_price, max_price) in price_ranges.items():
                count = len(data[(data['price'] >= min_price) & (data['price'] < max_price)])
                percentage = count / len(data) * 100
                
                if percentage > 40:  # Significant presence
                    insights.append(MarketInsight(
                        insight_type="Price Segment",
                        description=f"{category.title()} flights dominate the market at {percentage:.1f}%",
                        value=percentage,
                        trend=TrendType.STABLE,
                        confidence=0.9,
                        category=InsightCategory.PRICE
                    ))
            
            # Price-demand correlation
            if 'demand_score' in data.columns:
                correlation = data['price'].corr(data['demand_score'])
                
                if abs(correlation) > 0.3:  # Significant correlation
                    insights.append(MarketInsight(
                        insight_type="Price-Demand Correlation",
                        description=f"{'Strong positive' if correlation > 0.5 else 'Moderate positive' if correlation > 0.3 else 'Moderate negative' if correlation < -0.3 else 'Strong negative'} correlation between price and demand",
                        value=correlation,
                        trend=TrendType.INCREASING if correlation > 0 else TrendType.DECREASING,
                        confidence=0.8,
                        category=InsightCategory.PRICE
                    ))
            
        except Exception as e:
            logger.error(f"Error in price trend analysis: {e}")
        
        return insights
    
    def _analyze_demand_patterns(self, data: pd.DataFrame) -> List[MarketInsight]:
        """Analyze demand patterns and trends"""
        insights = []
        
        try:
            avg_demand = data['demand_score'].mean()
            
            # Overall demand level
            demand_level = (
                DemandLevel.VERY_HIGH if avg_demand > 0.8 else
                DemandLevel.HIGH if avg_demand > 0.6 else
                DemandLevel.MEDIUM if avg_demand > 0.4 else
                DemandLevel.LOW
            )
            
            insights.append(MarketInsight(
                insight_type="Overall Demand",
                description=f"Market demand is {demand_level} with an average score of {avg_demand:.2f}",
                value=avg_demand,
                trend=TrendType.STABLE,
                confidence=0.9,
                category=InsightCategory.DEMAND,
                severity='high' if demand_level in [DemandLevel.VERY_HIGH, DemandLevel.HIGH] else 'medium'
            ))
            
            # High-demand routes
            high_demand_routes = data[data['demand_score'] > 0.7]['route'].value_counts()
            if not high_demand_routes.empty:
                top_route = high_demand_routes.index[0]
                insights.append(MarketInsight(
                    insight_type="High Demand Route",
                    description=f"Route '{top_route}' shows highest demand with {high_demand_routes.iloc[0]} high-demand flights",
                    value=high_demand_routes.iloc[0],
                    trend=TrendType.INCREASING,
                    confidence=0.85,
                    category=InsightCategory.ROUTE
                ))
            
            # Demand variability
            demand_std = data['demand_score'].std()
            if demand_std > 0.2:
                insights.append(MarketInsight(
                    insight_type="Demand Variability",
                    description=f"High variability in demand across routes (std: {demand_std:.2f})",
                    value=demand_std,
                    trend=TrendType.VOLATILE,
                    confidence=0.8,
                    category=InsightCategory.DEMAND,
                    severity='medium'
                ))
            
        except Exception as e:
            logger.error(f"Error in demand pattern analysis: {e}")
        
        return insights
    
    def _analyze_route_performance(self, data: pd.DataFrame) -> List[MarketInsight]:
        """Analyze route performance and popularity"""
        insights = []
        
        try:
            # Route popularity analysis
            route_counts = data['route'].value_counts()
            total_routes = len(route_counts)
            
            # Compute average price for the entire dataset
            avg_price = data['price'].mean()
            
            # Most popular routes
            if not route_counts.empty:
                top_route = route_counts.index[0]
                top_count = route_counts.iloc[0]
                
                insights.append(MarketInsight(
                    insight_type="Most Popular Route",
                    description=f"Route '{top_route}' is most popular with {top_count} flights",
                    value=top_count,
                    trend=TrendType.INCREASING,
                    confidence=0.95,
                    category=InsightCategory.ROUTE
                ))
            
            # Route concentration analysis
            top_10_routes = route_counts.head(10).sum()
            concentration = top_10_routes / len(data) * 100
            
            if concentration > 50:
                insights.append(MarketInsight(
                    insight_type="Route Concentration",
                    description=f"Top 10 routes account for {concentration:.1f}% of all flights",
                    value=concentration,
                    trend=TrendType.STABLE,
                    confidence=0.9,
                    category=InsightCategory.ROUTE,
                    severity='medium'
                ))
            
            # Route price efficiency
            route_price_avg = data.groupby('route')['price'].mean()
            route_demand_avg = data.groupby('route')['demand_score'].mean()
            
            # Find routes with high demand but low prices (good value)
            efficient_routes = []
            for route in route_price_avg.index:
                if route_demand_avg[route] > 0.6 and route_price_avg[route] < avg_price:
                    efficient_routes.append(route)
            
            if efficient_routes:
                insights.append(MarketInsight(
                    insight_type="Value Routes",
                    description=f"Found {len(efficient_routes)} routes with high demand but competitive pricing",
                    value=len(efficient_routes),
                    trend=TrendType.STABLE,
                    confidence=0.8,
                    category=InsightCategory.ROUTE,
                    actionable=True
                ))
            
        except Exception as e:
            logger.error(f"Error in route performance analysis: {e}")
        
        return insights
    
    def _analyze_airline_performance(self, data: pd.DataFrame) -> List[MarketInsight]:
        """Analyze airline performance and market share"""
        insights = []
        
        try:
            # Market share analysis
            airline_counts = data['airline'].value_counts()
            total_flights = len(data)
            
            # Leading airline
            if not airline_counts.empty:
                leading_airline = airline_counts.index[0]
                market_share = airline_counts.iloc[0] / total_flights * 100
                
                insights.append(MarketInsight(
                    insight_type="Market Leader",
                    description=f"{leading_airline} leads the market with {market_share:.1f}% market share",
                    value=market_share,
                    trend=TrendType.STABLE,
                    confidence=0.95,
                    category=InsightCategory.AIRLINE
                ))
            
            # Market concentration
            top_3_airlines = airline_counts.head(3).sum()
            concentration = top_3_airlines / total_flights * 100
            
            insights.append(MarketInsight(
                insight_type="Market Concentration",
                description=f"Top 3 airlines control {concentration:.1f}% of the market",
                value=concentration,
                trend=TrendType.STABLE,
                confidence=0.9,
                category=InsightCategory.AIRLINE,
                severity='high' if concentration > 70 else 'medium'
            ))
            
            # Airline pricing analysis
            airline_avg_price = data.groupby('airline')['price'].mean()
            airline_demand = data.groupby('airline')['demand_score'].mean()
            
            # Find premium airlines (high price, high demand)
            premium_airlines = []
            for airline in airline_avg_price.index:
                if airline_avg_price[airline] > data['price'].mean() * 1.2:
                    premium_airlines.append(airline)
            
            if premium_airlines:
                insights.append(MarketInsight(
                    insight_type="Premium Airlines",
                    description=f"{len(premium_airlines)} airlines operate in the premium segment",
                    value=len(premium_airlines),
                    trend=TrendType.STABLE,
                    confidence=0.8,
                    category=InsightCategory.AIRLINE
                ))
            
        except Exception as e:
            logger.error(f"Error in airline performance analysis: {e}")
        
        return insights
    
    def _analyze_seasonal_patterns(self, data: pd.DataFrame) -> List[MarketInsight]:
        """Analyze seasonal patterns and trends"""
        insights = []
        
        try:
            # Convert date to datetime for analysis
            data['date_parsed'] = pd.to_datetime(data['date'])
            data['month'] = data['date_parsed'].dt.month
            data['weekday'] = data['date_parsed'].dt.dayofweek
            
            # Monthly patterns
            monthly_demand = data.groupby('month')['demand_score'].mean()
            monthly_price = data.groupby('month')['price'].mean()
            
            # Find peak months
            peak_demand_month = monthly_demand.idxmax()
            peak_price_month = monthly_price.idxmax()
            
            month_names = {
                1: 'January', 2: 'February', 3: 'March', 4: 'April',
                5: 'May', 6: 'June', 7: 'July', 8: 'August',
                9: 'September', 10: 'October', 11: 'November', 12: 'December'
            }
            
            insights.append(MarketInsight(
                insight_type="Peak Demand Month",
                description=f"{month_names[peak_demand_month]} shows highest demand with score {monthly_demand[peak_demand_month]:.2f}",
                value=monthly_demand[peak_demand_month],
                trend=TrendType.INCREASING,
                confidence=0.8,
                category=InsightCategory.SEASONAL
            ))
            
            # Weekend vs weekday patterns
            weekend_demand = data[data['weekday'] >= 5]['demand_score'].mean()
            weekday_demand = data[data['weekday'] < 5]['demand_score'].mean()
            
            if weekend_demand > weekday_demand * 1.1:
                insights.append(MarketInsight(
                    insight_type="Weekend Premium",
                    description=f"Weekend flights show {((weekend_demand/weekday_demand - 1) * 100):.1f}% higher demand",
                    value=weekend_demand / weekday_demand,
                    trend=TrendType.INCREASING,
                    confidence=0.85,
                    category=InsightCategory.SEASONAL
                ))
            
        except Exception as e:
            logger.error(f"Error in seasonal pattern analysis: {e}")
        
        return insights
    
    def _analyze_market_competition(self, data: pd.DataFrame) -> List[MarketInsight]:
        """Analyze market competition and dynamics"""
        insights = []
        
        try:
            # Route competition analysis
            route_airline_count = data.groupby('route')['airline'].nunique()
            
            # Highly competitive routes
            competitive_routes = route_airline_count[route_airline_count >= 3]
            if not competitive_routes.empty:
                insights.append(MarketInsight(
                    insight_type="Competitive Routes",
                    description=f"{len(competitive_routes)} routes have 3+ airlines competing",
                    value=len(competitive_routes),
                    trend=TrendType.INCREASING,
                    confidence=0.9,
                    category=InsightCategory.COMPETITION
                ))
            
            # Monopolistic routes
            monopolistic_routes = route_airline_count[route_airline_count == 1]
            if not monopolistic_routes.empty:
                insights.append(MarketInsight(
                    insight_type="Monopolistic Routes",
                    description=f"{len(monopolistic_routes)} routes served by single airline",
                    value=len(monopolistic_routes),
                    trend=TrendType.STABLE,
                    confidence=0.9,
                    category=InsightCategory.COMPETITION,
                    severity='high'
                ))
            
            # Price dispersion in competitive routes
            if not competitive_routes.empty:
                competitive_route_names = competitive_routes.index.tolist()
                competitive_data = data[data['route'].isin(competitive_route_names)]
                
                route_price_std = competitive_data.groupby('route')['price'].std()
                avg_price_std = route_price_std.mean()
                
                if avg_price_std > 50:  # High price variance
                    insights.append(MarketInsight(
                        insight_type="Price Competition",
                        description=f"Competitive routes show high price variance (avg std: ${avg_price_std:.2f})",
                        value=avg_price_std,
                        trend=TrendType.VOLATILE,
                        confidence=0.8,
                        category=InsightCategory.COMPETITION
                    ))
            
        except Exception as e:
            logger.error(f"Error in market competition analysis: {e}")
        
        return insights
    
    def _generate_predictive_insights(self, data: pd.DataFrame) -> List[MarketInsight]:
        """Generate predictive insights and recommendations"""
        insights = []
        
        try:
            # Predict price trends based on demand
            high_demand_routes = data[data['demand_score'] > 0.7]['route'].unique()
            
            if len(high_demand_routes) > 0:
                # Predict price increases for high-demand routes
                high_demand_data = data[data['route'].isin(high_demand_routes)]
                avg_price_high_demand = high_demand_data['price'].mean()
                overall_avg_price = data['price'].mean()
                
                price_premium = (avg_price_high_demand / overall_avg_price - 1) * 100
                
                insights.append(MarketInsight(
                    insight_type="Price Prediction",
                    description=f"High-demand routes command {price_premium:.1f}% price premium, expect further increases",
                    value=price_premium,
                    trend=TrendType.INCREASING,
                    confidence=0.7,
                    category=InsightCategory.PRICE,
                    actionable=True
                ))
            
            # Identify emerging opportunities
            route_growth = data.groupby('route').size().sort_values(ascending=False)
            emerging_routes = route_growth[route_growth >= 5]  # Routes with decent activity
            
            if not emerging_routes.empty:
                insights.append(MarketInsight(
                    insight_type="Market Opportunity",
                    description=f"Identified {len(emerging_routes)} routes with growth potential",
                    value=len(emerging_routes),
                    trend=TrendType.INCREASING,
                    confidence=0.6,
                    category=InsightCategory.ROUTE,
                    actionable=True
                ))
            
            # Capacity utilization insights
            if 'availability' in data.columns:
                avg_availability = data['availability'].mean()
                low_availability_routes = data[data['availability'] < avg_availability * 0.8]['route'].unique()
                
                if len(low_availability_routes) > 0:
                    insights.append(MarketInsight(
                        insight_type="Capacity Constraint",
                        description=f"{len(low_availability_routes)} routes showing capacity constraints",
                        value=len(low_availability_routes),
                        trend=TrendType.DECREASING,
                        confidence=0.8,
                        category=InsightCategory.DEMAND,
                        severity='high',
                        actionable=True
                    ))
            
        except Exception as e:
            logger.error(f"Error in predictive insights generation: {e}")
        
        return insights
    
    def generate_summary_report(self, insights: List[MarketInsight]) -> Dict[str, Any]:
        """Generate a summary report of all insights"""
        if not insights:
            return {'status': 'no_insights', 'summary': 'No insights generated'}
        
        summary = {
            'total_insights': len(insights),
            'categories': {},
            'severity_distribution': {'high': 0, 'medium': 0, 'low': 0},
            'actionable_insights': 0,
            'key_findings': [],
            'recommendations': []
        }
        
        # Categorize insights
        for insight in insights:
            category = insight.category
            if category not in summary['categories']:
                summary['categories'][category] = 0
            summary['categories'][category] += 1
            
            # Count severity
            summary['severity_distribution'][insight.severity] += 1
            
            # Count actionable insights
            if insight.actionable:
                summary['actionable_insights'] += 1
            
            # Collect high-confidence insights as key findings
            if insight.confidence > 0.8:
                summary['key_findings'].append({
                    'type': insight.insight_type,
                    'description': insight.description,
                    'confidence': insight.confidence
                })
        
        # Generate recommendations based on insights
        summary['recommendations'] = self._generate_recommendations(insights)
        
        return summary
    
    def _generate_recommendations(self, insights: List[MarketInsight]) -> List[str]:
        """Generate actionable recommendations based on insights"""
        recommendations = []
        
        # Price-based recommendations
        price_insights = [i for i in insights if i.category == InsightCategory.PRICE]
        if price_insights:
            high_volatility = any(i.insight_type == "Price Volatility" and i.value > 0.3 for i in price_insights)
            if high_volatility:
                recommendations.append("Consider dynamic pricing strategies to capitalize on price volatility")
        
        # Demand-based recommendations
        demand_insights = [i for i in insights if i.category == InsightCategory.DEMAND]
        if demand_insights:
            high_demand = any(i.insight_type == "Overall Demand" and i.value > 0.7 for i in demand_insights)
            if high_demand:
                recommendations.append("Increase capacity on high-demand routes to capture market share")
        
        # Route-based recommendations
        route_insights = [i for i in insights if i.category == InsightCategory.ROUTE]
        if route_insights:
            value_routes = any(i.insight_type == "Value Routes" for i in route_insights)
            if value_routes:
                recommendations.append("Focus marketing efforts on value routes with high demand and competitive pricing")
        
        # Competition-based recommendations
        competition_insights = [i for i in insights if i.category == InsightCategory.COMPETITION]
        if competition_insights:
            monopolistic = any(i.insight_type == "Monopolistic Routes" for i in competition_insights)
            if monopolistic:
                recommendations.append("Explore opportunities on monopolistic routes for potential market entry")
        
        return recommendations
    
    def export_insights(self, insights: List[MarketInsight], format: str = 'json') -> str:
        """Export insights in specified format"""
        if format == 'json':
            insights_data = [insight.to_dict() for insight in insights]
            return json.dumps(insights_data, indent=2, default=str)
        
        elif format == 'csv':
            insights_data = [insight.to_dict() for insight in insights]
            df = pd.DataFrame(insights_data)
            return df.to_csv(index=False)
        
        elif format == 'text':
            text_output = "Market Insights Report\n" + "=" * 50 + "\n\n"
            
            for insight in insights:
                text_output += f"Type: {insight.insight_type}\n"
                text_output += f"Description: {insight.description}\n"
                text_output += f"Value: {insight.value}\n"
                text_output += f"Trend: {insight.trend}\n"
                text_output += f"Confidence: {insight.confidence:.1%}\n"
                text_output += f"Category: {insight.category}\n"
                text_output += f"Severity: {insight.severity}\n"
                text_output += "-" * 30 + "\n\n"
            
            return text_output
        
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def get_insights_by_category(self, insights: List[MarketInsight], category: str) -> List[MarketInsight]:
        """Filter insights by category"""
        return [insight for insight in insights if insight.category == category]
    
    def get_high_priority_insights(self, insights: List[MarketInsight]) -> List[MarketInsight]:
        """Get high priority insights (high confidence and actionable)"""
        return [
            insight for insight in insights 
            if insight.confidence > 0.8 and insight.actionable and insight.severity == 'high'
        ]