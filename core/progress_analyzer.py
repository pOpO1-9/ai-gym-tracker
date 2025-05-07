import pandas as pd

class ProgressAnalyzer:
    def __init__(self, raw_logs):
        self.df = pd.DataFrame(raw_logs, columns=["id", "date", "exercise", "sets", "reps", "weight"])
        self.df["volume"] = self.df["sets"] * self.df["reps"] * self.df["weight"]

    def get_total_volume_by_exercise(self):
        return self.df.groupby("exercise")["volume"].sum().sort_values(ascending=False)

    def get_recent_sessions(self, n=5):
        return self.df.head(n)

    def get_prs(self):
        return self.df.groupby("exercise")["weight"].max().sort_values(ascending=False)
