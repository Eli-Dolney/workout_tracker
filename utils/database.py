# utils/database.py

import sqlite3
import os

class Database:
    def __init__(self, db_path):
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        self.connect()
        self.initialize_db()

    def connect(self):
        """Establish a connection to the SQLite database."""
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        self.cursor.execute("PRAGMA foreign_keys = ON;")  # Enable foreign key support

    def initialize_db(self):
        """Create necessary tables if they don't exist."""
        # Create 'exercises' table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS exercises (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                type TEXT NOT NULL
            )
        ''')

        # Create 'pr_records' table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS pr_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                exercise_id INTEGER,
                max_lift REAL,
                FOREIGN KEY(exercise_id) REFERENCES exercises(id) ON DELETE CASCADE
            )
        ''')

        # Create 'workout_logs' table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS workout_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                exercise_id INTEGER,
                duration REAL,
                calories REAL,
                FOREIGN KEY(exercise_id) REFERENCES exercises(id) ON DELETE CASCADE
            )
        ''')

        self.conn.commit()

    def close(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()

    # --- CRUD Operations for Exercises ---

    def add_exercise(self, name, type_):
        """Add a new exercise."""
        try:
            self.cursor.execute("INSERT INTO exercises (name, type) VALUES (?, ?)", (name, type_))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False  # Exercise already exists

    def update_exercise(self, old_name, new_name, new_type):
        """Update an existing exercise."""
        try:
            self.cursor.execute("UPDATE exercises SET name = ?, type = ? WHERE name = ?", (new_name, new_type, old_name))
            self.conn.commit()
            return self.cursor.rowcount > 0
        except sqlite3.IntegrityError:
            return False  # New exercise name already exists

    def delete_exercise(self, name):
        """Delete an exercise."""
        self.cursor.execute("DELETE FROM exercises WHERE name = ?", (name,))
        self.conn.commit()
        return self.cursor.rowcount > 0

    def get_all_exercises(self):
        """Retrieve all exercises."""
        self.cursor.execute("SELECT name, type FROM exercises")
        return self.cursor.fetchall()

    def get_exercise_id(self, name):
        """Get the ID of an exercise by name."""
        self.cursor.execute("SELECT id FROM exercises WHERE name = ?", (name,))
        result = self.cursor.fetchone()
        return result[0] if result else None

    # --- CRUD Operations for PR Records ---

    def add_or_update_pr(self, exercise_id, max_lift):
        """Add or update a personal record."""
        self.cursor.execute("SELECT id FROM pr_records WHERE exercise_id = ?", (exercise_id,))
        result = self.cursor.fetchone()
        if result:
            self.cursor.execute("UPDATE pr_records SET max_lift = ? WHERE exercise_id = ?", (max_lift, exercise_id))
        else:
            self.cursor.execute("INSERT INTO pr_records (exercise_id, max_lift) VALUES (?, ?)", (exercise_id, max_lift))
        self.conn.commit()

    def delete_pr(self, exercise_id):
        """Delete a personal record."""
        self.cursor.execute("DELETE FROM pr_records WHERE exercise_id = ?", (exercise_id,))
        self.conn.commit()

    def get_all_prs(self):
        """Retrieve all personal records."""
        self.cursor.execute('''
            SELECT exercises.name, pr_records.max_lift
            FROM pr_records
            JOIN exercises ON pr_records.exercise_id = exercises.id
        ''')
        return self.cursor.fetchall()

    # --- CRUD Operations for Workout Logs ---

    def add_workout_log(self, date, exercise_id, duration, calories):
        """Add a new workout log."""
        self.cursor.execute('''
            INSERT INTO workout_logs (date, exercise_id, duration, calories)
            VALUES (?, ?, ?, ?)
        ''', (date, exercise_id, duration, calories))
        self.conn.commit()

    def update_workout_log(self, log_id, date, exercise_id, duration, calories):
        """Update an existing workout log."""
        self.cursor.execute('''
            UPDATE workout_logs
            SET date = ?, exercise_id = ?, duration = ?, calories = ?
            WHERE id = ?
        ''', (date, exercise_id, duration, calories, log_id))
        self.conn.commit()
        return self.cursor.rowcount > 0

    def delete_workout_log(self, log_id):
        """Delete a workout log."""
        self.cursor.execute("DELETE FROM workout_logs WHERE id = ?", (log_id,))
        self.conn.commit()
        return self.cursor.rowcount > 0

    def get_all_workout_logs(self):
        """Retrieve all workout logs."""
        self.cursor.execute('''
            SELECT workout_logs.id, workout_logs.date, exercises.name, workout_logs.duration, workout_logs.calories
            FROM workout_logs
            JOIN exercises ON workout_logs.exercise_id = exercises.id
            ORDER BY workout_logs.date DESC
        ''')
        return self.cursor.fetchall()

    def get_pr_data(self):
        """Retrieve data for personal records chart."""
        self.cursor.execute('''
            SELECT exercises.name, pr_records.max_lift
            FROM pr_records
            JOIN exercises ON pr_records.exercise_id = exercises.id
        ''')
        return self.cursor.fetchall()

    def get_calories_over_time(self):
        """Retrieve calories burned over time for charting."""
        self.cursor.execute('''
            SELECT date, SUM(calories) as total_calories
            FROM workout_logs
            GROUP BY date
            ORDER BY date ASC
        ''')
        return self.cursor.fetchall()
