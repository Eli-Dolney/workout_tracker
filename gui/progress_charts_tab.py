# gui/progress_charts_tab.py

import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class ProgressChartsTab(ttk.Frame):
    def __init__(self, parent, db):
        super().__init__(parent)
        self.db = db
        self.create_widgets()
        self.load_data()

    def create_widgets(self):
        # Frame for chart type selection
        control_frame = ttk.Frame(self)
        control_frame.pack(fill='x', padx=10, pady=10)

        ttk.Label(control_frame, text="Select Chart Type:").pack(side='left', padx=5)

        self.chart_type = tk.StringVar(value="Bar")
        chart_options = ["Bar", "Line"]
        chart_menu = ttk.OptionMenu(control_frame, self.chart_type, chart_options[0], *chart_options, command=self.plot_chart)
        chart_menu.pack(side='left', padx=5)

        # Canvas for the chart
        self.figure = plt.Figure(figsize=(6,5), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, self)
        self.canvas.get_tk_widget().pack(fill='both', expand=True)

    def load_data(self):
        self.plot_chart()

    def plot_chart(self, _=None):
        self.ax.clear()
        prs = self.db.get_pr_data()

        if not prs:
            self.ax.text(0.5, 0.5, 'No PR Data Available', horizontalalignment='center', verticalalignment='center')
        else:
            exercises, max_lifts = zip(*prs)
            if self.chart_type.get() == "Bar":
                self.ax.bar(exercises, max_lifts, color='skyblue')
                self.ax.set_ylabel('Max Lift')
                self.ax.set_title('Personal Records')
            elif self.chart_type.get() == "Line":
                self.ax.plot(exercises, max_lifts, marker='o', linestyle='-', color='green')
                self.ax.set_ylabel('Max Lift')
                self.ax.set_title('Personal Records')

            self.ax.set_xlabel('Exercise')
            self.ax.tick_params(axis='x', rotation=45)

        self.figure.tight_layout()
        self.canvas.draw()
