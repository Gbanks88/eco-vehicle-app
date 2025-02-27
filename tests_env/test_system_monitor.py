"""Tests for the system monitoring module."""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
import time
import numpy as np
from datetime import datetime
from src.monitoring.system_monitor import (
    SystemMetrics,
    VehicleMetrics,
    MetricsCollector,
    AlertManager,
    PerformanceAnalyzer,
    SystemMonitor
)

@pytest.fixture
def metrics_collector():
    """Create metrics collector instance."""
    collector = MetricsCollector(sampling_rate=10.0)  # 10 Hz for faster tests
    return collector

@pytest.fixture
def alert_manager():
    """Create alert manager instance."""
    return AlertManager()

@pytest.fixture
def performance_analyzer():
    """Create performance analyzer instance."""
    return PerformanceAnalyzer(window_size=10)

@pytest.fixture
def system_monitor():
    """Create system monitor instance."""
    return SystemMonitor(sampling_rate=10.0)

def test_metrics_collector(metrics_collector):
    """Test metrics collection."""
    metrics_collector.start()
    time.sleep(0.5)  # Collect some metrics
    
    # Check if metrics are being collected
    assert not metrics_collector.metrics_queue.empty()
    
    # Get a metric sample
    metrics = metrics_collector.metrics_queue.get()
    assert isinstance(metrics, dict)
    assert 'cpu_usage' in metrics
    assert 'memory_usage' in metrics
    
    metrics_collector.stop()
    assert metrics_collector.collector_thread is None

def test_alert_manager(alert_manager):
    """Test alert management."""
    alerts_received = []
    
    def alert_handler(metric, value):
        alerts_received.append((metric, value))
    
    # Register handler and set threshold
    alert_manager.register_handler('cpu_usage', alert_handler)
    alert_manager.set_threshold('cpu_usage', 75.0)
    
    # Test alert triggering
    metrics = {'cpu_usage': 80.0}
    alert_manager.check_metrics(metrics)
    assert len(alerts_received) == 1
    assert alerts_received[0][0] == 'cpu_usage'
    assert alerts_received[0][1] == 80.0
    
    # Test no alert for normal values
    metrics = {'cpu_usage': 50.0}
    alert_manager.check_metrics(metrics)
    assert len(alerts_received) == 1  # No new alerts

def test_performance_analyzer(performance_analyzer):
    """Test performance analysis."""
    # Add test metrics
    test_metrics = {
        'cpu_usage': [50.0] * 10  # Create baseline
    }
    
    for value in test_metrics['cpu_usage']:
        performance_analyzer.add_metrics({'cpu_usage': value})
    
    # Test statistics
    stats = performance_analyzer.get_statistics('cpu_usage')
    assert stats['mean'] == pytest.approx(50.0)
    assert stats['min'] == 50.0
    assert stats['max'] == 50.0
    
    # Test anomaly detection
    performance_analyzer.add_metrics({'cpu_usage': 150.0})  # Clear anomaly
    anomalies = performance_analyzer.detect_anomalies('cpu_usage', threshold=2.0)
    assert len(anomalies) > 0
    assert 150.0 in anomalies

def test_system_monitor(system_monitor):
    """Test complete system monitoring."""
    # Start monitoring
    system_monitor.start_monitoring()
    time.sleep(1.0)  # Let it collect some data
    
    # Check system health
    health = system_monitor.get_system_health()
    assert isinstance(health, dict)
    assert 'cpu_usage' in health
    assert 'memory_usage' in health
    
    # Test alert handling
    alerts = []
    def test_alert_handler(metric, value):
        alerts.append((metric, value))
    
    system_monitor.alert_manager.register_handler('test_metric', test_alert_handler)
    system_monitor.alert_manager.set_threshold('test_metric', 50.0)
    system_monitor.alert_manager.check_metrics({'test_metric': 75.0})
    
    assert len(alerts) == 1
    assert alerts[0][0] == 'test_metric'
    assert alerts[0][1] == 75.0
    
    # Stop monitoring
    system_monitor.stop_monitoring()

def test_metrics_integration():
    """Test integration between components."""
    monitor = SystemMonitor(sampling_rate=10.0)
    
    # Register test alert handler
    alerts = []
    def test_handler(metric, value):
        alerts.append((metric, value))
    
    monitor.alert_manager.register_handler('cpu_usage', test_handler)
    monitor.alert_manager.set_threshold('cpu_usage', 75.0)
    
    # Start monitoring
    monitor.start_monitoring()
    time.sleep(1.0)  # Collect data
    
    # Check if metrics are flowing through the system
    health = monitor.get_system_health()
    assert isinstance(health, dict)
    assert len(health) > 0
    
    # Verify that statistics are being calculated
    cpu_stats = health.get('cpu_usage', {})
    assert len(cpu_stats) > 0
    assert 'mean' in cpu_stats
    assert 'std' in cpu_stats
    
    # Stop monitoring
    monitor.stop_monitoring()
