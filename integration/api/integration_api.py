from typing import Dict, List, Optional
import sys
import os
import json

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from src.modeling.uml.diagrams import DiagramGenerator
from game.src.core.game_engine import GameState
from integration.fusion360.fusion360_connector import Fusion360Connector

class IntegrationAPI:
    def __init__(self):
        self.diagram_generator = DiagramGenerator()
        self.game_state = GameState()
        self.fusion360 = Fusion360Connector()
        self.config_path = os.path.join(os.path.dirname(__file__), '../../config/vehicle_config.json')

    def load_vehicle_config(self) -> Dict:
        """Load vehicle configuration"""
        with open(self.config_path, 'r') as f:
            return json.load(f)

    def save_vehicle_config(self, config: Dict):
        """Save vehicle configuration"""
        with open(self.config_path, 'w') as f:
            json.dump(config, f, indent=2)

    def generate_sysml_diagrams(self, diagram_type: str):
        """Generate SysML diagrams"""
        return self.diagram_generator.generate_diagram(diagram_type)

    def update_fusion360_model(self, config: Dict):
        """Update Fusion 360 model with new configuration"""
        self.fusion360.create_eco_vehicle_model(config)

    def update_game_vehicle(self, config: Dict):
        """Update game vehicle properties"""
        # Convert vehicle config to game properties
        vehicle_props = {
            "mass": config["physics"]["mass"],
            "max_speed": config["physics"]["max_speed"],
            "acceleration": config["physics"]["acceleration"],
            "battery_capacity": config["battery"]["capacity"],
            "solar_power": sum(panel["power"] for panel in config["solar_panels"]["panels"])
        }
        return vehicle_props

    def sync_all_systems(self):
        """Synchronize all three systems"""
        # Load current configuration
        config = self.load_vehicle_config()

        # Update SysML diagrams
        self.generate_sysml_diagrams("bdd")  # Block Definition Diagram
        self.generate_sysml_diagrams("ibd")  # Internal Block Diagram

        # Update Fusion 360 model
        self.update_fusion360_model(config)

        # Update game vehicle
        game_props = self.update_game_vehicle(config)
        return {
            "config": config,
            "game_properties": game_props
        }

    def export_fusion360_model(self, export_path: str):
        """Export Fusion 360 model"""
        self.fusion360.export_model(export_path)

    def get_system_status(self) -> Dict:
        """Get status of all integrated systems"""
        return {
            "sysml": {
                "diagrams": self.diagram_generator.list_diagrams(),
                "status": "active"
            },
            "fusion360": {
                "model": "eco_vehicle",
                "status": "active" if self.fusion360.app else "inactive"
            },
            "game": {
                "status": "active",
                "stats": self.game_state.get_stats()
            }
        }
