from datetime import datetime, timedelta
import pandas as pd


class AICoach:
    def __init__(self, df):
        self.df = df.copy()
        self.df["date"] = pd.to_datetime(self.df["date"])
        self.df["volume"] = self.df["sets"] * self.df["reps"] * self.df["weight"]

    def detect_plateaus(self, days=21):
        recent = self.df[self.df["date"] >= datetime.now() - timedelta(days=days)]
        pr_now = recent.groupby("exercise")["weight"].max()
        pr_all = self.df.groupby("exercise")["weight"].max()

        plateaus = []
        for exercise in pr_all.index:
            if pr_now.get(exercise, 0) < pr_all[exercise]:
                plateaus.append(f"📉 Plateau on {exercise}: Recent PR lower than your all-time best.")
        return plateaus

    def detect_volume_drop(self, days=7):
        today = datetime.now().date()
        week_ago = today - timedelta(days=days)

        recent_volume = self.df[self.df["date"].dt.date > week_ago]["volume"].sum()
        past_volume = self.df[self.df["date"].dt.date <= week_ago]["volume"].sum()

        if past_volume == 0:
            return []

        drop_percent = 100 * (past_volume - recent_volume) / past_volume
        if drop_percent > 25:
            return [f"⚠️ Volume dropped {int(drop_percent)}% compared to your previous week."]
        return []

    def detect_neglected_muscles(self, muscle_groups):
        # Requires a predefined mapping: exercise → muscle group
        self.df["date"] = pd.to_datetime(self.df["date"])
        recent = self.df[self.df["date"] >= datetime.now() - timedelta(days=10)]

        neglected = []
        for group, exercises in muscle_groups.items():
            trained = recent["exercise"].isin(exercises).any()
            if not trained:
                neglected.append(f"🔻 You haven’t trained {group} in over 10 days.")
        return neglected

    def generate_report(self, muscle_groups):
        return (
                self.detect_plateaus() +
                self.detect_volume_drop() +
                self.detect_neglected_muscles(muscle_groups)
        )
