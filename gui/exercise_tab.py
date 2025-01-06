# gui/exercise_tab.py

import tkinter as tk
from tkinter import ttk, messagebox

class ExerciseTab(ttk.Frame):
    def __init__(self, parent, db):
        super().__init__(parent)
        self.db = db
        self.create_widgets()
        self.load_data()

    def create_widgets(self):
        # Frame for form inputs
        form_frame = ttk.LabelFrame(self, text="Add / Update Exercise")
        form_frame.pack(fill='x', padx=10, pady=10)

        ttk.Label(form_frame, text="Exercise Name:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.name_entry = ttk.Entry(form_frame)
        self.name_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(form_frame, text="Type:").grid(row=1, column=0, padx=5, pady=5, sticky='e')
        self.type_entry = ttk.Entry(form_frame)
        self.type_entry.grid(row=1, column=1, padx=5, pady=5)

        self.add_button = ttk.Button(form_frame, text="Add Exercise", command=self.add_exercise)
        self.add_button.grid(row=2, column=0, columnspan=2, pady=10)

        # Treeview for displaying exercises
        self.tree = ttk.Treeview(self, columns=('Name', 'Type'), show='headings')
        self.tree.heading('Name', text='Name')
        self.tree.heading('Type', text='Type')
        self.tree.pack(fill='both', expand=True, padx=10, pady=10)

        # Buttons for Update and Delete
        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=5)

        self.update_button = ttk.Button(btn_frame, text="Update Selected", command=self.update_exercise)
        self.update_button.pack(side='left', padx=5)

        self.delete_button = ttk.Button(btn_frame, text="Delete Selected", command=self.delete_exercise)
        self.delete_button.pack(side='left', padx=5)

    def load_data(self):
        exercises = self.db.get_all_exercises()
        self.refresh_treeview(exercises)

    def refresh_treeview(self, exercises):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for name, type_ in exercises:
            self.tree.insert('', 'end', values=(name, type_))

    def add_exercise(self):
        name = self.name_entry.get().strip()
        type_ = self.type_entry.get().strip()

        if not name or not type_:
            messagebox.showwarning("Input Error", "Please fill out all fields.")
            return

        success = self.db.add_exercise(name, type_)
        if success:
            self.load_data()
            self.clear_form()
        else:
            messagebox.showwarning("Duplicate Entry", "Exercise already exists.")

    def update_exercise(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selection Error", "Please select an exercise to update.")
            return

        selected_item = self.tree.item(selected[0])
        old_name, old_type = selected_item['values']

        # Pop-up window for updating
        update_window = tk.Toplevel(self)
        update_window.title("Update Exercise")

        ttk.Label(update_window, text="Exercise Name:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        name_entry = ttk.Entry(update_window)
        name_entry.grid(row=0, column=1, padx=5, pady=5)
        name_entry.insert(0, old_name)

        ttk.Label(update_window, text="Type:").grid(row=1, column=0, padx=5, pady=5, sticky='e')
        type_entry = ttk.Entry(update_window)
        type_entry.grid(row=1, column=1, padx=5, pady=5)
        type_entry.insert(0, old_type)

        def save_updates():
            new_name = name_entry.get().strip()
            new_type = type_entry.get().strip()

            if not new_name or not new_type:
                messagebox.showwarning("Input Error", "Please fill out all fields.")
                return

            success = self.db.update_exercise(old_name, new_name, new_type)
            if success:
                self.load_data()
                update_window.destroy()
            else:
                messagebox.showwarning("Duplicate Entry", "Exercise name already exists.")

        save_button = ttk.Button(update_window, text="Save", command=save_updates)
        save_button.grid(row=2, column=0, columnspan=2, pady=10)

    def delete_exercise(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selection Error", "Please select an exercise to delete.")
            return

        selected_item = self.tree.item(selected[0])
        name = selected_item['values'][0]

        confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{name}'?")
        if confirm:
            success = self.db.delete_exercise(name)
            if success:
                self.load_data()
            else:
                messagebox.showwarning("Error", "Failed to delete exercise.")

    def clear_form(self):
        self.name_entry.delete(0, tk.END)
        self.type_entry.delete(0, tk.END)
