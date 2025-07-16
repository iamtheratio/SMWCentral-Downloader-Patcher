import tkinter as tk
from tkinter import ttk
import sv_ttk
from colors import get_colors

class ThemeControls:
    """Handles theme toggle and related UI elements"""
    
    def __init__(self, root, toggle_callback):
        self.root = root
        self.toggle_callback = toggle_callback
        self.theme_frame = None
        self.theme_switch = None
        self.moon_label = None
    
    def create(self):
        """Create theme toggle controls"""
        self.theme_frame = ttk.Frame(self.root)
        self.theme_frame.place(relx=1.0, rely=0.0, anchor="ne", x=-10, y=10)
        
        self.theme_switch = ttk.Checkbutton(
            self.theme_frame,
            style="Switch.TCheckbutton",
            command=lambda: self.toggle_callback(self.root)
        )
        self.theme_switch.pack(side="left")
        self.theme_switch.state(['selected'] if sv_ttk.get_theme() == "dark" else [])
        
        self.moon_label = ttk.Label(
            self.theme_frame, 
            text="🌙",
            font=("Segoe UI Emoji", 12),
        )
        self.moon_label.pack(side="left", padx=(2, 5))
        
        # Store references
        self.root.theme_switch = self.theme_switch
        self.root.moon_label = self.moon_label
        
        self.theme_frame.lift()
    
    def lift(self):
        """Bring theme controls to front"""
        if self.theme_frame:
            self.theme_frame.lift()
