#!/usr/bin/env python3
"""Application Builder for Eco-Vehicle System."""

import os
import json
import logging
import argparse
import subprocess
from pathlib import Path
from typing import Dict, List, Optional

class EcoVehicleBuilder:
    """Builder for Eco-Vehicle system components."""
    
    def __init__(self):
        self.logger = self._setup_logging()
        self.config = self._load_default_config()
        self.components = {
            'dashboard': self._build_dashboard,
            'viewer': self._build_viewer,
            'monitor': self._build_monitor,
            'power': self._build_power_system,
            'analytics': self._build_analytics,
            'all': self._build_all
        }
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        return logging.getLogger('EcoVehicleBuilder')
    
    def _load_default_config(self) -> Dict:
        """Load default configuration."""
        return {
            'dashboard': {
                'port': 5000,
                'debug': True
            },
            'viewer': {
                'port': 8081,
                'models_dir': 'static/models'
            },
            'monitor': {
                'update_interval': 1.0,
                'log_dir': 'logs'
            },
            'power': {
                'default_state': 'STANDBY',
                'voltage_range': [42.0, 52.0],
                'current_range': [0, 100]
            }
        }
    
    def _ensure_directory(self, path: str) -> None:
        """Ensure directory exists."""
        Path(path).mkdir(parents=True, exist_ok=True)
    
    def _install_requirements(self, requirements: List[str]) -> None:
        """Install Python requirements."""
        self.logger.info(f"Installing requirements: {requirements}")
        try:
            subprocess.run([
                'pip', 'install', *requirements
            ], check=True)
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to install requirements: {e}")
            raise
    
    def _build_dashboard(self) -> None:
        """Build dashboard component."""
        self.logger.info("Building dashboard component...")
        
        # Create necessary directories
        self._ensure_directory('src/dashboard/static')
        self._ensure_directory('src/dashboard/templates')
        
        # Install requirements
        self._install_requirements(['flask', 'flask-socketio'])
        
        # Create dashboard configuration
        config = {
            'port': self.config['dashboard']['port'],
            'debug': self.config['dashboard']['debug']
        }
        
        with open('src/dashboard/config.json', 'w') as f:
            json.dump(config, f, indent=2)
        
        self.logger.info("Dashboard component built successfully")
    
    def _build_viewer(self) -> None:
        """Build CAD viewer component."""
        self.logger.info("Building viewer component...")
        
        # Create necessary directories
        viewer_dir = Path('src/viewer')
        self._ensure_directory(viewer_dir / 'static/models')
        self._ensure_directory(viewer_dir / 'static/js')
        self._ensure_directory(viewer_dir / 'static/css')
        
        # Copy static files if they exist
        if (viewer_dir / 'static/index.html').exists():
            self.logger.info("Using existing viewer files")
        else:
            self.logger.info("Creating new viewer files")
            # Create default files here
        
        self.logger.info("Viewer component built successfully")
    
    def _build_monitor(self) -> None:
        """Build system monitor component."""
        self.logger.info("Building monitor component...")
        
        # Create necessary directories
        self._ensure_directory('src/monitoring')
        self._ensure_directory('logs')
        
        # Create monitor configuration
        config = {
            'update_interval': self.config['monitor']['update_interval'],
            'log_dir': self.config['monitor']['log_dir']
        }
        
        with open('src/monitoring/config.json', 'w') as f:
            json.dump(config, f, indent=2)
        
        self.logger.info("Monitor component built successfully")
    
    def _build_power_system(self) -> None:
        """Build power management system component."""
        self.logger.info("Building power system component...")
        
        # Create necessary directories
        self._ensure_directory('src/power')
        
        # Create power system configuration
        config = {
            'default_state': self.config['power']['default_state'],
            'voltage_range': self.config['power']['voltage_range'],
            'current_range': self.config['power']['current_range']
        }
        
        with open('src/power/config.json', 'w') as f:
            json.dump(config, f, indent=2)
        
        self.logger.info("Power system component built successfully")
    
    def _build_analytics(self) -> None:
        """Build analytics component."""
        self.logger.info("Building analytics component...")
        
        # Create necessary directories
        self._ensure_directory('src/analytics')
        self._ensure_directory('src/analytics/models')
        self._ensure_directory('src/analytics/data')
        
        # Install requirements
        self._install_requirements([
            'scikit-learn',
            'numpy',
            'pandas',
            'joblib'
        ])
        
        # Create analytics configuration
        config = {
            'update_interval': 300,  # 5 minutes
            'prediction_horizon': 3600,  # 1 hour
            'min_samples': 1000,
            'model_path': 'models/vehicle_predictor.joblib',
            'features': [
                'voltage',
                'current',
                'temperature',
                'speed',
                'acceleration',
                'terrain_grade'
            ]
        }
        
        with open('src/analytics/config.json', 'w') as f:
            json.dump(config, f, indent=2)
        
        self.logger.info("Analytics component built successfully")
    
    def _build_all(self) -> None:
        """Build all components."""
        self.logger.info("Building all components...")
        self._build_dashboard()
        self._build_viewer()
        self._build_monitor()
        self._build_power_system()
        self._build_analytics()
        self.logger.info("All components built successfully")
    
    def build(self, component: str, config: Optional[Dict] = None) -> None:
        """Build specified component with optional configuration."""
        if config:
            self.config.update(config)
        
        if component not in self.components:
            raise ValueError(f"Unknown component: {component}")
        
        self.components[component]()
    
    def run(self, component: str) -> None:
        """Run specified component."""
        self.logger.info(f"Running {component}...")
        
        if component == 'dashboard':
            subprocess.Popen(['python', '-m', 'src.dashboard.server'])
        elif component == 'viewer':
            subprocess.Popen(['python', '-m', 'src.viewer.server'])
        elif component == 'monitor':
            subprocess.Popen(['python', '-m', 'src.monitoring.monitor'])
        elif component == 'analytics':
            # Start predictor
            subprocess.Popen(['python', '-m', 'src.analytics.predictor'])
            # Start analytics dashboard
            subprocess.Popen(['python', '-m', 'src.analytics.dashboard'])
            # Start UI designer
            subprocess.Popen(['python', '-m', 'src.analytics.ui_designer'])
        elif component == 'all':
            self.run('dashboard')
            self.run('viewer')
            self.run('monitor')
            self.run('analytics')
        else:
            raise ValueError(f"Unknown component: {component}")

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Eco-Vehicle Application Builder')
    parser.add_argument('action', choices=['build', 'run'], help='Action to perform')
    parser.add_argument('component', choices=['dashboard', 'viewer', 'monitor', 'power', 'all'],
                      help='Component to build/run')
    parser.add_argument('--config', type=str, help='Path to configuration file')
    
    args = parser.parse_args()
    
    builder = EcoVehicleBuilder()
    
    config = None
    if args.config:
        with open(args.config) as f:
            config = json.load(f)
    
    if args.action == 'build':
        builder.build(args.component, config)
    else:
        builder.run(args.component)

if __name__ == '__main__':
    main()
