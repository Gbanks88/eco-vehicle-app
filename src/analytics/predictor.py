#!/usr/bin/env python3
"""AI-powered analytics for eco-vehicle optimization."""

import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import joblib
import logging
from pathlib import Path
import json
from datetime import datetime, timedelta
from typing import Dict, List, Tuple

class VehiclePredictor:
    """Predictive analytics for vehicle optimization."""
    
    def __init__(self, config_path: str = None, model_type: str = 'random_forest'):
        self.logger = logging.getLogger(__name__)
        self.config = self._load_config(config_path)
        self.scaler = StandardScaler()
        self.model_type = model_type
        self.model = self._create_model()
        self.features = [
            'voltage', 'current', 'temperature',
            'speed', 'acceleration', 'terrain_grade'
        ]
        
    def _create_model(self) -> object:
        """Create ML model based on type."""
        if self.model_type == 'random_forest':
            return RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                random_state=42
            )
        elif self.model_type == 'gradient_boost':
            return GradientBoostingRegressor(
                n_estimators=100,
                max_depth=5,
                learning_rate=0.1,
                random_state=42
            )
        elif self.model_type == 'neural_net':
            return MLPRegressor(
                hidden_layer_sizes=(100, 50),
                activation='relu',
                solver='adam',
                random_state=42
            )
        else:
            raise ValueError(f"Unknown model type: {self.model_type}")
    
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from file."""
        default_config = {
            'update_interval': 300,  # 5 minutes
            'prediction_horizon': 3600,  # 1 hour
            'min_samples': 1000,
            'model_path': 'models/vehicle_predictor.joblib'
        }
        
        if config_path and Path(config_path).exists():
            with open(config_path) as f:
                config = json.load(f)
            return {**default_config, **config}
        return default_config
    
    def preprocess_data(self, data: List[Dict]) -> Tuple[np.ndarray, np.ndarray]:
        """Preprocess raw data for model training."""
        X = np.array([[d[f] for f in self.features] for d in data])
        y = np.array([d['efficiency'] for d in data])
        
        X_scaled = self.scaler.fit_transform(X)
        return X_scaled, y
    
    def train(self, training_data: List[Dict]) -> None:
        """Train the prediction model."""
        if len(training_data) < self.config['min_samples']:
            self.logger.warning(
                f"Insufficient training data: {len(training_data)} < "
                f"{self.config['min_samples']}"
            )
            return
        
        X, y = self.preprocess_data(training_data)
        self.model.fit(X, y)
        
        # Save the model
        model_path = Path(self.config['model_path'])
        model_path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump((self.model, self.scaler), model_path)
        self.logger.info(f"Model saved to {model_path}")
    
    def predict_efficiency(self, current_state: Dict) -> Dict:
        """Predict future efficiency based on current state."""
        features = np.array([[
            current_state[f] for f in self.features
        ]])
        features_scaled = self.scaler.transform(features)
        
        prediction = self.model.predict(features_scaled)[0]
        confidence = self.model.predict_proba(features_scaled)[0] if hasattr(self.model, 'predict_proba') else None
        
        return {
            'predicted_efficiency': float(prediction),
            'confidence': float(confidence) if confidence is not None else None,
            'timestamp': datetime.now().isoformat()
        }
    
    def optimize_parameters(self, current_state: Dict) -> Dict:
        """Optimize vehicle parameters for maximum efficiency."""
        # Create parameter grid
        voltage_range = np.linspace(
            current_state['voltage'] - 2,
            current_state['voltage'] + 2,
            10
        )
        current_range = np.linspace(
            current_state['current'] - 1,
            current_state['current'] + 1,
            10
        )
        
        best_efficiency = float('-inf')
        optimal_params = None
        
        # Grid search for optimal parameters
        for voltage in voltage_range:
            for current in current_range:
                test_state = current_state.copy()
                test_state.update({
                    'voltage': voltage,
                    'current': current
                })
                
                prediction = self.predict_efficiency(test_state)
                if prediction['predicted_efficiency'] > best_efficiency:
                    best_efficiency = prediction['predicted_efficiency']
                    optimal_params = {
                        'voltage': voltage,
                        'current': current,
                        'predicted_efficiency': best_efficiency
                    }
        
        return optimal_params
    
    def analyze_patterns(self, historical_data: List[Dict]) -> Dict:
        """Analyze patterns in historical data."""
        if not historical_data:
            return {}
        
        # Calculate time-based patterns
        hourly_efficiencies = {}
        for entry in historical_data:
            timestamp = datetime.fromisoformat(entry['timestamp'])
            hour = timestamp.hour
            
            if hour not in hourly_efficiencies:
                hourly_efficiencies[hour] = []
            hourly_efficiencies[hour].append(entry['efficiency'])
        
        # Calculate average efficiency by hour
        hourly_averages = {
            hour: sum(effs) / len(effs)
            for hour, effs in hourly_efficiencies.items()
        }
        
        # Find optimal operating hours
        optimal_hours = sorted(
            hourly_averages.items(),
            key=lambda x: x[1],
            reverse=True
        )[:3]
        
        return {
            'optimal_hours': optimal_hours,
            'hourly_averages': hourly_averages,
            'analysis_timestamp': datetime.now().isoformat()
        }

class RealTimeOptimizer:
    """Real-time optimization of vehicle parameters."""
    
    def __init__(self, predictor: VehiclePredictor):
        self.predictor = predictor
        self.logger = logging.getLogger(__name__)
        self.current_state = {}
        self.optimization_history = []
    
    def update_state(self, new_state: Dict) -> None:
        """Update current vehicle state."""
        self.current_state = new_state
        self.optimization_history.append({
            'timestamp': datetime.now().isoformat(),
            'state': new_state
        })
        
        # Keep only last 24 hours of history
        cutoff_time = datetime.now() - timedelta(hours=24)
        self.optimization_history = [
            entry for entry in self.optimization_history
            if datetime.fromisoformat(entry['timestamp']) > cutoff_time
        ]
    
    def get_optimization_advice(self) -> Dict:
        """Get real-time optimization advice."""
        if not self.current_state:
            return {}
        
        # Get predictions and optimal parameters
        prediction = self.predictor.predict_efficiency(self.current_state)
        optimal_params = self.predictor.optimize_parameters(self.current_state)
        
        # Analyze historical patterns
        patterns = self.predictor.analyze_patterns(self.optimization_history)
        
        return {
            'current_efficiency': self.current_state.get('efficiency'),
            'predicted_efficiency': prediction['predicted_efficiency'],
            'optimal_parameters': optimal_params,
            'patterns': patterns,
            'recommendations': self._generate_recommendations(
                self.current_state,
                optimal_params,
                patterns
            )
        }
    
    def _generate_recommendations(
        self,
        current_state: Dict,
        optimal_params: Dict,
        patterns: Dict
    ) -> List[Dict]:
        """Generate specific recommendations based on analysis."""
        recommendations = []
        
        # Check if current efficiency can be improved
        if optimal_params['predicted_efficiency'] > current_state['efficiency']:
            recommendations.append({
                'type': 'parameter_adjustment',
                'priority': 'high',
                'message': 'Adjust power parameters for optimal efficiency',
                'actions': {
                    'voltage': optimal_params['voltage'],
                    'current': optimal_params['current']
                }
            })
        
        # Add timing-based recommendations
        if patterns.get('optimal_hours'):
            recommendations.append({
                'type': 'timing_optimization',
                'priority': 'medium',
                'message': 'Consider optimal operating hours',
                'optimal_hours': patterns['optimal_hours']
            })
        
        return recommendations
