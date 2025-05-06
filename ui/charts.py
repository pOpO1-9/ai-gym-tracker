import matplotlib.pyplot as plt
import pandas as pd

def plot_pr_chart(df):
    prs = df.groupby("exercise")["weight"].max().sort_values()
    plt.figure(figsize=(8, 5))
    prs.plot(kind="barh")
    plt.title("🏆 Personal Records by Exercise")
    plt.xlabel("Weight (kg)")
    plt.tight_layout()
    plt.show()

def plot_volume_over_time(df):
    df["date"] = pd.to_datetime(df["date"])
    df["volume"] = df["sets"] * df["reps"] * df["weight"]
    volume_by_day = df.groupby("date")["volume"].sum()

    plt.figure(figsize=(8, 4))
    volume_by_day.plot(marker="o")
    plt.title("📈 Volume Over Time")
    plt.ylabel("Total Volume")
    plt.xlabel("Date")
    plt.grid(True)
    plt.tight_layout()
    plt.show()
