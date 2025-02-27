"""
Integration tests for Model-Based Design components
"""

import pytest
from src.model_based.digital_twin.digital_twin import DigitalTwin
from src.model_based.autodesk.autocad_interface import AutoCADInterface
from src.model_based.autodesk.fusion360_pipeline import Fusion360Pipeline

@pytest.fixture
def test_config():
    return {
        'autocad_path': '/path/to/autocad',
        'fusion360_credentials': {
            'api_key': 'test_key',
            'api_secret': 'test_secret'
        }
    }

@pytest.fixture
def test_vehicle_data():
    return {
        'position': {'x': 0.0, 'y': 0.0, 'z': 0.0},
        'velocity': {'x': 1.0, 'y': 0.0, 'z': 0.0},
        'acceleration': {'x': 0.0, 'y': 0.0, 'z': 0.0},
        'system_states': {'engine': 'running', 'battery': 'charging'},
        'sensor_readings': {'temperature': 25.0, 'pressure': 1.0},
        'component_health': {'engine': 0.95, 'battery': 0.88}
    }

class TestModelIntegration:
    """Test integration between different model-based components"""
    
    def test_digital_twin_autocad_integration(self, test_config, test_vehicle_data):
        """Test integration between Digital Twin and AutoCAD"""
        # Initialize components
        twin = DigitalTwin('test_vehicle', test_config)
        autocad = AutoCADInterface(test_config['autocad_path'])
        
        # Update digital twin state
        twin.update_state(test_vehicle_data)
        
        # Verify AutoCAD model updates
        component_id = f"vehicle_{twin.vehicle_id}"
        component_specs = {
            'position': test_vehicle_data['position'],
            'orientation': {'yaw': 0.0, 'pitch': 0.0, 'roll': 0.0}
        }
        
        assert autocad.update_component(component_id, component_specs)
        
    def test_digital_twin_fusion360_integration(self, test_config, test_vehicle_data):
        """Test integration between Digital Twin and Fusion 360"""
        # Initialize components
        twin = DigitalTwin('test_vehicle', test_config)
        fusion360 = Fusion360Pipeline(test_config['fusion360_credentials'])
        
        # Update digital twin state
        twin.update_state(test_vehicle_data)
        
        # Run simulation in Fusion 360
        simulation_params = {
            'type': 'structural',
            'duration': 3600,
            'resolution': 'high'
        }
        
        results = fusion360.run_simulation(twin.vehicle_id, 'structural', simulation_params)
        assert 'error' not in results
        
    def test_full_system_integration(self, test_config, test_vehicle_data):
        """Test full system integration with all components"""
        # Initialize digital twin
        twin = DigitalTwin('test_vehicle', test_config)
        
        # Simulate a complete workflow
        # 1. Update state
        assert twin.update_state(test_vehicle_data)
        
        # 2. Run maintenance prediction
        predictions = twin.predict_maintenance()
        assert isinstance(predictions, dict)
        assert 'error' not in predictions
        
        # 3. Run simulation
        scenario = {
            'duration': 3600,
            'environment': {'temperature': 25.0, 'humidity': 0.5},
            'events': []
        }
        sim_results = twin.run_simulation(scenario)
        assert isinstance(sim_results, dict)
        assert 'error' not in sim_results
        
        # 4. Get performance metrics
        metrics = twin.get_performance_metrics()
        assert isinstance(metrics, dict)
        assert all(key in metrics for key in ['efficiency', 'reliability', 'performance_score'])
        
    def test_error_handling(self, test_config):
        """Test error handling across integrated components"""
        # Initialize with invalid config
        invalid_config = {
            'autocad_path': '/invalid/path',
            'fusion360_credentials': {
                'api_key': 'invalid_key',
                'api_secret': 'invalid_secret'
            }
        }
        
        with pytest.raises(Exception):
            DigitalTwin('test_vehicle', invalid_config)
            
    def test_data_consistency(self, test_config, test_vehicle_data):
        """Test data consistency across components"""
        # Initialize components
        twin = DigitalTwin('test_vehicle', test_config)
        autocad = AutoCADInterface(test_config['autocad_path'])
        fusion360 = Fusion360Pipeline(test_config['fusion360_credentials'])
        
        # Update state
        twin.update_state(test_vehicle_data)
        
        # Verify data consistency
        # 1. Check AutoCAD model
        component_id = f"vehicle_{twin.vehicle_id}"
        autocad_data = autocad.export_drawing(component_id, '/tmp/test.dxf')
        assert autocad_data
        
        # 2. Check Fusion 360 model
        fusion360_data = fusion360.export_model(twin.vehicle_id)
        assert fusion360_data
        
        # 3. Compare positions
        assert test_vehicle_data['position'] == twin.current_state.position
