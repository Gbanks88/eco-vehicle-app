"""Tests for the air quality monitoring system."""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

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

def test_safe_limits(safe_metrics):
    """Test metrics within safe limits."""
    assert safe_metrics.is_within_limits()

def test_unsafe_limits(unsafe_metrics):
    """Test metrics exceeding safe limits."""
    assert not unsafe_metrics.is_within_limits()

def test_air_quality_monitor():
    """Test air quality monitor functionality."""
    monitor = AirQualityMonitor()
    metrics = AirQualityMetrics(
        co2_level=1000.0,
        co_level=4.0,
        nox_level=0.05,
        pm25_level=12.0,
        pm10_level=50.0,
        timestamp=datetime.now()
    )
    
    # Test adding measurements
    monitor.add_measurement(metrics)
    assert len(monitor.history) == 1
    assert monitor.history[0] == metrics
    
    # Test average calculation
    avg = monitor.get_average_metrics(window_size=1)
    assert avg is not None
    assert avg.co2_level == metrics.co2_level
    
    # Test alert system
    alerts = []
    monitor.register_alert_callback(lambda m: alerts.append(m))
    
    unsafe = AirQualityMetrics(
        co2_level=6000.0,
        co_level=10.0,
        nox_level=0.15,
        pm25_level=40.0,
        pm10_level=200.0,
        timestamp=datetime.now()
    )
    monitor.add_measurement(unsafe)
    assert len(alerts) == 1

def test_emissions_calculator():
    """Test emissions calculator functionality."""
    calc = EmissionsCalculator()
    
    # Test electric vehicle (should be 0)
    assert calc.calculate_emissions('electric', 100.0) == 0.0
    
    # Test gasoline vehicle
    gasoline_emissions = calc.calculate_emissions('gasoline', 100.0)
    assert gasoline_emissions == 19200.0  # 192 g/km * 100 km
    
    # Test comparison
    comparison = calc.compare_emissions('gasoline', 'electric', 10000.0)
    assert comparison['base_emissions'] == 1920000.0  # Gasoline
    assert comparison['eco_emissions'] == 0.0         # Electric
    assert comparison['savings'] == 1920000.0
    assert comparison['percentage'] == 100.0
    
    # Test invalid vehicle type
    with pytest.raises(ValueError):
        calc.calculate_emissions('invalid_type', 100.0)

def test_environmental_impact():
    """Test environmental impact analyzer."""
    analyzer = EnvironmentalImpactAnalyzer()
    metrics = AirQualityMetrics(
        co2_level=1000.0,
        co_level=4.0,
        nox_level=0.05,
        pm25_level=12.0,
        pm10_level=50.0,
        timestamp=datetime.now()
    )
    
    impact = analyzer.analyze_impact(metrics, 'electric', 100.0)
    
    assert 'emissions' in impact
    assert 'air_quality_score' in impact
    assert 'environmental_score' in impact
    assert 'within_limits' in impact
    
    assert impact['emissions'] == 0.0  # Electric vehicle
    assert 0.0 <= impact['air_quality_score'] <= 1.0
    assert 0.0 <= impact['environmental_score'] <= 1.0
    assert impact['within_limits'] == True
