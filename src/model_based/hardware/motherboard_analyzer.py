"""Motherboard Analysis Module for Eco Vehicle Project.

This module provides functionality to analyze and select optimal motherboard
configurations for eco vehicle computer systems, considering factors like
power efficiency, compatibility, and cost-effectiveness.
"""

from dataclasses import dataclass
from enum import Enum
from typing import List, Dict, Optional
import json

class SocketType(Enum):
    """CPU socket types supported by the analyzer."""
    LGA_1150 = "LGA 1150"
    LGA_1151 = "LGA 1151"
    LGA_1155 = "LGA 1155"
    LGA_1200 = "LGA 1200"
    AM4 = "AM4"
    AM5 = "AM5"

class ChipsetFeature(Enum):
    """Chipset features that may be relevant for eco vehicle systems."""
    USB3_NATIVE = "USB 3.0 Native Support"
    VPRO = "Intel vPro Technology"
    ADVANCED_POWER = "Advanced Power Management"
    RAID = "RAID Support"
    PCIe_3 = "PCIe 3.0 Support"
    PCIe_4 = "PCIe 4.0 Support"

@dataclass
class MemoryConfig:
    """Memory configuration specifications."""
    slots: int
    max_speed: int  # MHz
    max_capacity: int  # GB
    voltage: float  # V
    ecc_support: bool = False

@dataclass
class PowerProfile:
    """Power consumption and efficiency metrics."""
    idle_power: float  # Watts
    load_power: float  # Watts
    vrm_efficiency: float  # Percentage
    max_tdp_support: int  # Watts

@dataclass
class MotherboardSpec:
    """Complete motherboard specifications."""
    model: str
    manufacturer: str
    socket: SocketType
    chipset: str
    memory: MemoryConfig
    features: List[ChipsetFeature]
    power: PowerProfile
    cost: float
    form_factor: str
    pcie_slots: Dict[str, int]  # slot_type: count

class MotherboardAnalyzer:
    """Analyzes and recommends motherboard configurations for eco vehicles."""
    
    def __init__(self):
        self.motherboards: List[MotherboardSpec] = []
        self.power_weight = 0.4
        self.cost_weight = 0.3
        self.feature_weight = 0.3
    
    def load_database(self, json_path: str) -> None:
        """Load motherboard database from JSON file."""
        with open(json_path, 'r') as f:
            data = json.load(f)
            self.motherboards = []
            for board_data in data['motherboards']:
                # Convert string socket type to enum
                board_data['socket'] = SocketType(board_data['socket'])
                
                # Convert string features to enums
                board_data['features'] = [
                    ChipsetFeature(f) for f in board_data['features']
                ]
                
                # Create MemoryConfig object
                board_data['memory'] = MemoryConfig(**board_data['memory'])
                
                # Create PowerProfile object
                board_data['power'] = PowerProfile(**board_data['power'])
                
                self.motherboards.append(MotherboardSpec(**board_data))
    
    def calculate_power_score(self, power: PowerProfile) -> float:
        """Calculate power efficiency score (0-1)."""
        # Lower power consumption and higher efficiency is better
        idle_score = 1 - (power.idle_power / 20)  # Assume 20W is max acceptable idle
        load_score = 1 - (power.load_power / 100)  # Assume 100W is max acceptable load
        efficiency_score = power.vrm_efficiency / 100
        
        return (idle_score + load_score + efficiency_score) / 3
    
    def calculate_feature_score(self, features: List[ChipsetFeature]) -> float:
        """Calculate feature completeness score (0-1)."""
        essential_features = {
            ChipsetFeature.USB3_NATIVE,
            ChipsetFeature.ADVANCED_POWER,
            ChipsetFeature.PCIe_3
        }
        
        has_essential = sum(1 for f in essential_features if f in features)
        bonus_features = len(features) - has_essential
        
        return (has_essential / len(essential_features) * 0.7 + 
                min(bonus_features / 3, 1) * 0.3)
    
    def calculate_cost_score(self, cost: float) -> float:
        """Calculate cost effectiveness score (0-1)."""
        # Assume $300 is max acceptable cost
        return 1 - min(cost / 300, 1)
    
    def analyze_motherboard(self, board: MotherboardSpec) -> float:
        """Calculate overall score for a motherboard (0-1)."""
        power_score = self.calculate_power_score(board.power)
        feature_score = self.calculate_feature_score(board.features)
        cost_score = self.calculate_cost_score(board.cost)
        
        return (power_score * self.power_weight +
                feature_score * self.feature_weight +
                cost_score * self.cost_weight)
    
    def recommend_motherboards(self, 
                             max_power: Optional[float] = None,
                             max_cost: Optional[float] = None,
                             required_features: Optional[List[ChipsetFeature]] = None
                             ) -> List[tuple[MotherboardSpec, float]]:
        """
        Recommend motherboards based on criteria and return them with scores.
        
        Args:
            max_power: Maximum acceptable load power in watts
            max_cost: Maximum acceptable cost in USD
            required_features: List of required chipset features
            
        Returns:
            List of (motherboard, score) tuples, sorted by score descending
        """
        candidates = self.motherboards.copy()
        
        # Apply filters
        if max_power is not None:
            candidates = [b for b in candidates if b.power.load_power <= max_power]
        
        if max_cost is not None:
            candidates = [b for b in candidates if b.cost <= max_cost]
            
        if required_features is not None:
            candidates = [b for b in candidates 
                        if all(f in b.features for f in required_features)]
        
        # Score and sort candidates
        scored_boards = [(board, self.analyze_motherboard(board)) 
                        for board in candidates]
        return sorted(scored_boards, key=lambda x: x[1], reverse=True)
    
    def adjust_weights(self, power: float, cost: float, feature: float) -> None:
        """Adjust importance weights for different factors."""
        total = power + cost + feature
        self.power_weight = power / total
        self.cost_weight = cost / total
        self.feature_weight = feature / total
