"""Demo script showing how to use the motherboard analyzer."""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

from model_based.hardware.motherboard_analyzer import (
    MotherboardAnalyzer,
    ChipsetFeature
)

def main():
    """Run motherboard analysis demo."""
    # Initialize analyzer
    analyzer = MotherboardAnalyzer()
    
    # Load motherboard database
    analyzer.load_database('data/hardware/motherboard_database.json')
    
    # Example 1: Get all recommendations sorted by overall score
    print("All motherboards ranked by overall score:")
    recommendations = analyzer.recommend_motherboards()
    for board, score in recommendations:
        print(f"{board.manufacturer} {board.model}: {score:.2f}")
    print()
    
    # Example 2: Find power-efficient boards under $100
    print("Power-efficient boards under $100:")
    analyzer.adjust_weights(power=0.6, cost=0.2, feature=0.2)
    recommendations = analyzer.recommend_motherboards(max_cost=100.0)
    for board, score in recommendations:
        print(f"{board.manufacturer} {board.model}: {score:.2f}")
    print()
    
    # Example 3: Find feature-rich boards with specific requirements
    print("Feature-rich boards with USB 3.0 and PCIe 3.0:")
    analyzer.adjust_weights(power=0.3, cost=0.3, feature=0.4)
    required_features = [
        ChipsetFeature.USB3_NATIVE,
        ChipsetFeature.PCIe_3
    ]
    recommendations = analyzer.recommend_motherboards(
        required_features=required_features
    )
    for board, score in recommendations:
        print(f"{board.manufacturer} {board.model}: {score:.2f}")

if __name__ == "__main__":
    main()
