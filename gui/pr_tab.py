# gui/pr_tab.py

import tkinter as tk
from tkinter import ttk, messagebox

class PRTab(ttk.Frame):
    def __init__(self, parent, db):
        super().__init__(parent)
        self.db = db
        self.create_widgets()
        self.load_data()

    def create_widgets(self):
        # Frame for form inputs
        form_frame = ttk.LabelFrame(self, text="Add / Update PR")
        form_frame.pack(fill='x', padx=10, pady=10)

        ttk.Label(form_frame, text="Exercise:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.exercise_combo = ttk.Combobox(form_frame, state="readonly")
        self.exercise_combo.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(form_frame, text="Max Lift (kg/lbs):").grid(row=1, column=0, padx=5, pady=5, sticky='e')
        self.max_lift_entry = ttk.Entry(form_frame)
        self.max_lift_entry.grid(row=1, column=1, padx=5, pady=5)

        self.add_button = ttk.Button(form_frame, text="Add/Update PR", command=self.add_update_pr)
        self.add_button.grid(row=2, column=0, columnspan=2, pady=10)

        # Treeview for displaying PRs
        self.tree = ttk.Treeview(self, columns=('Exercise', 'Max Lift'), show='headings')
        self.tree.heading('Exercise', text='Exercise')
        self.tree.heading('Max Lift', text='Max Lift')
        self.tree.pack(fill='both', expand=True, padx=10, pady=10)

        # Button to delete PR
        self.delete_button = ttk.Button(self, text="Delete Selected PR", command=self.delete_pr)
        self.delete_button.pack(pady=5)

    def load_data(self):
        self.exercise_combo['values'] = [exercise[0] for exercise in self.db.get_all_exercises()]
        prs = self.db.get_all_prs()
        self.refresh_treeview(prs)

    def refresh_treeview(self, prs):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for exercise, max_lift in prs:
            self.tree.insert('', 'end', values=(exercise, max_lift))

    def add_update_pr(self):
        exercise = self.exercise_combo.get()
        max_lift = self.max_lift_entry.get().strip()

        if not exercise or not max_lift:
            messagebox.showwarning("Input Error", "Please select an exercise and enter max lift.")
            return

        try:
            max_lift = float(max_lift)
        except ValueError:
            messagebox.showwarning("Input Error", "Max lift must be a number.")
            return

        exercise_id = self.db.get_exercise_id(exercise)
        if not exercise_id:
            messagebox.showwarning("Error", "Selected exercise does not exist.")
            return

        self.db.add_or_update_pr(exercise_id, max_lift)
        self.load_data()
        self.clear_form()

    def delete_pr(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selection Error", "Please select a PR to delete.")
            return

        selected_item = self.tree.item(selected[0])
        exercise = selected_item['values'][0]

        confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete PR for '{exercise}'?")
        if confirm:
            exercise_id = self.db.get_exercise_id(exercise)
            if exercise_id:
                self.db.delete_pr(exercise_id)
                self.load_data()

    def clear_form(self):
        self.exercise_combo.set('')
        self.max_lift_entry.delete(0, tk.END)
