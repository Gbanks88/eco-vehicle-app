from dataclasses import dataclass
from typing import List, Dict, Callable, Optional
import random

@dataclass
class Challenge:
    name: str
    description: str
    points: int
    difficulty: int  # 1-5
    type: str  # 'sorting', 'quiz', 'puzzle'
    validator: Callable
    hint: Optional[str] = None

@dataclass
class Level:
    id: int
    name: str
    environment: str
    description: str
    challenges: List[Challenge]
    required_score: int
    completion_badge: str
    unlocked: bool = False
    completed: bool = False

class LevelManager:
    def __init__(self):
        self.levels: Dict[int, Level] = {}
        self._initialize_levels()

    def _initialize_levels(self):
        """Initialize game levels with challenges"""
        
        # Level 1: Urban Environment
        def validate_sorting(items: List[str], bins: Dict[str, List[str]]) -> bool:
            # Example validation for sorting challenge
            correct_bins = {
                "Metal": ["Aluminum Can", "Steel Can"],
                "Plastic": ["Plastic Bottle", "Plastic Container"],
                "Glass": ["Glass Bottle", "Glass Jar"],
                "Paper": ["Newspaper", "Cardboard"]
            }
            return all(item in correct_bins[bin_type] for bin_type, items in bins.items() for item in items)

        sorting_challenge = Challenge(
            name="Sorting Master",
            description="Sort different materials into their correct recycling bins",
            points=100,
            difficulty=1,
            type="sorting",
            validator=validate_sorting,
            hint="Look for recycling symbols on items to identify their material type"
        )

        def validate_energy_quiz(answers: Dict[str, float]) -> bool:
            # Example validation for energy calculation quiz
            correct_answers = {
                "aluminum_energy": 0.15,  # kWh per can
                "plastic_energy": 0.12,   # kWh per bottle
                "total_savings": 0.27     # Total kWh
            }
            return all(abs(answers[k] - v) < 0.01 for k, v in correct_answers.items())

        energy_quiz = Challenge(
            name="Energy Detective",
            description="Calculate the energy savings from recycling different materials",
            points=150,
            difficulty=2,
            type="quiz",
            validator=validate_energy_quiz,
            hint="Remember: Recycling aluminum saves 95% of the energy needed for new production"
        )

        self.levels[1] = Level(
            id=1,
            name="Urban Recycling Center",
            environment="city",
            description="Welcome to the city! Learn the basics of recycling and energy conservation.",
            challenges=[sorting_challenge, energy_quiz],
            required_score=200,
            completion_badge="Urban Recycler",
            unlocked=True
        )

        # Level 2: Forest Environment
        def validate_decomposition(timeline: Dict[str, int]) -> bool:
            # Example validation for decomposition timeline puzzle
            correct_timeline = {
                "banana_peel": 6,     # months
                "paper_bag": 12,      # months
                "plastic_bottle": 450, # years
                "glass_bottle": 1000000 # years
            }
            return all(abs(timeline[k] - v) / v < 0.1 for k, v in correct_timeline.items())

        decomposition_challenge = Challenge(
            name="Time Detective",
            description="Arrange materials by their decomposition time in nature",
            points=200,
            difficulty=3,
            type="puzzle",
            validator=validate_decomposition,
            hint="Think about material properties: natural materials decompose faster"
        )

        self.levels[2] = Level(
            id=2,
            name="Forest Conservation",
            environment="forest",
            description="Explore the forest and learn about material decomposition and ecosystem impact.",
            challenges=[decomposition_challenge],
            required_score=500,
            completion_badge="Forest Guardian",
            unlocked=False
        )

    def get_level(self, level_id: int) -> Optional[Level]:
        """Get a specific level by ID"""
        return self.levels.get(level_id)

    def unlock_level(self, level_id: int) -> bool:
        """Unlock a level if it exists"""
        if level_id in self.levels:
            self.levels[level_id].unlocked = True
            return True
        return False

    def complete_level(self, level_id: int) -> Optional[str]:
        """Mark a level as completed and return the badge earned"""
        if level_id in self.levels:
            level = self.levels[level_id]
            level.completed = True
            return level.completion_badge
        return None

    def get_available_levels(self) -> List[Level]:
        """Get all unlocked levels"""
        return [level for level in self.levels.values() if level.unlocked]

    def validate_challenge(self, level_id: int, challenge_name: str, answer: any) -> bool:
        """Validate a challenge answer"""
        level = self.levels.get(level_id)
        if not level:
            return False
        
        challenge = next((c for c in level.challenges if c.name == challenge_name), None)
        if not challenge:
            return False
            
        return challenge.validator(answer)
