from dataclasses import dataclass
from typing import List, Dict, Optional
import random

@dataclass
class Question:
    id: str
    text: str
    options: List[str]
    correct_answer: int  # Index of correct option
    explanation: str
    points: int
    difficulty: int  # 1-5
    category: str  # 'physics', 'chemistry', 'biology', 'general'

class QuizSystem:
    def __init__(self):
        self.questions: Dict[str, Question] = {}
        self._initialize_questions()

    def _initialize_questions(self):
        """Initialize the quiz question bank"""
        # Physics Questions
        self.questions["PHY001"] = Question(
            id="PHY001",
            text="How much energy is saved by recycling one aluminum can compared to producing a new one?",
            options=[
                "45% of the energy",
                "75% of the energy",
                "95% of the energy",
                "25% of the energy"
            ],
            correct_answer=2,
            explanation="Recycling aluminum cans saves 95% of the energy needed to produce new ones from raw materials.",
            points=10,
            difficulty=1,
            category="physics"
        )

        self.questions["PHY002"] = Question(
            id="PHY002",
            text="What is the primary energy source saved when recycling plastic bottles?",
            options=[
                "Coal",
                "Natural Gas",
                "Oil",
                "Solar Energy"
            ],
            correct_answer=2,
            explanation="Plastic is made from oil, so recycling plastic bottles helps conserve oil resources.",
            points=15,
            difficulty=2,
            category="physics"
        )

        # Chemistry Questions
        self.questions["CHEM001"] = Question(
            id="CHEM001",
            text="Which chemical process is used to recycle PET plastic bottles?",
            options=[
                "Oxidation",
                "Depolymerization",
                "Fermentation",
                "Crystallization"
            ],
            correct_answer=1,
            explanation="PET plastic is recycled through depolymerization, breaking down the long polymer chains.",
            points=20,
            difficulty=3,
            category="chemistry"
        )

        # Biology Questions
        self.questions["BIO001"] = Question(
            id="BIO001",
            text="How long does it take for a plastic bottle to decompose in nature?",
            options=[
                "10-20 years",
                "50-100 years",
                "450-500 years",
                "1000+ years"
            ],
            correct_answer=2,
            explanation="Plastic bottles take approximately 450 years to decompose in nature.",
            points=10,
            difficulty=1,
            category="biology"
        )

    def get_question(self, question_id: str) -> Optional[Question]:
        """Get a specific question by ID"""
        return self.questions.get(question_id)

    def get_random_question(self, category: Optional[str] = None, difficulty: Optional[int] = None) -> Optional[Question]:
        """Get a random question, optionally filtered by category and/or difficulty"""
        filtered_questions = self.questions.values()
        
        if category:
            filtered_questions = [q for q in filtered_questions if q.category == category]
        if difficulty:
            filtered_questions = [q for q in filtered_questions if q.difficulty == difficulty]
            
        return random.choice(list(filtered_questions)) if filtered_questions else None

    def check_answer(self, question_id: str, answer: int) -> Dict[str, any]:
        """Check if an answer is correct and return result with explanation"""
        question = self.questions.get(question_id)
        if not question:
            return {"correct": False, "error": "Question not found"}
            
        is_correct = answer == question.correct_answer
        return {
            "correct": is_correct,
            "points": question.points if is_correct else 0,
            "explanation": question.explanation
        }

    def generate_quiz(self, num_questions: int = 5, category: Optional[str] = None, difficulty: Optional[int] = None) -> List[Question]:
        """Generate a quiz with specified number of questions"""
        available_questions = list(self.questions.values())
        
        if category:
            available_questions = [q for q in available_questions if q.category == category]
        if difficulty:
            available_questions = [q for q in available_questions if q.difficulty == difficulty]
            
        return random.sample(available_questions, min(num_questions, len(available_questions)))
