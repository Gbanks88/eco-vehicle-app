import unittest
import yaml
import time
from pathlib import Path
from typing import Dict, List

class TestLargeScaleSystems(unittest.TestCase):
    def setUp(self):
        config_dir = Path(__file__).parents[2] / "config"
        
        # Load all configuration files
        self.config_files = [
            "domain_knowledge_bases.yaml",
            "advanced_domain_knowledge.yaml",
            "complex_systems_knowledge.yaml",
            "requirement_templates.yaml",
            "advanced_requirement_templates.yaml",
            "complex_systems_templates.yaml"
        ]
        
        self.configs = {}
        for file in self.config_files:
            with open(config_dir / file) as f:
                self.configs[file] = yaml.safe_load(f)

    def test_knowledge_base_load_time(self):
        """Test knowledge base loading performance"""
        start_time = time.time()
        
        for _ in range(100):  # Simulate multiple loads
            for file in self.config_files:
                with open(Path(__file__).parents[2] / "config" / file) as f:
                    yaml.safe_load(f)
        
        load_time = time.time() - start_time
        self.assertLess(load_time, 2.0)  # Should load 100 times in under 2 seconds

    def test_smart_city_scale(self):
        """Test smart city system scaling"""
        city = self.configs["complex_systems_knowledge.yaml"]["smart_city"]
        
        # Count total components
        component_count = 0
        for subsystem in city["subsystems"].values():
            component_count += len(subsystem)
            
        # Count total metrics
        metric_count = 0
        for category in city["metrics"].values():
            metric_count += len(category)
            
        # Test reasonable scale
        self.assertGreater(component_count, 20)
        self.assertGreater(metric_count, 10)
        self.assertLess(component_count, 100)  # Prevent excessive complexity

    def test_requirement_generation_performance(self):
        """Test requirement generation performance for large systems"""
        templates = self.configs["complex_systems_templates.yaml"]
        
        start_time = time.time()
        generated_requirements = []
        
        # Generate requirements for all systems
        for system, categories in templates.items():
            for category, requirements in categories.items():
                for template in requirements:
                    # Simple parameter replacement simulation
                    requirement = template.replace("{number}", "1000")
                    requirement = requirement.replace("{percentage}", "99.9")
                    requirement = requirement.replace("{time}", "100")
                    generated_requirements.append(requirement)
        
        generation_time = time.time() - start_time
        self.assertLess(generation_time, 1.0)  # Should generate in under 1 second
        self.assertGreater(len(generated_requirements), 100)

    def test_system_analysis_performance(self):
        """Test system analysis performance for complex systems"""
        start_time = time.time()
        
        # Simulate system analysis
        for config_file, data in self.configs.items():
            self._analyze_system_complexity(data)
        
        analysis_time = time.time() - start_time
        self.assertLess(analysis_time, 3.0)  # Should analyze in under 3 seconds

    def _analyze_system_complexity(self, data: Dict) -> Dict:
        """Helper method to analyze system complexity"""
        metrics = {
            "component_count": 0,
            "interaction_count": 0,
            "metric_count": 0,
            "max_depth": 0
        }
        
        def count_items(obj, depth=0):
            if isinstance(obj, dict):
                metrics["max_depth"] = max(metrics["max_depth"], depth)
                for value in obj.values():
                    count_items(value, depth + 1)
            elif isinstance(obj, list):
                metrics["component_count"] += len(obj)
                for item in obj:
                    count_items(item, depth + 1)
            elif isinstance(obj, str):
                if "interact" in obj.lower():
                    metrics["interaction_count"] += 1
                elif any(word in obj.lower() for word in ["metric", "measure", "kpi"]):
                    metrics["metric_count"] += 1
        
        count_items(data)
        return metrics

if __name__ == "__main__":
    unittest.main()
