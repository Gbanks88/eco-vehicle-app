#!/usr/bin/env python3

import json
import yaml
from dataclasses import dataclass
from typing import List, Dict, Optional, Set
from enum import Enum
import spacy
import torch
from transformers import AutoTokenizer, AutoModel
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

class DomainType(Enum):
    ML_AI = "Machine Learning and AI"
    CHIP_DESIGN = "Computer Chip Design"
    EMBEDDED_IOT = "Embedded and IoT Systems"
    POWER_ENERGY = "Power and Energy"
    AEROSPACE = "Space and Aerospace"
    MILITARY = "Government and Military"
    HEALTHCARE = "Healthcare Systems"
    HARDWARE = "Communication Equipment and Hardware"
    CYBERSECURITY = "Networks and Cybersecurity"
    ENVIRONMENT = "Natural Resources and Environment"
    BIOMEDICAL = "Biosciences and Biomedical"

@dataclass
class DomainKnowledge:
    domain: DomainType
    keywords: Set[str]
    standards: Set[str]
    regulations: Set[str]
    metrics: Set[str]
    stakeholders: Set[str]

class DomainRequirementsBot:
    def __init__(self):
        # Initialize NLP components
        self.nlp = spacy.load('en_core_web_sm')
        self.tokenizer = AutoTokenizer.from_pretrained('bert-base-uncased')
        self.model = AutoModel.from_pretrained('bert-base-uncased')
        
        # Load domain knowledge
        self.domain_knowledge = self._load_domain_knowledge()
        
    def _load_domain_knowledge(self) -> Dict[DomainType, DomainKnowledge]:
        """Load domain-specific knowledge bases"""
        knowledge_bases = {
            DomainType.ML_AI: DomainKnowledge(
                domain=DomainType.ML_AI,
                keywords={"neural network", "deep learning", "training data", "inference", "model accuracy"},
                standards={"ISO/IEC 25012", "IEEE 2807-2019", "ISO/IEC 20546"},
                regulations={"GDPR", "CCPA", "AI Act"},
                metrics={"accuracy", "precision", "recall", "F1-score", "AUC-ROC"},
                stakeholders={"Data Scientists", "ML Engineers", "Data Engineers"}
            ),
            DomainType.CHIP_DESIGN: DomainKnowledge(
                domain=DomainType.CHIP_DESIGN,
                keywords={"ASIC", "FPGA", "RTL", "synthesis", "verification"},
                standards={"IEEE 1364", "IEEE 1800", "ISO 26262"},
                regulations={"ITAR", "EAR"},
                metrics={"power consumption", "gate count", "clock frequency", "yield rate"},
                stakeholders={"Chip Architects", "Verification Engineers", "Layout Engineers"}
            ),
            DomainType.EMBEDDED_IOT: DomainKnowledge(
                domain=DomainType.EMBEDDED_IOT,
                keywords={"microcontroller", "RTOS", "sensor network", "firmware"},
                standards={"IEC 61508", "ISO/IEC 30141", "IEEE 2413"},
                regulations={"CE marking", "FCC regulations"},
                metrics={"power efficiency", "latency", "reliability", "bandwidth"},
                stakeholders={"Embedded Engineers", "IoT Architects", "System Integrators"}
            ),
            # Add other domains similarly...
        }
        return knowledge_bases
        
    def analyze_requirement(self, text: str) -> Dict:
        """Analyze requirement text and provide domain-specific insights"""
        # Process text
        doc = self.nlp(text)
        
        # Identify domains
        domains = self._identify_domains(text)
        
        # Extract domain-specific elements
        analysis = {
            "domains": domains,
            "keywords": self._extract_domain_keywords(text, domains),
            "standards": self._identify_applicable_standards(text, domains),
            "regulations": self._check_regulatory_compliance(text, domains),
            "metrics": self._extract_metrics(text, domains),
            "stakeholders": self._identify_stakeholders(text, domains),
            "risks": self._assess_risks(text, domains),
            "suggestions": self._generate_suggestions(text, domains)
        }
        
        return analysis
        
    def generate_domain_requirements(self, domain: DomainType, context: str) -> List[str]:
        """Generate domain-specific requirements based on context"""
        knowledge = self.domain_knowledge[domain]
        
        requirements = []
        
        # Generate functional requirements
        requirements.extend(self._generate_functional_requirements(domain, context))
        
        # Generate compliance requirements
        requirements.extend(self._generate_compliance_requirements(domain))
        
        # Generate performance requirements
        requirements.extend(self._generate_performance_requirements(domain))
        
        return requirements
        
    def validate_domain_compliance(self, text: str, domain: DomainType) -> Dict:
        """Validate requirement compliance with domain-specific standards"""
        knowledge = self.domain_knowledge[domain]
        
        validation = {
            "standards_compliance": self._check_standards_compliance(text, knowledge.standards),
            "regulatory_compliance": self._check_regulatory_compliance(text, [domain]),
            "metrics_compliance": self._validate_metrics(text, knowledge.metrics),
            "completeness": self._check_completeness(text, domain),
            "risks": self._assess_domain_risks(text, domain)
        }
        
        return validation
        
    def _identify_domains(self, text: str) -> List[DomainType]:
        """Identify relevant domains for the requirement"""
        domains = []
        embeddings = self._get_text_embedding(text)
        
        for domain in DomainType:
            knowledge = self.domain_knowledge[domain]
            domain_text = " ".join(knowledge.keywords)
            domain_embedding = self._get_text_embedding(domain_text)
            
            similarity = cosine_similarity(embeddings, domain_embedding)[0][0]
            if similarity > 0.5:  # Threshold can be adjusted
                domains.append(domain)
                
        return domains
        
    def _extract_domain_keywords(self, text: str, domains: List[DomainType]) -> Set[str]:
        """Extract domain-specific keywords from text"""
        keywords = set()
        doc = self.nlp(text)
        
        for domain in domains:
            knowledge = self.domain_knowledge[domain]
            for token in doc:
                if token.text.lower() in knowledge.keywords:
                    keywords.add(token.text.lower())
                    
        return keywords
        
    def _identify_applicable_standards(self, text: str, domains: List[DomainType]) -> Set[str]:
        """Identify applicable standards for the requirement"""
        standards = set()
        
        for domain in domains:
            knowledge = self.domain_knowledge[domain]
            for standard in knowledge.standards:
                if standard.lower() in text.lower():
                    standards.add(standard)
                    
        return standards
        
    def _generate_functional_requirements(self, domain: DomainType, context: str) -> List[str]:
        """Generate domain-specific functional requirements"""
        knowledge = self.domain_knowledge[domain]
        requirements = []
        
        # Template-based generation
        templates = {
            DomainType.ML_AI: [
                "The system shall achieve {metric} of at least {value} on {dataset}",
                "The model shall be retrained when {condition}",
                "The system shall handle {data_type} input data"
            ],
            DomainType.CHIP_DESIGN: [
                "The chip shall operate at {frequency} under {conditions}",
                "Power consumption shall not exceed {power} under {load}",
                "The design shall include {feature} for {purpose}"
            ],
            # Add templates for other domains...
        }
        
        domain_templates = templates.get(domain, [])
        for template in domain_templates:
            # Fill template with context-specific values
            requirement = self._fill_template(template, context, knowledge)
            requirements.append(requirement)
            
        return requirements
        
    def _generate_compliance_requirements(self, domain: DomainType) -> List[str]:
        """Generate compliance-related requirements"""
        knowledge = self.domain_knowledge[domain]
        requirements = []
        
        # Add standards compliance
        for standard in knowledge.standards:
            requirements.append(f"The system shall comply with {standard} standard")
            
        # Add regulatory compliance
        for regulation in knowledge.regulations:
            requirements.append(f"The system shall adhere to {regulation} regulations")
            
        return requirements
        
    def _generate_performance_requirements(self, domain: DomainType) -> List[str]:
        """Generate domain-specific performance requirements"""
        knowledge = self.domain_knowledge[domain]
        requirements = []
        
        for metric in knowledge.metrics:
            requirement = f"The system shall maintain {metric} within acceptable ranges"
            requirements.append(requirement)
            
        return requirements
        
    def _get_text_embedding(self, text: str) -> np.ndarray:
        """Get BERT embedding for text"""
        inputs = self.tokenizer(text, return_tensors="pt", padding=True, truncation=True)
        with torch.no_grad():
            outputs = self.model(**inputs)
        return outputs.last_hidden_state.mean(dim=1).numpy()
        
    def _fill_template(self, template: str, context: str, knowledge: DomainKnowledge) -> str:
        """Fill requirement template with context-specific values"""
        # Implement template filling logic based on context and domain knowledge
        # This is a placeholder implementation
        filled = template
        return filled
        
    def _assess_risks(self, text: str, domains: List[DomainType]) -> List[str]:
        """Assess potential risks in the requirement"""
        risks = []
        
        for domain in domains:
            if domain == DomainType.ML_AI:
                risks.extend(self._assess_ai_risks(text))
            elif domain == DomainType.CYBERSECURITY:
                risks.extend(self._assess_security_risks(text))
            # Add risk assessment for other domains...
            
        return risks
        
    def _generate_suggestions(self, text: str, domains: List[DomainType]) -> List[str]:
        """Generate improvement suggestions"""
        suggestions = []
        
        # Analyze completeness
        missing_elements = self._check_completeness(text, domains[0])
        if missing_elements:
            suggestions.append(f"Add missing elements: {', '.join(missing_elements)}")
            
        # Check for domain-specific best practices
        for domain in domains:
            suggestions.extend(self._check_domain_best_practices(text, domain))
            
        return suggestions

def main():
    # Example usage
    bot = DomainRequirementsBot()
    
    # Example requirement
    requirement = """
    The machine learning model shall achieve 95% accuracy on the test dataset
    while maintaining GDPR compliance for data processing.
    """
    
    # Analyze requirement
    analysis = bot.analyze_requirement(requirement)
    print("Requirement Analysis:")
    print(json.dumps(analysis, indent=2))
    
    # Generate domain-specific requirements
    ml_requirements = bot.generate_domain_requirements(
        DomainType.ML_AI,
        "Image classification system for medical diagnosis"
    )
    print("\nGenerated Requirements:")
    for req in ml_requirements:
        print(f"- {req}")
        
    # Validate domain compliance
    validation = bot.validate_domain_compliance(requirement, DomainType.ML_AI)
    print("\nValidation Results:")
    print(json.dumps(validation, indent=2))

if __name__ == "__main__":
    main()
