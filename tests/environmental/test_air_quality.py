"""Tests for the air quality monitoring system."""

import pytest
from datetime import datetime
from src.environmental.air_quality import (
    AirQualityMetrics,
    AirQualityMonitor,
    EmissionsCalculator,
    EnvironmentalImpactAnalyzer
)

@pytest.fixture
def safe_metrics():
    """Create air quality metrics within safe limits."""
    return AirQualityMetrics(
        co2_level=1000.0,  # Safe: < 5000
        co_level=4.0,      # Safe: < 9
        nox_level=0.05,    # Safe: < 0.1
        pm25_level=12.0,   # Safe: < 35
        pm10_level=50.0,   # Safe: < 150
        timestamp=datetime.now()
    )

@pytest.fixture
def unsafe_metrics():
    """Create air quality metrics exceeding safe limits."""
    return AirQualityMetrics(
        co2_level=6000.0,  # Unsafe: > 5000
        co_level=10.0,     # Unsafe: > 9
        nox_level=0.15,    # Unsafe: > 0.1
        pm25_level=40.0,   # Unsafe: > 35
        pm10_level=200.0,  # Unsafe: > 150
        timestamp=datetime.now()
    )

class TestAirQualityMetrics:
    """Test suite for AirQualityMetrics."""
    
    def test_safe_limits(self, safe_metrics):
        """Test metrics within safe limits."""
        assert safe_metrics.is_within_limits()
    
    def test_unsafe_limits(self, unsafe_metrics):
        """Test metrics exceeding safe limits."""
        assert not unsafe_metrics.is_within_limits()

class TestAirQualityMonitor:
    """Test suite for AirQualityMonitor."""
    
    @pytest.fixture
    def monitor(self):
        """Create air quality monitor instance."""
        return AirQualityMonitor()
    
    def test_add_measurement(self, monitor, safe_metrics):
        """Test adding measurements."""
        monitor.add_measurement(safe_metrics)
        assert len(monitor.history) == 1
        assert monitor.history[0] == safe_metrics
    
    def test_average_metrics(self, monitor, safe_metrics):
        """Test calculating average metrics."""
        for _ in range(5):
            monitor.add_measurement(safe_metrics)
        
        avg = monitor.get_average_metrics(window_size=5)
        assert avg is not None
        assert avg.co2_level == safe_metrics.co2_level
        assert avg.co_level == safe_metrics.co_level
    
    def test_alert_callback(self, monitor, unsafe_metrics):
        """Test alert callback system."""
        alerts = []
        monitor.register_alert_callback(lambda m: alerts.append(m))
        
        monitor.add_measurement(unsafe_metrics)
        assert len(alerts) == 1
        assert alerts[0] == unsafe_metrics

class TestEmissionsCalculator:
    """Test suite for EmissionsCalculator."""
    
    @pytest.fixture
    def calculator(self):
        """Create emissions calculator instance."""
        return EmissionsCalculator()
    
    def test_calculate_emissions(self, calculator):
        """Test emissions calculation."""
        # Test electric vehicle (should be 0)
        assert calculator.calculate_emissions('electric', 100.0) == 0.0
        
        # Test gasoline vehicle
        gasoline_emissions = calculator.calculate_emissions('gasoline', 100.0)
        assert gasoline_emissions == 19200.0  # 192 g/km * 100 km
    
    def test_compare_emissions(self, calculator):
        """Test emissions comparison."""
        comparison = calculator.compare_emissions('gasoline', 'electric', 10000.0)
        
        assert comparison['base_emissions'] == 1920000.0  # Gasoline
        assert comparison['eco_emissions'] == 0.0         # Electric
        assert comparison['savings'] == 1920000.0
        assert comparison['percentage'] == 100.0
    
    def test_invalid_vehicle_type(self, calculator):
        """Test handling of invalid vehicle types."""
        with pytest.raises(ValueError):
            calculator.calculate_emissions('invalid_type', 100.0)

class TestEnvironmentalImpactAnalyzer:
    """Test suite for EnvironmentalImpactAnalyzer."""
    
    @pytest.fixture
    def analyzer(self):
        """Create environmental impact analyzer instance."""
        return EnvironmentalImpactAnalyzer()
    
    def test_analyze_impact(self, analyzer, safe_metrics):
        """Test impact analysis."""
        impact = analyzer.analyze_impact(safe_metrics, 'electric', 100.0)
        
        assert 'emissions' in impact
        assert 'air_quality_score' in impact
        assert 'environmental_score' in impact
        assert 'within_limits' in impact
        
        assert impact['emissions'] == 0.0  # Electric vehicle
        assert 0.0 <= impact['air_quality_score'] <= 1.0
        assert 0.0 <= impact['environmental_score'] <= 1.0
        assert impact['within_limits'] == True
