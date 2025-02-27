"""Tests for the monitoring visualization components."""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from datetime import datetime, timedelta
from src.monitoring.visualization import MonitoringDashboard

@pytest.fixture
def dashboard():
    """Create dashboard instance."""
    return MonitoringDashboard()

@pytest.fixture
def sample_metrics():
    """Create sample metrics data."""
    return {
        'cpu_usage': 45.0,
        'memory_usage': 60.0,
        'network_latency': 25.0,
        'battery_level': 85.0,
        'environmental_score': 0.75
    }

def test_metrics_update(dashboard, sample_metrics):
    """Test metrics history update."""
    dashboard.update_metrics(sample_metrics)
    
    # Check if metrics were added
    for metric in sample_metrics:
        assert metric in dashboard.metrics_history
        assert len(dashboard.metrics_history[metric]) == 1
        _, value = dashboard.metrics_history[metric][0]
        assert value == sample_metrics[metric]

def test_alert_management(dashboard):
    """Test alert management."""
    # Add test alerts
    dashboard.add_alert('cpu_high', 'CPU usage exceeded threshold', 'warning')
    dashboard.add_alert('memory_high', 'Memory usage exceeded threshold', 'danger')
    
    assert len(dashboard.alert_history) == 2
    assert dashboard.alert_history[0]['type'] == 'cpu_high'
    assert dashboard.alert_history[1]['type'] == 'memory_high'

def test_system_overview(dashboard, sample_metrics):
    """Test system overview visualization."""
    # Add some historical data
    for i in range(10):
        timestamp = datetime.now() - timedelta(minutes=i)
        dashboard.update_metrics(sample_metrics, timestamp)
    
    overview = dashboard.create_system_overview()
    assert isinstance(overview, dict)
    assert 'data' in overview
    assert 'layout' in overview

def test_performance_trends(dashboard, sample_metrics):
    """Test performance trends visualization."""
    # Add some historical data
    for i in range(10):
        timestamp = datetime.now() - timedelta(minutes=i)
        dashboard.update_metrics(sample_metrics, timestamp)
    
    trends = dashboard.create_performance_trends()
    assert isinstance(trends, dict)
    assert 'data' in trends
    assert 'layout' in trends

def test_environmental_dashboard(dashboard, sample_metrics):
    """Test environmental dashboard visualization."""
    # Add some historical data
    for i in range(10):
        timestamp = datetime.now() - timedelta(minutes=i)
        dashboard.update_metrics(sample_metrics, timestamp)
    
    env_dashboard = dashboard.create_environmental_dashboard()
    assert isinstance(env_dashboard, dict)
    assert 'data' in env_dashboard
    assert 'layout' in env_dashboard

def test_history_limit(dashboard, sample_metrics):
    """Test metrics history size limit."""
    # Add more than max_history_points
    for i in range(dashboard.max_history_points + 10):
        timestamp = datetime.now() - timedelta(minutes=i)
        dashboard.update_metrics(sample_metrics, timestamp)
    
    for metric in sample_metrics:
        assert len(dashboard.metrics_history[metric]) <= dashboard.max_history_points
