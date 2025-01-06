# main.py

import tkinter as tk
from tkinter import ttk
import os
from utils.database import Database

from gui.exercise_tab import ExerciseTab
from gui.pr_tab import PRTab
from gui.workout_log_tab import WorkoutLogTab
from gui.progress_charts_tab import ProgressChartsTab

# Define paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
DB_FILE = os.path.join(DATA_DIR, 'workout_tracker.db')

def init_db():
    os.makedirs(DATA_DIR, exist_ok=True)
    db = Database(DB_FILE)
    db.close()  # Close immediately; tabs will manage connections as needed

def main():
    init_db()
    
    # Initialize the database instance
    db = Database(DB_FILE)
    
    root = tk.Tk()
    root.title("Workout Tracker")
    root.geometry("800x600")

    notebook = ttk.Notebook(root)
    notebook.pack(expand=True, fill='both')

    # Pass the database instance to each tab
    exercise_tab = ExerciseTab(notebook, db)
    pr_tab = PRTab(notebook, db)
    workout_log_tab = WorkoutLogTab(notebook, db)
    progress_charts_tab = ProgressChartsTab(notebook, db)

    notebook.add(exercise_tab, text='Exercises')
    notebook.add(pr_tab, text='Personal Records (PR)')
    notebook.add(workout_log_tab, text='Workout Log')
    notebook.add(progress_charts_tab, text='Progress Charts')

    root.mainloop()

    # Close the database connection when the app closes
    db.close()

if __name__ == "__main__":
    main()
