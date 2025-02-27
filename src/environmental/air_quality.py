"""Air quality monitoring and analysis system for eco vehicles."""

import numpy as np
from dataclasses import dataclass
from typing import Dict, List, Optional
from datetime import datetime
import logging

@dataclass
class AirQualityMetrics:
    """Air quality measurement metrics."""
    co2_level: float  # in ppm
    co_level: float   # in ppm
    nox_level: float  # in ppm
    pm25_level: float # in μg/m³
    pm10_level: float # in μg/m³
    timestamp: datetime

    def is_within_limits(self) -> bool:
        """Check if all metrics are within acceptable limits."""
        return (
            self.co2_level < 5000 and  # OSHA standard
            self.co_level < 9 and      # EPA standard
            self.nox_level < 0.1 and   # EPA standard
            self.pm25_level < 35 and   # EPA standard
            self.pm10_level < 150      # EPA standard
        )

class AirQualityMonitor:
    """Monitor and analyze air quality metrics."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.history: List[AirQualityMetrics] = []
        self.alert_callbacks: List[callable] = []
    
    def add_measurement(self, metrics: AirQualityMetrics) -> None:
        """Add new air quality measurement."""
        self.history.append(metrics)
        if not metrics.is_within_limits():
            self._trigger_alerts(metrics)
    
    def get_average_metrics(self, window_size: int = 10) -> Optional[AirQualityMetrics]:
        """Calculate average metrics over the last window_size measurements."""
        if not self.history:
            return None
            
        recent = self.history[-window_size:]
        return AirQualityMetrics(
            co2_level=np.mean([m.co2_level for m in recent]),
            co_level=np.mean([m.co_level for m in recent]),
            nox_level=np.mean([m.nox_level for m in recent]),
            pm25_level=np.mean([m.pm25_level for m in recent]),
            pm10_level=np.mean([m.pm10_level for m in recent]),
            timestamp=datetime.now()
        )
    
    def register_alert_callback(self, callback: callable) -> None:
        """Register callback for air quality alerts."""
        self.alert_callbacks.append(callback)
    
    def _trigger_alerts(self, metrics: AirQualityMetrics) -> None:
        """Trigger registered alert callbacks."""
        for callback in self.alert_callbacks:
            try:
                callback(metrics)
            except Exception as e:
                self.logger.error(f"Error in alert callback: {e}")

class EmissionsCalculator:
    """Calculate and analyze vehicle emissions."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.emission_factors = {
            'electric': 0.0,      # Direct emissions
            'hybrid': 89.0,       # g CO2/km
            'gasoline': 192.0,    # g CO2/km
            'diesel': 171.0       # g CO2/km
        }
    
    def calculate_emissions(self, 
                          vehicle_type: str,
                          distance: float,
                          additional_factors: Optional[Dict[str, float]] = None) -> float:
        """
        Calculate emissions for a given vehicle type and distance.
        
        Args:
            vehicle_type: Type of vehicle (electric, hybrid, gasoline, diesel)
            distance: Distance traveled in kilometers
            additional_factors: Additional emission factors to consider
            
        Returns:
            Total emissions in grams of CO2
        """
        if vehicle_type not in self.emission_factors:
            raise ValueError(f"Unknown vehicle type: {vehicle_type}")
            
        base_emissions = self.emission_factors[vehicle_type] * distance
        
        if additional_factors:
            # Apply additional factors (e.g., weather, driving style)
            for factor, value in additional_factors.items():
                base_emissions *= value
                
        return base_emissions
    
    def compare_emissions(self, 
                         base_vehicle: str,
                         eco_vehicle: str,
                         yearly_distance: float) -> Dict[str, float]:
        """Compare emissions between two vehicle types."""
        base_emissions = self.calculate_emissions(base_vehicle, yearly_distance)
        eco_emissions = self.calculate_emissions(eco_vehicle, yearly_distance)
        
        savings = base_emissions - eco_emissions
        percentage = (savings / base_emissions) * 100 if base_emissions > 0 else 0
        
        return {
            'base_emissions': base_emissions,
            'eco_emissions': eco_emissions,
            'savings': savings,
            'percentage': percentage
        }

class EnvironmentalImpactAnalyzer:
    """Analyze overall environmental impact of eco vehicles."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.air_monitor = AirQualityMonitor()
        self.emissions_calc = EmissionsCalculator()
        
    def analyze_impact(self,
                      metrics: AirQualityMetrics,
                      vehicle_type: str,
                      distance: float) -> Dict[str, float]:
        """
        Analyze environmental impact combining air quality and emissions.
        
        Args:
            metrics: Current air quality metrics
            vehicle_type: Type of vehicle
            distance: Distance traveled in kilometers
            
        Returns:
            Dictionary containing impact analysis results
        """
        # Calculate emissions
        emissions = self.emissions_calc.calculate_emissions(vehicle_type, distance)
        
        # Calculate air quality score (0-1, higher is better)
        air_quality_score = (
            (5000 - metrics.co2_level) / 5000 * 0.3 +  # CO2 weight
            (9 - metrics.co_level) / 9 * 0.3 +         # CO weight
            (0.1 - metrics.nox_level) / 0.1 * 0.2 +    # NOx weight
            (35 - metrics.pm25_level) / 35 * 0.1 +     # PM2.5 weight
            (150 - metrics.pm10_level) / 150 * 0.1     # PM10 weight
        )
        
        # Calculate overall environmental score
        environmental_score = (
            (1000 - emissions) / 1000 * 0.6 +  # Emissions weight
            air_quality_score * 0.4             # Air quality weight
        )
        
        return {
            'emissions': emissions,
            'air_quality_score': air_quality_score,
            'environmental_score': environmental_score,
            'within_limits': metrics.is_within_limits()
        }
