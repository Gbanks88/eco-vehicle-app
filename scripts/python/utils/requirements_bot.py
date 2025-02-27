#!/usr/bin/env python3

import re
import json
import yaml
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import wordnet
import spacy

@dataclass
class Requirement:
    id: str
    title: str
    description: str
    category: str
    priority: int  # 1 (highest) to 5 (lowest)
    source: str
    acceptance_criteria: List[str]
    metrics: Dict[str, str]
    stakeholders: List[str]
    version: str
    created_at: datetime
    updated_at: datetime
    status: str
    dependencies: List[str]
    feasibility_score: float  # 0 to 1

class RequirementsBot:
    def __init__(self):
        # Initialize NLP components
        nltk.download('punkt')
        nltk.download('wordnet')
        self.nlp = spacy.load('en_core_web_sm')
        
        # Load quality criteria patterns
        self.quality_patterns = {
            'ambiguous_terms': ['good', 'fast', 'efficient', 'user-friendly', 'flexible', 'approximately'],
            'measurable_keywords': ['shall', 'must', 'will', 'should'],
            'metric_patterns': r'\d+\s*(ms|seconds|minutes|hours|MB|GB|users|requests|%)'
        }
        
    def generate_requirement(self, input_text: str, category: str, priority: int) -> Requirement:
        """Generate a well-structured requirement from input text"""
        # Clean and process input
        processed_text = self._preprocess_text(input_text)
        
        # Generate unique ID
        req_id = self._generate_id(category)
        
        # Extract metrics
        metrics = self._extract_metrics(processed_text)
        
        # Generate acceptance criteria
        acceptance_criteria = self._generate_acceptance_criteria(processed_text)
        
        # Calculate feasibility
        feasibility = self._calculate_feasibility(processed_text, metrics)
        
        return Requirement(
            id=req_id,
            title=self._generate_title(processed_text),
            description=processed_text,
            category=category,
            priority=priority,
            source="RequirementsBot",
            acceptance_criteria=acceptance_criteria,
            metrics=metrics,
            stakeholders=self._identify_stakeholders(processed_text),
            version="1.0",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            status="Draft",
            dependencies=self._identify_dependencies(processed_text),
            feasibility_score=feasibility
        )
    
    def validate_requirement(self, requirement: Requirement) -> Tuple[bool, List[str]]:
        """Validate a requirement against quality criteria"""
        issues = []
        
        # Check for ambiguity
        ambiguous_terms = self._check_ambiguity(requirement.description)
        if ambiguous_terms:
            issues.append(f"Ambiguous terms found: {', '.join(ambiguous_terms)}")
        
        # Check for measurability
        if not self._has_measurable_criteria(requirement):
            issues.append("No measurable criteria found")
        
        # Check for completeness
        completeness_issues = self._check_completeness(requirement)
        issues.extend(completeness_issues)
        
        # Check for consistency
        consistency_issues = self._check_consistency(requirement)
        issues.extend(consistency_issues)
        
        return len(issues) == 0, issues
    
    def suggest_improvements(self, requirement: Requirement) -> List[str]:
        """Suggest improvements for a requirement"""
        suggestions = []
        
        # Check for missing metrics
        if not requirement.metrics:
            suggestions.append("Add quantifiable metrics to make the requirement measurable")
        
        # Check for acceptance criteria
        if len(requirement.acceptance_criteria) < 2:
            suggestions.append("Add more detailed acceptance criteria")
        
        # Check for stakeholder involvement
        if not requirement.stakeholders:
            suggestions.append("Identify relevant stakeholders for this requirement")
        
        # Check description length
        if len(requirement.description.split()) < 10:
            suggestions.append("Provide more detailed description")
        
        return suggestions
    
    def _preprocess_text(self, text: str) -> str:
        """Clean and normalize input text"""
        text = text.strip()
        text = re.sub(r'\s+', ' ', text)
        return text
    
    def _generate_id(self, category: str) -> str:
        """Generate a unique requirement ID"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"REQ-{category[:3].upper()}-{timestamp}"
    
    def _extract_metrics(self, text: str) -> Dict[str, str]:
        """Extract measurable metrics from text"""
        metrics = {}
        pattern = self.quality_patterns['metric_patterns']
        matches = re.finditer(pattern, text)
        
        for match in matches:
            metric = match.group(0)
            key = f"metric_{len(metrics) + 1}"
            metrics[key] = metric
            
        return metrics
    
    def _generate_acceptance_criteria(self, text: str) -> List[str]:
        """Generate acceptance criteria from requirement text"""
        doc = self.nlp(text)
        criteria = []
        
        # Extract main verbs and their objects
        for sent in doc.sents:
            for token in sent:
                if token.pos_ == "VERB":
                    criterion = f"Verify that the system can {token.text} "
                    for child in token.children:
                        if child.dep_ in ["dobj", "pobj"]:
                            criterion += child.text
                    criteria.append(criterion)
        
        return criteria
    
    def _calculate_feasibility(self, text: str, metrics: Dict[str, str]) -> float:
        """Calculate feasibility score based on complexity and metrics"""
        score = 1.0
        
        # Reduce score for complex requirements
        complexity_factors = {
            'dependencies': len(self._identify_dependencies(text)) * 0.1,
            'metrics_complexity': len(metrics) * 0.05,
            'text_length': len(text.split()) * 0.001
        }
        
        score -= sum(complexity_factors.values())
        return max(0.0, min(1.0, score))
    
    def _check_ambiguity(self, text: str) -> List[str]:
        """Check for ambiguous terms in text"""
        words = word_tokenize(text.lower())
        return [word for word in words if word in self.quality_patterns['ambiguous_terms']]
    
    def _has_measurable_criteria(self, requirement: Requirement) -> bool:
        """Check if requirement has measurable criteria"""
        return bool(requirement.metrics) and bool(requirement.acceptance_criteria)
    
    def _check_completeness(self, requirement: Requirement) -> List[str]:
        """Check for completeness of requirement"""
        issues = []
        
        required_fields = {
            'description': bool(requirement.description.strip()),
            'acceptance_criteria': bool(requirement.acceptance_criteria),
            'metrics': bool(requirement.metrics),
            'stakeholders': bool(requirement.stakeholders)
        }
        
        for field, is_complete in required_fields.items():
            if not is_complete:
                issues.append(f"Missing {field}")
                
        return issues
    
    def _check_consistency(self, requirement: Requirement) -> List[str]:
        """Check for internal consistency"""
        issues = []
        
        # Check if metrics match description
        metrics_mentioned = any(
            metric in requirement.description.lower()
            for metric in requirement.metrics.values()
        )
        if not metrics_mentioned:
            issues.append("Metrics not mentioned in description")
        
        return issues
    
    def _identify_stakeholders(self, text: str) -> List[str]:
        """Identify potential stakeholders from text"""
        doc = self.nlp(text)
        stakeholders = []
        
        # Look for organization names and job titles
        for ent in doc.ents:
            if ent.label_ in ["ORG", "PERSON", "NORP"]:
                stakeholders.append(ent.text)
                
        return list(set(stakeholders))
    
    def _identify_dependencies(self, text: str) -> List[str]:
        """Identify potential dependencies from text"""
        doc = self.nlp(text)
        dependencies = []
        
        # Look for dependency indicators
        dependency_indicators = ["requires", "depends on", "needs", "prerequisite"]
        for token in doc:
            if token.text.lower() in dependency_indicators:
                for chunk in doc.noun_chunks:
                    if chunk.root.head == token:
                        dependencies.append(chunk.text)
                        
        return dependencies
    
    def export_requirements(self, requirements: List[Requirement], format: str = 'json') -> str:
        """Export requirements to specified format"""
        data = [vars(req) for req in requirements]
        
        if format.lower() == 'json':
            return json.dumps(data, default=str, indent=2)
        elif format.lower() == 'yaml':
            return yaml.dump(data, default_flow_style=False)
        else:
            raise ValueError(f"Unsupported format: {format}")

def main():
    # Example usage
    bot = RequirementsBot()
    
    # Example requirement text
    requirement_text = """
    The system shall process user authentication requests within 200ms under normal load conditions.
    This requires integration with the existing user database and must maintain a 99.9% success rate.
    """
    
    # Generate requirement
    requirement = bot.generate_requirement(
        requirement_text,
        category="Performance",
        priority=1
    )
    
    # Validate requirement
    is_valid, issues = bot.validate_requirement(requirement)
    
    # Get improvement suggestions
    suggestions = bot.suggest_improvements(requirement)
    
    # Print results
    print(f"Generated Requirement ID: {requirement.id}")
    print(f"Valid: {is_valid}")
    if issues:
        print("Issues found:")
        for issue in issues:
            print(f"- {issue}")
    if suggestions:
        print("\nSuggested improvements:")
        for suggestion in suggestions:
            print(f"- {suggestion}")

if __name__ == "__main__":
    main()
