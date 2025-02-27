import unittest
import yaml
import re
import os
from pathlib import Path

class TestDomainKnowledge(unittest.TestCase):
    def setUp(self):
        # Load domain knowledge bases
        config_dir = Path(__file__).parents[3] / "config"
        
        with open(config_dir / "domain_knowledge_bases.yaml") as f:
            self.domain_knowledge = yaml.safe_load(f)
        with open(config_dir / "advanced_domain_knowledge.yaml") as f:
            self.advanced_knowledge = yaml.safe_load(f)
        with open(config_dir / "complex_systems_knowledge.yaml") as f:
            self.complex_knowledge = yaml.safe_load(f)

    def test_knowledge_structure(self):
        """Test that all knowledge bases have required components"""
        for domain in self.domain_knowledge.values():
            self.assertIn("keywords", domain)
            self.assertIn("standards", domain)
            self.assertIn("metrics", domain)

    def test_advanced_domains(self):
        """Test advanced domain specific content"""
        required_domains = [
            "digital_signal_processing",
            "control_systems",
            "modern_architecture",
            "communication_systems"
        ]
        for domain in required_domains:
            self.assertIn(domain, self.advanced_knowledge)

    def test_complex_systems(self):
        """Test complex systems knowledge"""
        required_systems = ["smart_city", "airline_manufacturing", "smart_grid"]
        for system in required_systems:
            self.assertIn(system, self.complex_knowledge)
            self.assertIn("subsystems", self.complex_knowledge[system])
            self.assertIn("metrics", self.complex_knowledge[system])

    def test_standards_validity(self):
        """Test that standards references are valid"""
        for domain in self.domain_knowledge.values():
            for standard in domain["standards"]:
                # Standards can be either:
                # 1. Standard format: Letters + Numbers (e.g., "ISO 9001")
                # 2. Acronym format: All caps (e.g., "DICOM")
                # 3. Combined format: Letters + Numbers + Description (e.g., "ISO/IEC 27001 Security")
                self.assertTrue(
                    bool(re.match(r"^[A-Z]+.*\s*\d+.*$", standard)) or  # Standard format
                    bool(re.match(r"^[A-Z]+$", standard)) or           # Acronym format
                    bool(re.match(r"^[A-Z]+[/-][A-Z]+.*$", standard)), # Combined format
                    f"Invalid standard format: {standard}"
                )

if __name__ == "__main__":
    unittest.main()
