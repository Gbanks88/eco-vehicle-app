"""Real-time system monitoring for eco vehicles."""

import logging
import threading
import queue
import time
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
from datetime import datetime
import numpy as np

from ..environmental.air_quality import (
    AirQualityMetrics,
    AirQualityMonitor,
    EnvironmentalImpactAnalyzer
)

@dataclass
class SystemMetrics:
    """System-wide performance metrics."""
    cpu_usage: float
    memory_usage: float
    network_latency: float
    sensor_health: Dict[str, bool]
    timestamp: datetime

@dataclass
class VehicleMetrics:
    """Vehicle performance metrics."""
    speed: float  # km/h
    acceleration: float  # m/s²
    battery_level: float  # percentage
    motor_temp: float  # celsius
    tire_pressure: Dict[str, float]  # kPa
    brake_wear: float  # percentage
    timestamp: datetime

class MetricsCollector:
    """Collect and aggregate system metrics."""
    
    def __init__(self, sampling_rate: float = 1.0):
        """Initialize metrics collector.
        
        Args:
            sampling_rate: Samples per second
        """
        self.sampling_rate = sampling_rate
        self.logger = logging.getLogger(__name__)
        self.metrics_queue = queue.Queue()
        self.stop_event = threading.Event()
        self.collector_thread = None
        
    def start(self):
        """Start metrics collection."""
        if self.collector_thread is not None:
            self.logger.warning("Collector already running")
            return
            
        self.stop_event.clear()
        self.collector_thread = threading.Thread(target=self._collect_metrics)
        self.collector_thread.daemon = True
        self.collector_thread.start()
        
    def stop(self):
        """Stop metrics collection."""
        self.stop_event.set()
        if self.collector_thread is not None:
            self.collector_thread.join()
            self.collector_thread = None
            
    def _collect_metrics(self):
        """Continuously collect metrics."""
        while not self.stop_event.is_set():
            try:
                metrics = self._gather_current_metrics()
                self.metrics_queue.put(metrics)
                time.sleep(1.0 / self.sampling_rate)
            except Exception as e:
                self.logger.error(f"Error collecting metrics: {e}")
                
    def _gather_current_metrics(self) -> Dict[str, float]:
        """Gather current system metrics."""
        # This would interface with actual hardware sensors
        # For now, return simulated data
        return {
            'cpu_usage': np.random.uniform(20, 80),
            'memory_usage': np.random.uniform(30, 70),
            'network_latency': np.random.uniform(10, 100),
            'battery_level': np.random.uniform(50, 100)
        }

class AlertManager:
    """Manage system alerts and notifications."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.alert_handlers: Dict[str, List[Callable]] = {}
        self.alert_thresholds: Dict[str, float] = {
            'cpu_usage': 80.0,
            'memory_usage': 90.0,
            'network_latency': 150.0,
            'battery_level': 20.0,
            'motor_temp': 90.0
        }
        
    def register_handler(self, alert_type: str, handler: Callable):
        """Register alert handler."""
        if alert_type not in self.alert_handlers:
            self.alert_handlers[alert_type] = []
        self.alert_handlers[alert_type].append(handler)
        
    def set_threshold(self, metric: str, threshold: float):
        """Set alert threshold for metric."""
        self.alert_thresholds[metric] = threshold
        
    def check_metrics(self, metrics: Dict[str, float]):
        """Check metrics against thresholds."""
        for metric, value in metrics.items():
            if metric in self.alert_thresholds:
                # For battery level, alert when below threshold
                if metric == 'battery_level':
                    if value < self.alert_thresholds[metric]:
                        self._trigger_alert(metric, value)
                # For other metrics, alert when above threshold
                else:
                    if value > self.alert_thresholds[metric]:
                        self._trigger_alert(metric, value)
                    
    def _trigger_alert(self, metric: str, value: float):
        """Trigger alert handlers."""
        if metric in self.alert_handlers:
            for handler in self.alert_handlers[metric]:
                try:
                    handler(metric, value)
                except Exception as e:
                    self.logger.error(f"Error in alert handler: {e}")

class PerformanceAnalyzer:
    """Analyze system performance metrics."""
    
    def __init__(self, window_size: int = 100):
        self.window_size = window_size
        self.metrics_history: Dict[str, List[float]] = {}
        self.logger = logging.getLogger(__name__)
        
    def add_metrics(self, metrics: Dict[str, float]):
        """Add metrics to history."""
        for metric, value in metrics.items():
            if metric not in self.metrics_history:
                self.metrics_history[metric] = []
            self.metrics_history[metric].append(value)
            if len(self.metrics_history[metric]) > self.window_size:
                self.metrics_history[metric].pop(0)
                
    def get_statistics(self, metric: str) -> Dict[str, float]:
        """Get statistics for metric."""
        if metric not in self.metrics_history:
            return {}
            
        values = np.array(self.metrics_history[metric])
        return {
            'mean': np.mean(values),
            'std': np.std(values),
            'min': np.min(values),
            'max': np.max(values),
            'median': np.median(values)
        }
        
    def detect_anomalies(self, metric: str, threshold: float = 2.0) -> List[float]:
        """Detect anomalies using z-score."""
        if metric not in self.metrics_history:
            return []
            
        values = np.array(self.metrics_history[metric])
        z_scores = np.abs((values - np.mean(values)) / np.std(values))
        return values[z_scores > threshold].tolist()

class SystemMonitor:
    """Main system monitoring class."""
    
    def __init__(self, sampling_rate: float = 1.0):
        self.collector = MetricsCollector(sampling_rate)
        self.alert_manager = AlertManager()
        self.analyzer = PerformanceAnalyzer()
        self.env_monitor = AirQualityMonitor()
        self.env_analyzer = EnvironmentalImpactAnalyzer()
        self.logger = logging.getLogger(__name__)
        
        # Register default alert handlers
        self.alert_manager.register_handler('cpu_usage', self._handle_high_cpu)
        self.alert_manager.register_handler('memory_usage', self._handle_high_memory)
        self.alert_manager.register_handler('battery_level', self._handle_low_battery)
        
    def start_monitoring(self):
        """Start system monitoring."""
        self.collector.start()
        self.logger.info("System monitoring started")
        
        # Start processing metrics
        threading.Thread(target=self._process_metrics, daemon=True).start()
        
    def stop_monitoring(self):
        """Stop system monitoring."""
        self.collector.stop()
        self.logger.info("System monitoring stopped")
        
    def _process_metrics(self):
        """Process collected metrics."""
        while True:
            try:
                metrics = self.collector.metrics_queue.get(timeout=1.0)
                
                # Check for alerts
                self.alert_manager.check_metrics(metrics)
                
                # Update performance analysis
                self.analyzer.add_metrics(metrics)
                
                # Log significant anomalies
                for metric in metrics:
                    anomalies = self.analyzer.detect_anomalies(metric)
                    if anomalies:
                        self.logger.warning(f"Anomalies detected in {metric}: {anomalies}")
                        
            except queue.Empty:
                continue
            except Exception as e:
                self.logger.error(f"Error processing metrics: {e}")
                
    def _handle_high_cpu(self, metric: str, value: float):
        """Handle high CPU usage alert."""
        self.logger.warning(f"High CPU usage detected: {value}%")
        
    def _handle_high_memory(self, metric: str, value: float):
        """Handle high memory usage alert."""
        self.logger.warning(f"High memory usage detected: {value}%")
        
    def _handle_low_battery(self, metric: str, value: float):
        """Handle low battery alert."""
        self.logger.warning(f"Low battery level detected: {value}%")
        
    def get_system_health(self) -> Dict[str, Dict[str, float]]:
        """Get overall system health metrics."""
        health_metrics = {}
        
        # Get performance metrics
        for metric in ['cpu_usage', 'memory_usage', 'network_latency', 'battery_level']:
            health_metrics[metric] = self.analyzer.get_statistics(metric)
            
        return health_metrics
