#!/usr/bin/env python3
"""Test script for power management API."""

import requests
import json
import time
import logging
from pathlib import Path

def setup_logging():
    """Setup logging configuration."""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / "api_test.log"),
            logging.StreamHandler()
        ]
    )

def call_api(endpoint, method='GET', data=None):
    """Make API call to the dashboard."""
    url = f'http://localhost:8080/api/{endpoint}'
    headers = {'Content-Type': 'application/json'}
    
    try:
        if method == 'GET':
            response = requests.get(url, headers=headers)
        else:
            response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"API call failed: {e}")
        return None

def main():
    """Test power management API endpoints."""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    # Test power state transitions
    states = [
        ("power/state", {"state": "STANDBY"}),
        ("power/state", {"state": "POWER_ON"}),
        ("power/mode", {"mode": "NORMAL_POWER", "params": {"voltage": 48.2, "current": 12.5}}),
        ("power/mode", {"mode": "ECO_POWER", "params": {"voltage": 42.0, "current": 8.5}}),
        ("charging/mode", {"mode": "SLOW_CHARGING", "params": {"input_current": 16}}),
        ("charging/mode", {"mode": "FAST_CHARGING", "params": {"input_current": 32}})
    ]
    
    for endpoint, data in states:
        logger.info(f"Setting {endpoint}: {json.dumps(data, indent=2)}")
        response = call_api(endpoint, method='POST', data=data)
        logger.info(f"Response: {json.dumps(response, indent=2) if response else 'Failed'}")
        
        # Get current status
        status = call_api("system/status")
        logger.info(f"System status: {json.dumps(status, indent=2) if status else 'Failed'}")
        time.sleep(2)
    
    # Monitor environmental metrics
    metrics = call_api("metrics/environmental")
    logger.info(f"Environmental metrics: {json.dumps(metrics, indent=2) if metrics else 'Failed'}")

if __name__ == "__main__":
    main()
