"""
Unit tests for Digital Twin module
"""

import pytest
from datetime import datetime
from src.model_based.digital_twin.digital_twin import DigitalTwin, VehicleState

@pytest.fixture
def sample_config():
    return {
        'autocad_path': '/path/to/autocad',
        'fusion360_credentials': {
            'api_key': 'test_key',
            'api_secret': 'test_secret'
        }
    }

@pytest.fixture
def sample_telemetry():
    return {
        'position': {'x': 0.0, 'y': 0.0, 'z': 0.0},
        'velocity': {'x': 1.0, 'y': 0.0, 'z': 0.0},
        'acceleration': {'x': 0.0, 'y': 0.0, 'z': 0.0},
        'system_states': {'engine': 'running', 'battery': 'charging'},
        'sensor_readings': {'temperature': 25.0, 'pressure': 1.0},
        'component_health': {'engine': 0.95, 'battery': 0.88}
    }

def test_digital_twin_initialization(sample_config):
    """Test digital twin initialization"""
    twin = DigitalTwin('test_vehicle', sample_config)
    assert twin.vehicle_id == 'test_vehicle'
    assert twin.config == sample_config
    assert twin.current_state is None
    assert len(twin.history) == 0

def test_state_update(sample_config, sample_telemetry):
    """Test state update functionality"""
    twin = DigitalTwin('test_vehicle', sample_config)
    success = twin.update_state(sample_telemetry)
    
    assert success
    assert twin.current_state is not None
    assert len(twin.history) == 1
    
    state = twin.current_state
    assert isinstance(state, VehicleState)
    assert state.position == sample_telemetry['position']
    assert state.velocity == sample_telemetry['velocity']

def test_maintenance_prediction(sample_config, sample_telemetry):
    """Test maintenance prediction functionality"""
    twin = DigitalTwin('test_vehicle', sample_config)
    twin.update_state(sample_telemetry)
    
    predictions = twin.predict_maintenance()
    assert isinstance(predictions, dict)
    assert 'error' not in predictions

def test_simulation(sample_config, sample_telemetry):
    """Test simulation functionality"""
    twin = DigitalTwin('test_vehicle', sample_config)
    twin.update_state(sample_telemetry)
    
    scenario = {
        'duration': 3600,  # 1 hour simulation
        'environment': {'temperature': 25.0, 'humidity': 0.5},
        'events': []
    }
    
    results = twin.run_simulation(scenario)
    assert isinstance(results, dict)
    assert 'error' not in results

def test_performance_metrics(sample_config, sample_telemetry):
    """Test performance metrics calculation"""
    twin = DigitalTwin('test_vehicle', sample_config)
    twin.update_state(sample_telemetry)
    
    metrics = twin.get_performance_metrics()
    assert isinstance(metrics, dict)
    assert 'efficiency' in metrics
    assert 'reliability' in metrics
    assert 'performance_score' in metrics

def test_invalid_state_transition(sample_config):
    """Test invalid state transition handling"""
    twin = DigitalTwin('test_vehicle', sample_config)
    
    invalid_telemetry = {
        'position': {'x': float('inf'), 'y': 0.0, 'z': 0.0},  # Invalid position
        'velocity': {'x': 1.0, 'y': 0.0, 'z': 0.0},
        'acceleration': {'x': 0.0, 'y': 0.0, 'z': 0.0},
        'system_states': {},
        'sensor_readings': {},
        'component_health': {}
    }
    
    success = twin.update_state(invalid_telemetry)
    assert not success
    assert twin.current_state is None

def test_historical_data(sample_config, sample_telemetry):
    """Test historical data management"""
    twin = DigitalTwin('test_vehicle', sample_config)
    
    # Add multiple states
    for i in range(5):
        telemetry = sample_telemetry.copy()
        telemetry['position']['x'] = float(i)
        twin.update_state(telemetry)
    
    assert len(twin.history) == 5
    assert twin.history[0].position['x'] == 0.0
    assert twin.history[-1].position['x'] == 4.0
