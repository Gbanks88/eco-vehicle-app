#!/usr/bin/env python3
"""Test script for power mode transitions."""

import json
import time
from pathlib import Path
import logging
from src.monitoring.system_monitor import SystemMonitor

def setup_logging():
    """Setup logging configuration."""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / "power_test.log"),
            logging.StreamHandler()
        ]
    )

def main():
    """Demonstrate power mode transitions."""
    setup_logging()
    logger = logging.getLogger(__name__)
    monitor = SystemMonitor()
    
    # Start from STANDBY
    logger.info("Initial state: STANDBY")
    monitor.update_state({"power_state": "STANDBY"})
    time.sleep(2)
    
    # Power on sequence
    logger.info("Initiating power-on sequence")
    monitor.update_state({"power_state": "POWER_ON"})
    time.sleep(2)
    
    # Test different power modes
    power_modes = [
        ("NORMAL_POWER", {"voltage": 48.2, "current": 12.5}),
        ("ECO_POWER", {"voltage": 42.0, "current": 8.5}),
        ("HIGH_POWER", {"voltage": 52.0, "current": 18.0})
    ]
    
    for mode, params in power_modes:
        logger.info(f"Switching to {mode}")
        monitor.update_state({"power_mode": mode, "parameters": params})
        metrics = monitor.get_power_metrics()
        logger.info(f"Power metrics: {json.dumps(metrics, indent=2)}")
        time.sleep(2)
    
    # Test charging sequence
    logger.info("Initiating charging sequence")
    monitor.update_state({"power_state": "CHARGING"})
    charging_modes = [
        ("SLOW_CHARGING", {"input_current": 16, "target_voltage": 48.0}),
        ("FAST_CHARGING", {"input_current": 32, "target_voltage": 50.0})
    ]
    
    for mode, params in charging_modes:
        logger.info(f"Switching to {mode}")
        monitor.update_state({"charging_mode": mode, "parameters": params})
        metrics = monitor.get_charging_metrics()
        logger.info(f"Charging metrics: {json.dumps(metrics, indent=2)}")
        time.sleep(2)
    
    # Test fault handling
    logger.info("Testing fault handling")
    monitor.update_state({"fault": {"type": "THERMAL_WARNING", "severity": "MINOR"}})
    time.sleep(2)
    
    # Return to standby
    logger.info("Returning to standby")
    monitor.update_state({"power_state": "STANDBY"})

if __name__ == "__main__":
    main()
