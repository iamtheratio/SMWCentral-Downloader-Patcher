#!/usr/bin/env python3
"""
Test script to verify that dashboard theme toggle works correctly
"""
import tkinter as tk
from tkinter import ttk
import sv_ttk
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui.pages.dashboard_page import DashboardPage
from colors import get_colors

def test_theme_toggle():
    """Test that dashboard colors change when theme is toggled"""
    root = tk.Tk()
    root.title("Theme Toggle Test")
    root.geometry("800x600")
    
    # Set initial theme
    sv_ttk.set_theme("dark")
    
    # Create dashboard page
    dashboard = DashboardPage(root)
    dashboard_frame = dashboard.create()
    dashboard_frame.pack(fill="both", expand=True)
    
    def toggle_and_check():
        """Toggle theme and refresh dashboard"""
        print(f"Current theme: {sv_ttk.get_theme()}")
        print(f"Current colors: {get_colors()}")
        
        # Toggle theme
        sv_ttk.toggle_theme()
        
        print(f"New theme: {sv_ttk.get_theme()}")
        print(f"New colors: {get_colors()}")
        
        # Refresh dashboard (this should apply new colors)
        dashboard._refresh_dashboard()
        
        print("Dashboard refreshed with new theme!")
    
    # Add button to test toggle
    test_button = ttk.Button(root, text="Toggle Theme & Refresh", command=toggle_and_check)
    test_button.pack(pady=10)
    
    # Test initial colors
    print(f"Initial theme: {sv_ttk.get_theme()}")
    print(f"Initial colors: {get_colors()}")
    
    root.mainloop()

if __name__ == "__main__":
    test_theme_toggle()
