"""
Data models and classes for Airline Market Demand Analyzer
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any
import json

@dataclass
class FlightData:
    """Flight data model"""
    route: str
    origin: str
    destination: str
    airline: str
    price: float
    date: str
    demand_score: float
    flight_number: Optional[str] = None
    aircraft_type: Optional[str] = None
    duration: Optional[int] = None  # in minutes
    distance: Optional[float] = None  # in kilometers
    booking_class: Optional[str] = 'Economy'
    availability: Optional[int] = None
    created_at: Optional[datetime] = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Validate data after initialization"""
        if self.price < 0:
            raise ValueError("Price cannot be negative")
        if not (0 <= self.demand_score <= 1):
            raise ValueError("Demand score must be between 0 and 1")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'route': self.route,
            'origin': self.origin,
            'destination': self.destination,
            'airline': self.airline,
            'price': self.price,
            'date': self.date,
            'demand_score': self.demand_score,
            'flight_number': self.flight_number,
            'aircraft_type': self.aircraft_type,
            'duration': self.duration,
            'distance': self.distance,
            'booking_class': self.booking_class,
            'availability': self.availability
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FlightData':
        """Create from dictionary"""
        return cls(**data)

@dataclass
class MarketInsight:
    """Market insight model"""
    insight_type: str
    description: str
    value: float
    trend: str
    confidence: float = 0.8
    category: str = 'general'
    severity: str = 'medium'  # low, medium, high
    actionable: bool = True
    created_at: Optional[datetime] = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'type': self.insight_type,
            'description': self.description,
            'value': self.value,
            'trend': self.trend,
            'confidence': self.confidence,
            'category': self.category,
            'severity': self.severity,
            'actionable': self.actionable
        }

@dataclass
class RouteAnalysis:
    """Route analysis model"""
    route: str
    origin: str
    destination: str
    avg_price: float
    min_price: float
    max_price: float
    flight_count: int
    demand_score: float
    price_trend: str
    popularity_rank: int
    seasonal_factor: float = 1.0
    competition_level: str = 'medium'
    
    def get_price_volatility(self) -> float:
        """Calculate price volatility"""
        if self.avg_price == 0:
            return 0
        return (self.max_price - self.min_price) / self.avg_price
    
    def is_high_demand(self) -> bool:
        """Check if route has high demand"""
        return self.demand_score > 0.7 and self.flight_count > 10

@dataclass
class LiveFlightData:
    """Live flight data from OpenSky Network"""
    callsign: str
    origin_country: str
    longitude: float
    latitude: float
    altitude: Optional[float] = None
    velocity: Optional[float] = None
    heading: Optional[float] = None
    vertical_rate: Optional[float] = None
    last_update: Optional[int] = None
    
    def is_valid(self) -> bool:
        """Check if flight data is valid"""
        return (self.callsign is not None and 
                self.longitude is not None and 
                self.latitude is not None and
                abs(self.longitude) <= 180 and
                abs(self.latitude) <= 90)

@dataclass
class PriceAlert:
    """Price alert model for future implementation"""
    user_id: str
    route: str
    target_price: float
    current_price: float
    alert_type: str  # 'below', 'above', 'change'
    is_active: bool = True
    created_at: Optional[datetime] = field(default_factory=datetime.now)
    triggered_at: Optional[datetime] = None
    
    def should_trigger(self, new_price: float) -> bool:
        """Check if alert should be triggered"""
        if not self.is_active:
            return False
        
        if self.alert_type == 'below':
            return new_price <= self.target_price
        elif self.alert_type == 'above':
            return new_price >= self.target_price
        elif self.alert_type == 'change':
            change_percent = abs(new_price - self.current_price) / self.current_price
            return change_percent >= self.target_price / 100  # target_price as percentage
        
        return False

@dataclass
class DataCollectionResult:
    """Result of data collection operation"""
    total_flights: int
    successful_flights: int
    failed_flights: int
    insights_generated: int
    execution_time: float
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate"""
        if self.total_flights == 0:
            return 0.0
        return self.successful_flights / self.total_flights
    
    def add_error(self, error: str):
        """Add error message"""
        self.errors.append(error)
    
    def add_warning(self, warning: str):
        """Add warning message"""
        self.warnings.append(warning)

class APIResponse:
    """Standard API response wrapper"""
    
    def __init__(self, status: str, data: Any = None, message: str = None, errors: List[str] = None):
        self.status = status
        self.data = data
        self.message = message
        self.errors = errors or []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON response"""
        response = {'status': self.status}
        
        if self.data is not None:
            response['data'] = self.data
        if self.message:
            response['message'] = self.message
        if self.errors:
            response['errors'] = self.errors
        
        return response
    
    @classmethod
    def success(cls, data: Any = None, message: str = None) -> 'APIResponse':
        """Create success response"""
        return cls('success', data, message)
    
    @classmethod
    def error(cls, message: str, errors: List[str] = None) -> 'APIResponse':
        """Create error response"""
        return cls('error', message=message, errors=errors)

# Enum-like classes for constants
class TrendType:
    INCREASING = 'increasing'
    DECREASING = 'decreasing'
    STABLE = 'stable'
    VOLATILE = 'volatile'

class DemandLevel:
    LOW = 'low'
    MEDIUM = 'medium'
    HIGH = 'high'
    VERY_HIGH = 'very_high'

class InsightCategory:
    PRICE = 'price'
    DEMAND = 'demand'
    ROUTE = 'route'
    AIRLINE = 'airline'
    SEASONAL = 'seasonal'
    COMPETITION = 'competition'