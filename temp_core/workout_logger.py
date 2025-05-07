import sqlite3
from datetime import datetime

class WorkoutLogger:
    def __init__(self, db_path="data/user_logs.db"):
        self.conn = sqlite3.connect(db_path)
        self.create_table()

    def create_table(self):
        query = """
        CREATE TABLE IF NOT EXISTS workouts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            exercise TEXT NOT NULL,
            sets INTEGER,
            reps INTEGER,
            weight REAL
        );
        """
        self.conn.execute(query)
        self.conn.commit()

    def log_workout(self, exercise, sets, reps, weight, date=None):
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")

        query = """
        INSERT INTO workouts (date, exercise, sets, reps, weight)
        VALUES (?, ?, ?, ?, ?);
        """
        self.conn.execute(query, (date, exercise, sets, reps, weight))
        self.conn.commit()

    def fetch_all_logs(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM workouts ORDER BY date DESC;")
        return cursor.fetchall()
