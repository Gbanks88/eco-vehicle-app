#!/usr/bin/env python3

import json
import yaml
from datetime import datetime
from pathlib import Path
import pandas as pd
import numpy as np
from typing import Dict, List, Any
import logging

class BotDataCollector:
    def __init__(self, base_dir: str):
        self.base_dir = Path(base_dir)
        self.user_format_dir = self.base_dir / "data/user_format"
        self.ai_patterns_dir = self.base_dir / "data/ai_patterns"
        self.system_analysis_dir = self.base_dir / "data/system_analysis"
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.base_dir / "logs/bot_data_collection.log"),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger("BotDataCollector")

    def collect_bot_data(self, bot_name: str, data: Dict[str, Any]):
        """Collect and store bot data in different formats"""
        timestamp = datetime.now().isoformat()
        
        # 1. User-friendly format (CSV)
        self._save_user_format(bot_name, data, timestamp)
        
        # 2. AI Pattern Analysis (JSON with metadata)
        self._save_ai_patterns(bot_name, data, timestamp)
        
        # 3. System Analysis Format (YAML with detailed annotations)
        self._save_system_analysis(bot_name, data, timestamp)

    def _save_user_format(self, bot_name: str, data: Dict[str, Any], timestamp: str):
        """Save data in user-friendly CSV format"""
        try:
            # Flatten nested data for CSV format
            flat_data = self._flatten_dict(data)
            df = pd.DataFrame([flat_data])
            
            # Add metadata columns
            df['bot_name'] = bot_name
            df['timestamp'] = timestamp
            
            # Save to CSV
            output_file = self.user_format_dir / f"{bot_name}_data.csv"
            if output_file.exists():
                df.to_csv(output_file, mode='a', header=False, index=False)
            else:
                df.to_csv(output_file, index=False)
                
            self.logger.info(f"Saved user format data for {bot_name}")
        except Exception as e:
            self.logger.error(f"Error saving user format data: {str(e)}")

    def _save_ai_patterns(self, bot_name: str, data: Dict[str, Any], timestamp: str):
        """Save data with AI pattern analysis"""
        try:
            ai_patterns = {
                'metadata': {
                    'bot_name': bot_name,
                    'timestamp': timestamp,
                    'pattern_version': '1.0'
                },
                'raw_data': data,
                'pattern_analysis': {
                    'data_types': self._analyze_data_types(data),
                    'value_distributions': self._analyze_value_distributions(data),
                    'relationship_patterns': self._analyze_relationships(data)
                }
            }
            
            output_file = self.ai_patterns_dir / f"{bot_name}_patterns_{timestamp}.json"
            with open(output_file, 'w') as f:
                json.dump(ai_patterns, f, indent=2)
                
            self.logger.info(f"Saved AI patterns for {bot_name}")
        except Exception as e:
            self.logger.error(f"Error saving AI patterns: {str(e)}")

    def _save_system_analysis(self, bot_name: str, data: Dict[str, Any], timestamp: str):
        """Save data with detailed system analysis"""
        try:
            system_analysis = {
                'metadata': {
                    'bot_name': bot_name,
                    'timestamp': timestamp,
                    'analysis_version': '1.0'
                },
                'data_structure': {
                    'schema': self._generate_schema(data),
                    'relationships': self._analyze_relationships(data),
                    'constraints': self._analyze_constraints(data)
                },
                'raw_data': data,
                'analysis_results': {
                    'quality_metrics': self._calculate_quality_metrics(data),
                    'statistical_analysis': self._perform_statistical_analysis(data)
                }
            }
            
            output_file = self.system_analysis_dir / f"{bot_name}_analysis_{timestamp}.yaml"
            with open(output_file, 'w') as f:
                yaml.dump(system_analysis, f, default_flow_style=False)
                
            self.logger.info(f"Saved system analysis for {bot_name}")
        except Exception as e:
            self.logger.error(f"Error saving system analysis: {str(e)}")

    def _flatten_dict(self, d: Dict[str, Any], parent_key: str = '', sep: str = '_') -> Dict[str, Any]:
        """Flatten nested dictionary"""
        items: List = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self._flatten_dict(v, new_key, sep).items())
            else:
                items.append((new_key, v))
        return dict(items)

    def _analyze_data_types(self, data: Dict[str, Any]) -> Dict[str, str]:
        """Analyze and return data types of all fields"""
        types = {}
        for key, value in self._flatten_dict(data).items():
            types[key] = str(type(value).__name__)
        return types

    def _analyze_value_distributions(self, data: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """Analyze value distributions for numerical and categorical data"""
        distributions = {}
        flat_data = self._flatten_dict(data)
        
        for key, value in flat_data.items():
            if isinstance(value, (int, float)):
                distributions[key] = {
                    'type': 'numerical',
                    'min': value,
                    'max': value,
                    'mean': value
                }
            elif isinstance(value, str):
                distributions[key] = {
                    'type': 'categorical',
                    'unique_values': [value]
                }
        return distributions

    def _analyze_relationships(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze relationships between data fields"""
        # This is a placeholder for actual relationship analysis
        return [{'type': 'correlation', 'fields': list(data.keys())}]

    def _generate_schema(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate schema from data"""
        schema = {}
        for key, value in data.items():
            if isinstance(value, dict):
                schema[key] = self._generate_schema(value)
            else:
                schema[key] = {
                    'type': type(value).__name__,
                    'required': True
                }
        return schema

    def _analyze_constraints(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze data constraints"""
        # This is a placeholder for actual constraint analysis
        return [{'type': 'required', 'fields': list(data.keys())}]

    def _calculate_quality_metrics(self, data: Dict[str, Any]) -> Dict[str, float]:
        """Calculate data quality metrics"""
        return {
            'completeness': 1.0,  # Placeholder
            'accuracy': 1.0,      # Placeholder
            'consistency': 1.0    # Placeholder
        }

    def _perform_statistical_analysis(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform statistical analysis on numerical data"""
        stats = {}
        flat_data = self._flatten_dict(data)
        
        for key, value in flat_data.items():
            if isinstance(value, (int, float)):
                stats[key] = {
                    'mean': float(value),
                    'std': 0.0,  # Placeholder
                    'min': float(value),
                    'max': float(value)
                }
        return stats
