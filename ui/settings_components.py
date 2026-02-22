import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
from colors import get_colors
from datetime import datetime
import sys
import os

# Add path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from ui_constants import get_labelframe_padding

# Move the existing SetupSection, FilterSection, DifficultySection here
# (Just copy the existing content from components.py)

class SetupSection:
    """Setup section with path controls"""
    def __init__(self, master):
        self.master = master
        self.frame = ttk.LabelFrame(master, text="Setup", padding=get_labelframe_padding())
        self.frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        # Source code path
        self.src_label = ttk.Label(self.frame, text="Source Code Path:")
        self.src_label.grid(row=0, column=0, sticky="w")
        self.src_entry = ttk.Entry(self.frame, width=50)
        self.src_entry.grid(row=0, column=1, padx=5, pady=5)
        self.src_button = ttk.Button(self.frame, text="Browse", command=self.browse_src)
        self.src_button.grid(row=0, column=2, padx=5, pady=5)

        # Output path
        self.out_label = ttk.Label(self.frame, text="Output Path:")
        self.out_label.grid(row=1, column=0, sticky="w")
        self.out_entry = ttk.Entry(self.frame, width=50)
        self.out_entry.grid(row=1, column=1, padx=5, pady=5)
        self.out_button = ttk.Button(self.frame, text="Browse", command=self.browse_out)
        self.out_button.grid(row=1, column=2, padx=5, pady=5)

        # Date selection
        self.date_label = ttk.Label(self.frame, text="Date:")
        self.date_label.grid(row=2, column=0, sticky="w")
        self.date_entry = ttk.Entry(self.frame, width=20)
        self.date_entry.grid(row=2, column=1, padx=5, pady=5)
        self.date_button = ttk.Button(self.frame, text="Today", command=self.set_today)
        self.date_button.grid(row=2, column=2, padx=5, pady=5)

    def browse_src(self):
        """Browse for source code path"""
        from platform_utils import pick_directory
        path = pick_directory(title="Select Source Code Path")
        if path:
            self.src_entry.delete(0, tk.END)
            self.src_entry.insert(0, path)

    def browse_out(self):
        """Browse for output path"""
        from platform_utils import pick_directory
        path = pick_directory(title="Select Output Path")
        if path:
            self.out_entry.delete(0, tk.END)
            self.out_entry.insert(0, path)

    def set_today(self):
        """Set date entry to today's date"""
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))

class FilterSection:
    """Filter section for hack type and options"""
    def __init__(self, master):
        self.master = master
        self.frame = ttk.LabelFrame(master, text="Filters", padding=get_labelframe_padding())
        self.frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

        # Hack type
        self.hacktype_label = ttk.Label(self.frame, text="Hack Type:")
        self.hacktype_label.grid(row=0, column=0, sticky="w")
        self.hacktype_combo = ttk.Combobox(self.frame, values=["Type1", "Type2", "Type3"], state="readonly")
        self.hacktype_combo.grid(row=0, column=1, padx=5, pady=5)

        # Options
        self.options_label = ttk.Label(self.frame, text="Options:")
        self.options_label.grid(row=1, column=0, sticky="w")
        self.options_entry = ttk.Entry(self.frame, width=50)
        self.options_entry.grid(row=1, column=1, padx=5, pady=5)

        # Apply filters button
        self.apply_button = ttk.Button(self.frame, text="Apply Filters", command=self.apply_filters)
        self.apply_button.grid(row=2, column=1, padx=5, pady=5, sticky="e")

    def apply_filters(self):
        """Apply the selected filters"""
        hack_type = self.hacktype_combo.get()
        options = self.options_entry.get()
        # Implement filter logic here
        print(f"Applying filters - Hack Type: {hack_type}, Options: {options}")

class DifficultySection:
    """Difficulty selection section"""
    def __init__(self, master):
        self.master = master
        self.frame = ttk.LabelFrame(master, text="Difficulty", padding=get_labelframe_padding())
        self.frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")

        # Difficulty level
        self.level_label = ttk.Label(self.frame, text="Level:")
        self.level_label.grid(row=0, column=0, sticky="w")
        self.level_scale = ttk.Scale(self.frame, from_=1, to=10, orient="horizontal")
        self.level_scale.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        # Show hints checkbox
        self.hints_var = tk.BooleanVar()
        self.hints_checkbox = ttk.Checkbutton(self.frame, text="Show Hints", variable=self.hints_var)
        self.hints_checkbox.grid(row=1, column=0, columnspan=2, sticky="w")

        # Difficulty presets
        self.preset_label = ttk.Label(self.frame, text="Presets:")
        self.preset_label.grid(row=2, column=0, sticky="w")
        self.preset_combo = ttk.Combobox(self.frame, values=["Easy", "Medium", "Hard"], state="readonly")
        self.preset_combo.grid(row=2, column=1, padx=5, pady=5)

        # Apply difficulty button
        self.apply_button = ttk.Button(self.frame, text="Apply Difficulty", command=self.apply_difficulty)
        self.apply_button.grid(row=3, column=1, padx=5, pady=5, sticky="e")

    def apply_difficulty(self):
        """Apply the selected difficulty settings"""
        level = self.level_scale.get()
        show_hints = self.hints_var.get()
        preset = self.preset_combo.get()
        # Implement difficulty logic here
        print(f"Applying difficulty - Level: {level}, Show Hints: {show_hints}, Preset: {preset}")
