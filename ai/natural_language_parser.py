import re
from rapidfuzz import process

EXERCISE_LIST = [
    "Bench Press", "Incline Bench", "Dumbbell Press",
    "Deadlift", "Barbell Row", "Lat Pulldown",
    "Squat", "Leg Press", "Lunges",
    "Overhead Press", "Lateral Raise",
    "Barbell Curl", "Tricep Pushdown"
]

def parse_workout_input(text):
    text = text.lower()

    patterns = [
        r"(?P<sets>\d+)\s*[xX×*]\s*(?P<reps>\d+)\s*(?P<exercise>.+?)\s*(at\s*)?(?P<weight>\d+)",
        r"(?P<exercise>[a-z\s]+)\s*(?P<sets>\d+)\s*sets?\s*of\s*(?P<reps>\d+)\s*reps?\s*(at\s*)?(?P<weight>\d+)",
    ]

    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            data = match.groupdict()

            # Fuzzy match the exercise name
            raw_ex = data["exercise"].strip().title()
            best_match = process.extractOne(raw_ex, EXERCISE_LIST, score_cutoff=60)
            if best_match:
                exercise_name = best_match[0]
            else:
                exercise_name = raw_ex  # fallback

            return {
                "exercise": exercise_name,
                "sets": int(data["sets"]),
                "reps": int(data["reps"]),
                "weight": float(data["weight"])
            }

    return None
