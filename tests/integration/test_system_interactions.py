import unittest
import yaml
from pathlib import Path
from typing import Dict, List

class TestSystemInteractions(unittest.TestCase):
    def setUp(self):
        config_dir = Path(__file__).parents[2] / "config"
        
        # Load all knowledge bases and templates
        with open(config_dir / "complex_systems_knowledge.yaml") as f:
            self.systems_knowledge = yaml.safe_load(f)
        with open(config_dir / "complex_systems_templates.yaml") as f:
            self.systems_templates = yaml.safe_load(f)

    def test_smart_city_integration(self):
        """Test smart city subsystem interactions"""
        city = self.systems_knowledge["smart_city"]
        
        # Test subsystem completeness
        required_subsystems = ["structural", "economic", "environmental", 
                             "management", "energy", "healthcare"]
        for subsystem in required_subsystems:
            self.assertIn(subsystem, city["subsystems"])

        # Test interaction coverage
        for interaction in city["interactions"]:
            # Verify interaction is reflected in metrics
            found = False
            for metric_category in city["metrics"].values():
                for metric in metric_category:
                    if interaction.lower() in metric.lower():
                        found = True
                        break
            self.assertTrue(found, f"Interaction {interaction} not covered in metrics")

    def test_airline_manufacturing_workflow(self):
        """Test airline manufacturing process workflow"""
        airline = self.systems_knowledge["airline_manufacturing"]
        
        # Test process dependencies
        processes = airline["processes"]
        self.assertIn("development", processes)
        self.assertIn("manufacturing", processes)
        self.assertIn("management", processes)

        # Verify process sequence
        dev_steps = processes["development"]
        for i in range(len(dev_steps)-1):
            # Each step should have corresponding metrics
            step = dev_steps[i]
            found_metric = False
            for metric_category in airline["metrics"].values():
                for metric in metric_category:
                    if step.lower() in metric.lower():
                        found_metric = True
                        break
            self.assertTrue(found_metric, f"No metrics for step {step}")

    def test_smart_grid_components(self):
        """Test smart grid component integration"""
        grid = self.systems_knowledge["smart_grid"]
        
        # Test subsystem interfaces
        subsystems = grid["subsystems"]
        components = grid["components"]
        
        # Each subsystem should have supporting components
        for subsystem_name, subsystem in subsystems.items():
            for item in subsystem:
                found_component = False
                for component_category in components.values():
                    for component in component_category:
                        if item.lower() in component.lower():
                            found_component = True
                            break
                self.assertTrue(found_component, 
                              f"No component support for {item} in {subsystem_name}")

        # Test metric coverage
        metrics = grid["metrics"]
        for subsystem in subsystems.values():
            for item in subsystem:
                found_metric = False
                for metric_category in metrics.values():
                    for metric in metric_category:
                        if item.lower() in metric.lower():
                            found_metric = True
                            break
                self.assertTrue(found_metric, f"No metrics for {item}")

if __name__ == "__main__":
    unittest.main()
