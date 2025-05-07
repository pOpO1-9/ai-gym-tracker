import streamlit as st
from core.workout_logger import WorkoutLogger
from core.progress_analyzer import ProgressAnalyzer
from ai.ai_coach import AICoach
from ai.natural_language_parser import parse_workout_input
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
import json
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


PROGRAM_FILE = "data/program.json"

def load_program():
    if os.path.exists(PROGRAM_FILE):
        with open(PROGRAM_FILE, "r") as f:
            return json.load(f)
    return {"program": [], "current_index": 0}

def save_program(data):
    with open(PROGRAM_FILE, "w") as f:
        json.dump(data, f, indent=2)

# Template definitions
template_workouts = {
    "Push Day A": [
        {"exercise": "Bench Press", "sets": 4, "reps": 8, "weight": 90},
        {"exercise": "Overhead Press", "sets": 3, "reps": 10, "weight": 50},
        {"exercise": "Tricep Pushdown", "sets": 3, "reps": 12, "weight": 30}
    ],
    "Pull Day A": [
        {"exercise": "Barbell Row", "sets": 4, "reps": 8, "weight": 80},
        {"exercise": "Lat Pulldown", "sets": 3, "reps": 10, "weight": 60},
        {"exercise": "Barbell Curl", "sets": 3, "reps": 12, "weight": 25}
    ],
    "Leg Day A": [
        {"exercise": "Squat", "sets": 4, "reps": 6, "weight": 100},
        {"exercise": "Leg Press", "sets": 3, "reps": 10, "weight": 180},
        {"exercise": "Lunges", "sets": 3, "reps": 12, "weight": 20}
    ]
}

TEMPLATE_FILE = "data/templates.json"

def load_custom_templates():
    if os.path.exists(TEMPLATE_FILE):
        with open(TEMPLATE_FILE, "r") as f:
            return json.load(f)
    return {}

def save_custom_template(name, exercises):
    templates = load_custom_templates()
    templates[name] = exercises
    with open(TEMPLATE_FILE, "w") as f:
        json.dump(templates, f, indent=2)

# Merge user templates
template_workouts.update(load_custom_templates())

# Initialize DB + logger
logger = WorkoutLogger()
logs = logger.fetch_all_logs()
analyzer = ProgressAnalyzer(logs)
df = analyzer.df

# Predefined muscle groups
muscle_groups = {
    "Chest": ["Bench Press", "Incline Bench", "Dumbbell Press"],
    "Back": ["Deadlift", "Barbell Row", "Lat Pulldown"],
    "Legs": ["Squat", "Leg Press", "Lunges"],
    "Shoulders": ["Overhead Press", "Lateral Raise"],
    "Arms": ["Barbell Curl", "Tricep Pushdown"]
}

# App Layout
st.set_page_config(page_title="AI Gym Tracker", layout="wide")
st.title("🏋️ AI Gym Tracker")
st.markdown("Mobile-friendly workout tracker with charts and AI insights.")

# Tabs
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📥 Log Workout",
    "📊 Progress",
    "🧠 AI Coach",
    "🗑️ Delete Logs",
    "📋 Templates",
    "🗓️ Program"
])



# --- 📥 Log Workout ---
with tab1:
    st.subheader("Quick Log (Natural Language)")
    input_text = st.text_input("e.g. '3x10 bench at 90'")

    if st.button("Log Workout"):
        parsed = parse_workout_input(input_text)
        if parsed:
            logger.log_workout(**parsed)
            st.success(f"✅ Logged: {parsed['sets']}x{parsed['reps']} {parsed['exercise']} at {parsed['weight']}kg")
        else:
            st.error("❌ Couldn't understand that. Try '3x10 deadlift at 120'.")

# --- 📊 Progress ---
with tab2:
    st.subheader("Progress Charts")

    if df.empty:
        st.info("No workouts logged yet.")
    else:
        # Chart area
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### 🏆 Personal Records")
            prs = df.groupby("exercise")["weight"].max().sort_values()
            st.bar_chart(prs)

        with col2:
            st.markdown("#### 📈 Volume Over Time")
            df["date"] = pd.to_datetime(df["date"])
            df["volume"] = df["sets"] * df["reps"] * df["weight"]
            volume = df.groupby("date")["volume"].sum()
            st.line_chart(volume)

        # ✅ Workout history log table
        st.markdown("### 📋 Workout Log History")
        st.dataframe(df.sort_values("date", ascending=False), use_container_width=True)

        # ✅ CSV Export button
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="⬇️ Download Log as CSV",
            data=csv,
            file_name="workout_log.csv",
            mime="text/csv"
        )


# --- 🧠 AI Coach ---
with tab3:
    st.subheader("AI Feedback")
    coach = AICoach(df)
    feedback = coach.generate_report(muscle_groups)

    if feedback:
        for tip in feedback:
            st.warning(tip)
    else:
        st.success("All good! You’re training consistently 💪")

# --- 🗑️ Delete Logs ---
with tab4:
    st.subheader("Delete Workout Logs")

    if df.empty:
        st.info("No logs to delete.")
    else:
        # Show table with delete buttons
        for _, row in df.sort_values("date", ascending=False).iterrows():
            col1, col2 = st.columns([4, 1])
            with col1:
                st.write(f"{row['date'].strftime('%Y-%m-%d')} | {row['exercise']} - {row['sets']}x{row['reps']} @ {row['weight']}kg")
            with col2:
                if st.button("Delete", key=row['id']):
                    logger.conn.execute("DELETE FROM workouts WHERE id = ?", (row['id'],))
                    logger.conn.commit()
                    st.rerun()

# --- 📋 Templates ---
with tab5:
    st.subheader("Quick Log Templates")

    for name, exercises in template_workouts.items():
        if st.button(f"Log: {name}"):
            for entry in exercises:
                logger.log_workout(**entry)
            st.success(f"✅ {name} logged!")
            st.rerun()

    # ✅ Moved outside the loop 👇
    st.divider()
    st.subheader("➕ Create New Template")

    new_name = st.text_input("Template Name")

    new_exercises = []
    with st.form("new_template_form"):
        for i in range(1, 6):
            st.markdown(f"**Exercise {i}**")
            ex = st.text_input(f"Exercise name {i}", key=f"ex{i}")
            sets = st.number_input(f"Sets {i}", 1, 10, key=f"sets{i}")
            reps = st.number_input(f"Reps {i}", 1, 20, key=f"reps{i}")
            weight = st.number_input(f"Weight {i} (kg)", 0.0, 500.0, key=f"wt{i}")
            if ex:
                new_exercises.append({
                    "exercise": ex.title(),
                    "sets": sets,
                    "reps": reps,
                    "weight": weight
                })

        submitted = st.form_submit_button("Save Template")
        if submitted:
            if new_name and new_exercises:
                save_custom_template(new_name, new_exercises)
                st.success(f"✅ Saved: {new_name}")
                st.rerun()
            else:
                st.error("❌ Please add a name and at least one exercise.")

# --- Manage Custom Templates ---
custom_templates = load_custom_templates()

if custom_templates:
    st.divider()
    st.subheader("🧹 Manage Saved Templates")

    for name in sorted(custom_templates.keys()):
        exercises = custom_templates[name]

        with st.expander(f"📋 {name}"):
            edited_exercises = []

            for i, ex in enumerate(exercises):
                st.markdown(f"**Exercise {i + 1}**")
                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    exercise = st.text_input("Name", ex["exercise"], key=f"{name}_ex_{i}")
                with col2:
                    sets = st.number_input("Sets", 1, 10, value=ex["sets"], key=f"{name}_sets_{i}")
                with col3:
                    reps = st.number_input("Reps", 1, 20, value=ex["reps"], key=f"{name}_reps_{i}")
                with col4:
                    weight = st.number_input("Weight (kg)", 0.0, 500.0, value=ex["weight"], key=f"{name}_wt_{i}")

                edited_exercises.append({
                    "exercise": exercise.title(),
                    "sets": sets,
                    "reps": reps,
                    "weight": weight
                })

            save_col, del_col = st.columns([1, 1])

            with save_col:
                if st.button("💾 Save Changes", key=f"save_{name}"):
                    templates = load_custom_templates()
                    templates[name] = edited_exercises
                    with open(TEMPLATE_FILE, "w") as f:
                        json.dump(templates, f, indent=2)
                    st.success(f"✅ Updated: {name}")
                    st.rerun()

            with del_col:
                if st.button("🗑️ Delete Template", key=f"del_{name}"):
                    templates = load_custom_templates()
                    templates.pop(name, None)
                    with open(TEMPLATE_FILE, "w") as f:
                        json.dump(templates, f, indent=2)
                    st.warning(f"🧹 Deleted template: {name}")
                    st.rerun()

# --- 🗓️ Program Tab ---
with tab6:
    st.subheader("Workout Program Tracker")

    prog_data = load_program()
    prog_list = prog_data.get("program", [])
    current_index = prog_data.get("current_index", 0)

    # Display current routine
    if prog_list:
        current_day = prog_list[current_index % len(prog_list)]
        st.markdown(f"### 📅 Today: **{current_day}**")

        if st.button("✅ Log Today’s Workout"):
            exercises = template_workouts.get(current_day)
            if exercises:
                for entry in exercises:
                    logger.log_workout(**entry)
                st.success(f"✅ Logged: {current_day}")
            else:
                st.error("❌ Template not found.")

        if st.button("➡️ Next Workout Day"):
            prog_data["current_index"] = (current_index + 1) % len(prog_list)
            save_program(prog_data)
            st.rerun()

    else:
        st.info("No program set. Add days below.")

    # Custom program editor
    st.divider()
    st.subheader("🧠 Customize Program Cycle")

    new_program = st.multiselect(
        "Choose days (order matters):",
        options=list(template_workouts.keys()),
        default=prog_list
    )

    if st.button("💾 Save Program"):
        save_program({"program": new_program, "current_index": 0})
        st.success("✅ Program saved!")
        st.rerun()

if __name__ == "__main__":
    import streamlit.web.cli as stcli
    import sys
    sys.argv = ["streamlit", "run", "ui/streamlit_app.py"]
    sys.exit(stcli.main())