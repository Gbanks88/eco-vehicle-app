from core.game_engine import GameState, RecyclableItem
from levels.level_manager import LevelManager
from components.quiz_system import QuizSystem

def main():
    # Initialize game components
    game_state = GameState()
    level_manager = LevelManager()
    quiz_system = QuizSystem()

    # Start new game
    print("Welcome to Recycle Quest!")
    player_name = "Player1"  # In a real game, this would be input from the player
    game_state.initialize_game(player_name)

    # Start Level 1
    current_level = level_manager.get_level(1)
    print(f"\nStarting {current_level.name}")
    print(current_level.description)

    # Example: Sorting Challenge
    print("\nChallenge 1: Sorting Master")
    sorting_answer = {
        "Metal": ["Aluminum Can"],
        "Plastic": ["Plastic Bottle"],
        "Glass": ["Glass Bottle"]
    }
    if level_manager.validate_challenge(1, "Sorting Master", sorting_answer):
        print("Great job! You've correctly sorted the materials!")
        game_state.player.add_score(100)
    else:
        print("Try again! Make sure to check the recycling symbols.")

    # Example: Quiz Challenge
    print("\nChallenge 2: Energy Quiz")
    quiz = quiz_system.generate_quiz(num_questions=2, category="physics")
    for question in quiz:
        print(f"\nQuestion: {question.text}")
        for i, option in enumerate(question.options):
            print(f"{i + 1}. {option}")
        
        # In a real game, this would be input from the player
        example_answer = question.correct_answer
        result = quiz_system.check_answer(question.id, example_answer)
        
        if result["correct"]:
            print(f"Correct! {result['explanation']}")
            game_state.player.add_score(result["points"])
        else:
            print(f"Incorrect. {result['explanation']}")

    # Recycle some items
    print("\nRecycling Items...")
    for item in game_state.available_items[:2]:  # Recycle first two items
        result = game_state.recycle_item(item)
        print(f"\nRecycled {item.name}:")
        print(f"Energy Saved: {result['energy_saved']:.2f} kWh")
        print(f"CO2 Reduced: {result['co2_reduced']:.2f} kg")
        print(f"Points Earned: {result['points_earned']}")
        if result['leveled_up']:
            print("Level Up!")

    # Show final stats
    stats = game_state.get_stats()
    print("\nGame Stats:")
    print(f"Score: {stats['score']}")
    print(f"Level: {stats['level']}")
    print(f"Items Recycled: {stats['total_items_recycled']}")
    print(f"Total Energy Saved: {stats['total_energy_saved']:.2f} kWh")
    print(f"Total CO2 Reduced: {stats['total_co2_reduced']:.2f} kg")

if __name__ == "__main__":
    main()
