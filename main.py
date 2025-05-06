from Core.workout_logger import WorkoutLogger
from Core.progress_analyzer import ProgressAnalyzer
from ui.charts import plot_pr_chart, plot_volume_over_time
from ai.ai_coach import AICoach
from ai.natural_language_parser import parse_workout_input


# Muscle group mapping used by AI Coach
muscle_groups = {
    "Chest": ["Bench Press", "Incline Bench", "Dumbbell Press"],
    "Back": ["Deadlift", "Barbell Row", "Lat Pulldown"],
    "Legs": ["Squat", "Leg Press", "Lunges"],
    "Shoulders": ["Overhead Press", "Lateral Raise"],
    "Arms": ["Barbell Curl", "Tricep Pushdown"]
}

def display_logs(analyzer):
    print("\n📋 Recent Logs:")
    print(analyzer.get_recent_sessions().to_string(index=False))

    print("\n🏆 PRs:")
    print(analyzer.get_prs().to_string())

    print("\n📊 Total Volume by Exercise:")
    print(analyzer.get_total_volume_by_exercise().to_string())


def main():
    logger = WorkoutLogger()

    while True:
        print("\n=== AI Gym Tracker ===")
        print("1. Log Workout")
        print("2. View Stats")
        print("3. Log with Natural Language 🧠")
        print("4. Exit")
        choice = input("Choose an option: ")

        if choice == "1":
            ex = input("Exercise name: ")

            try:
                sets = int(input("Sets: "))
                reps = int(input("Reps: "))
                weight = float(input("Weight (kg): "))
            except ValueError:
                print("❌ Invalid input. Please enter numbers for sets, reps, and weight.")
                continue

            logger.log_workout(ex, sets, reps, weight)
            print("✅ Logged!")

        elif choice == "2":

            logs = logger.fetch_all_logs()
            analyzer = ProgressAnalyzer(logs)
            display_logs(analyzer)

            plot_pr_chart(analyzer.df)
            plot_volume_over_time(analyzer.df)

            coach = AICoach(analyzer.df)
            feedback = coach.generate_report(muscle_groups)

            print("\n🧠 AI Coach Feedback:")
            if feedback:
                for tip in feedback:
                    print("–", tip)
            else:
                print("All good — keep lifting hard 💪")

        elif choice == "3":
            raw = input("Describe your lift (e.g. 3x10 bench press at 100):\n> ")
            parsed = parse_workout_input(raw)

            if parsed:
                logger.log_workout(
                    parsed["exercise"],
                    parsed["sets"],
                    parsed["reps"],
                    parsed["weight"]
                )
                print(f"✅ Logged: {parsed['sets']}x{parsed['reps']} {parsed['exercise']} at {parsed['weight']}kg")
            else:
                print("❌ Sorry, couldn't understand that. Try a simpler format like '3x8 squat at 100'.")


        elif choice == "4":
            print("Exiting...")
            break

        else:
            print("Invalid option.")


if __name__ == "__main__":
    main()
