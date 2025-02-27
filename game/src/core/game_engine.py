from dataclasses import dataclass
from typing import List, Dict, Optional
import math

@dataclass
class Player:
    name: str
    score: int = 0
    level: int = 1
    badges: List[str] = None
    inventory: Dict[str, int] = None

    def __post_init__(self):
        self.badges = self.badges or []
        self.inventory = self.inventory or {}

    def add_score(self, points: int):
        self.score += points
        # Level up every 1000 points
        new_level = math.floor(self.score / 1000) + 1
        if new_level > self.level:
            self.level = new_level
            return True
        return False

    def add_badge(self, badge: str):
        if badge not in self.badges:
            self.badges.append(badge)
            return True
        return False

@dataclass
class RecyclableItem:
    name: str
    material_type: str
    energy_value: float  # Energy saved by recycling this item
    points: int
    description: str

class RecyclingFormulas:
    @staticmethod
    def calculate_energy_savings(items: List[RecyclableItem]) -> float:
        """Calculate total energy saved from recycling items"""
        return sum(item.energy_value for item in items)

    @staticmethod
    def calculate_environmental_impact(energy_saved: float) -> float:
        """Convert energy savings to CO2 reduction (kg)"""
        # Approximate conversion: 1 kWh = 0.4 kg CO2
        return energy_saved * 0.4

class GameState:
    def __init__(self):
        self.player: Optional[Player] = None
        self.current_level: int = 1
        self.available_items: List[RecyclableItem] = []
        self.recycled_items: List[RecyclableItem] = []
        self.total_energy_saved: float = 0
        self.total_co2_reduced: float = 0

    def initialize_game(self, player_name: str):
        self.player = Player(name=player_name)
        self._load_initial_items()

    def _load_initial_items(self):
        """Load the initial set of recyclable items"""
        self.available_items = [
            RecyclableItem(
                name="Aluminum Can",
                material_type="Metal",
                energy_value=0.15,  # kWh saved per can
                points=10,
                description="Recycling aluminum saves 95% of the energy used to make new cans"
            ),
            RecyclableItem(
                name="Plastic Bottle",
                material_type="Plastic",
                energy_value=0.12,
                points=8,
                description="Recycling plastic reduces oil consumption and CO2 emissions"
            ),
            RecyclableItem(
                name="Glass Bottle",
                material_type="Glass",
                energy_value=0.08,
                points=5,
                description="Glass can be recycled endlessly without loss in quality"
            ),
            RecyclableItem(
                name="Paper",
                material_type="Paper",
                energy_value=0.05,
                points=3,
                description="Recycling paper saves trees and reduces landfill space"
            )
        ]

    def recycle_item(self, item: RecyclableItem) -> Dict[str, float]:
        """Process a recycled item and update game state"""
        self.recycled_items.append(item)
        self.available_items.remove(item)
        
        # Calculate environmental impact
        energy_saved = item.energy_value
        co2_reduced = RecyclingFormulas.calculate_environmental_impact(energy_saved)
        
        # Update totals
        self.total_energy_saved += energy_saved
        self.total_co2_reduced += co2_reduced
        
        # Update player score
        leveled_up = self.player.add_score(item.points)
        
        return {
            "energy_saved": energy_saved,
            "co2_reduced": co2_reduced,
            "points_earned": item.points,
            "leveled_up": leveled_up
        }

    def get_stats(self) -> Dict[str, float]:
        """Get current game statistics"""
        return {
            "score": self.player.score if self.player else 0,
            "level": self.player.level if self.player else 1,
            "total_items_recycled": len(self.recycled_items),
            "total_energy_saved": self.total_energy_saved,
            "total_co2_reduced": self.total_co2_reduced
        }
