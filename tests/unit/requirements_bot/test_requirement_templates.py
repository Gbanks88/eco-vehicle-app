import unittest
import yaml
from pathlib import Path

class TestRequirementTemplates(unittest.TestCase):
    def setUp(self):
        # Load requirement templates
        config_dir = Path(__file__).parents[3] / "config"
        
        with open(config_dir / "requirement_templates.yaml") as f:
            self.templates = yaml.safe_load(f)
        with open(config_dir / "advanced_requirement_templates.yaml") as f:
            self.advanced_templates = yaml.safe_load(f)
        with open(config_dir / "complex_systems_templates.yaml") as f:
            self.complex_templates = yaml.safe_load(f)

    def test_template_format(self):
        """Test that templates have correct placeholder format"""
        for domain in self.templates.values():
            for category in domain.values():
                for template in category:
                    # Check for {parameter} format
                    self.assertRegex(template, r"\{[a-zA-Z_]+\}")

    def test_advanced_templates(self):
        """Test advanced domain templates"""
        required_categories = [
            "filter_design",
            "stability",
            "processor_design",
            "model_optimization"
        ]
        for category in required_categories:
            found = False
            for domain in self.advanced_templates.values():
                if category in domain:
                    found = True
                    break
            self.assertTrue(found, f"Category {category} not found")

    def test_complex_system_templates(self):
        """Test complex system requirement templates"""
        required_systems = ["smart_city", "airline_manufacturing", "smart_grid"]
        for system in required_systems:
            self.assertIn(system, self.complex_templates)
            # Each system should have multiple requirement categories
            self.assertGreater(len(self.complex_templates[system]), 3)

    def test_template_completeness(self):
        """Test that templates cover all necessary aspects"""
        aspects = ["functional", "performance", "safety", "reliability"]
        for domain in self.templates.values():
            covered_aspects = []
            for category in domain.keys():
                for aspect in aspects:
                    if aspect in category.lower():
                        covered_aspects.append(aspect)
            self.assertGreater(len(covered_aspects), 0)

if __name__ == "__main__":
    unittest.main()
