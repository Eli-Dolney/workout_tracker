# gui/workout_log_tab.py

import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import Calendar
from datetime import datetime

class WorkoutLogTab(ttk.Frame):
    def __init__(self, parent, db):
        super().__init__(parent)
        self.db = db
        self.create_widgets()
        self.load_data()

    def create_widgets(self):
        # Frame for form inputs
        form_frame = ttk.LabelFrame(self, text="Add Workout")
        form_frame.pack(fill='x', padx=10, pady=10)

        # Date Selection
        ttk.Label(form_frame, text="Date:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.cal = Calendar(form_frame, selectmode='day')
        self.cal.grid(row=0, column=1, padx=5, pady=5)
        self.cal.selection_set(datetime.now().date())  # Corrected method

        # Exercise Selection
        ttk.Label(form_frame, text="Exercise:").grid(row=1, column=0, padx=5, pady=5, sticky='e')
        self.exercise_combo = ttk.Combobox(form_frame, state="readonly")
        self.exercise_combo.grid(row=1, column=1, padx=5, pady=5)

        # Duration
        ttk.Label(form_frame, text="Duration (minutes):").grid(row=2, column=0, padx=5, pady=5, sticky='e')
        self.duration_entry = ttk.Entry(form_frame)
        self.duration_entry.grid(row=2, column=1, padx=5, pady=5)

        # Calories Burned
        ttk.Label(form_frame, text="Calories Burned:").grid(row=3, column=0, padx=5, pady=5, sticky='e')
        self.calories_entry = ttk.Entry(form_frame)
        self.calories_entry.grid(row=3, column=1, padx=5, pady=5)

        # Add Button
        self.add_button = ttk.Button(form_frame, text="Add Workout", command=self.add_workout)
        self.add_button.grid(row=4, column=0, columnspan=2, pady=10)

        # Treeview for displaying workout logs
        self.tree = ttk.Treeview(self, columns=('ID', 'Date', 'Exercise', 'Duration', 'Calories'), show='headings')
        self.tree.heading('ID', text='ID')
        self.tree.heading('Date', text='Date')
        self.tree.heading('Exercise', text='Exercise')
        self.tree.heading('Duration', text='Duration (min)')
        self.tree.heading('Calories', text='Calories Burned')
        self.tree.pack(fill='both', expand=True, padx=10, pady=10)

        # Buttons for Update and Delete
        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=5)

        self.update_button = ttk.Button(btn_frame, text="Update Selected", command=self.update_workout)
        self.update_button.pack(side='left', padx=5)

        self.delete_button = ttk.Button(btn_frame, text="Delete Selected", command=self.delete_workout)
        self.delete_button.pack(side='left', padx=5)

    def load_data(self):
        self.exercise_combo['values'] = [exercise[0] for exercise in self.db.get_all_exercises()]
        workouts = self.db.get_all_workout_logs()
        self.refresh_treeview(workouts)

    def refresh_treeview(self, workouts):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for log in workouts:
            self.tree.insert('', 'end', values=log)

    def add_workout(self):
        date = self.cal.get_date()
        exercise = self.exercise_combo.get()
        duration = self.duration_entry.get().strip()
        calories = self.calories_entry.get().strip()

        if not exercise or not duration or not calories:
            messagebox.showwarning("Input Error", "Please fill out all fields.")
            return

        try:
            duration = float(duration)
            calories = float(calories)
        except ValueError:
            messagebox.showwarning("Input Error", "Duration and Calories must be numbers.")
            return

        exercise_id = self.db.get_exercise_id(exercise)
        if not exercise_id:
            messagebox.showwarning("Error", "Selected exercise does not exist.")
            return

        self.db.add_workout_log(date, exercise_id, duration, calories)
        self.load_data()
        self.clear_form()

    def update_workout(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selection Error", "Please select a workout to update.")
            return

        selected_item = self.tree.item(selected[0])
        log_id, date, exercise, duration, calories = selected_item['values']

        # Pop-up window for updating
        update_window = tk.Toplevel(self)
        update_window.title("Update Workout")

        ttk.Label(update_window, text="Date:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        cal = Calendar(update_window, selectmode='day')
        cal.grid(row=0, column=1, padx=5, pady=5)
        try:
            cal.set_date(datetime.strptime(date, '%m/%d/%Y').date())
        except ValueError:
            cal.set_date(datetime.now().date())

        ttk.Label(update_window, text="Exercise:").grid(row=1, column=0, padx=5, pady=5, sticky='e')
        exercise_combo = ttk.Combobox(update_window, state="readonly")
        exercise_combo['values'] = [ex[0] for ex in self.db.get_all_exercises()]
        exercise_combo.grid(row=1, column=1, padx=5, pady=5)
        exercise_combo.set(exercise)

        ttk.Label(update_window, text="Duration (minutes):").grid(row=2, column=0, padx=5, pady=5, sticky='e')
        duration_entry = ttk.Entry(update_window)
        duration_entry.grid(row=2, column=1, padx=5, pady=5)
        duration_entry.insert(0, duration)

        ttk.Label(update_window, text="Calories Burned:").grid(row=3, column=0, padx=5, pady=5, sticky='e')
        calories_entry = ttk.Entry(update_window)
        calories_entry.grid(row=3, column=1, padx=5, pady=5)
        calories_entry.insert(0, calories)

        def save_updates():
            new_date = cal.get_date()
            new_exercise = exercise_combo.get()
            new_duration = duration_entry.get().strip()
            new_calories = calories_entry.get().strip()

            if not new_exercise or not new_duration or not new_calories:
                messagebox.showwarning("Input Error", "Please fill out all fields.")
                return

            try:
                new_duration = float(new_duration)
                new_calories = float(new_calories)
            except ValueError:
                messagebox.showwarning("Input Error", "Duration and Calories must be numbers.")
                return

            new_exercise_id = self.db.get_exercise_id(new_exercise)
            if not new_exercise_id:
                messagebox.showwarning("Error", "Selected exercise does not exist.")
                return

            success = self.db.update_workout_log(log_id, new_date, new_exercise_id, new_duration, new_calories)
            if success:
                self.load_data()
                update_window.destroy()
            else:
                messagebox.showwarning("Error", "Failed to update workout.")

        save_button = ttk.Button(update_window, text="Save", command=save_updates)
        save_button.grid(row=4, column=0, columnspan=2, pady=10)

    def delete_workout(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selection Error", "Please select a workout to delete.")
            return

        selected_item = self.tree.item(selected[0])
        log_id = selected_item['values'][0]

        confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete this workout?")
        if confirm:
            success = self.db.delete_workout_log(log_id)
            if success:
                self.load_data()
            else:
                messagebox.showwarning("Error", "Failed to delete workout.")

    def clear_form(self):
        self.exercise_combo.set('')
        self.duration_entry.delete(0, tk.END)
        self.calories_entry.delete(0, tk.END)
        self.cal.set_date(datetime.now().date())
