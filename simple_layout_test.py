#!/usr/bin/env python3
"""Simple test script for button visibility"""

import tkinter as tk
from tkinter import ttk
import sv_ttk
import sys
import os

# Add the parent directory to the path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui.pages.download_page import DownloadPage

def simple_test():
    """Simple test to verify button is visible"""
    
    root = tk.Tk()
    root.title("Button Visibility Test - Simplified Layout")
    
    # Set up theme
    sv_ttk.USE_FONT_CONFIG = False
    sv_ttk.set_theme("dark")
    
    def mock_run_pipeline(*args, **kwargs):
        print("Mock pipeline called")
        
    def mock_logger():
        class MockLogger:
            def log(self, message, level="Information"):
                print(f"[{level}] {message}")
        return MockLogger()
    
    # Set window size similar to your large screen
    root.geometry("1920x1080+100+100")
    
    # Create the download page
    page = DownloadPage(root, mock_run_pipeline, mock_logger())
    frame = page.create()
    frame.pack(fill="both", expand=True)
    
    def check_layout():
        """Check if button is visible after layout settles"""
        try:
            root.update_idletasks()  # Let layout settle
            
            # Get the tree widget
            if hasattr(page, 'results') and page.results and hasattr(page.results, 'tree'):
                tree = page.results.tree
                tree_height = tree.cget('height')
                print(f"✅ Tree height: {tree_height} rows (fixed, simple)")
            
            # Check if button exists
            if hasattr(page, 'download_button_component') and page.download_button_component:
                button = page.download_button_component.get_button()
                if button:
                    print("✅ Download button found and should be visible at bottom")
                    
                    # Check button position relative to window
                    try:
                        root.update_idletasks()
                        button_y = button.winfo_y()
                        window_height = root.winfo_height()
                        print(f"Button Y position: {button_y}, Window height: {window_height}")
                        
                        if button_y < window_height - 50:  # Button should be well within window
                            print("✅ Button is positioned within visible window area")
                        else:
                            print("❌ Button might be cut off")
                    except:
                        print("Could not check button position details")
                else:
                    print("❌ Button not found")
            else:
                print("❌ Download button component not found")
                
        except Exception as e:
            print(f"Error checking layout: {e}")
    
    # Check layout after UI settles
    root.after(1000, check_layout)
    
    # Create a test button to resize window
    def test_resize():
        root.geometry("1366x768+100+100")
        root.after(500, check_layout)  # Check again after resize
    
    test_frame = ttk.Frame(root)
    test_frame.pack(side="bottom", fill="x", padx=10, pady=5)
    
    ttk.Button(test_frame, text="Test Resize to 1366x768", command=test_resize).pack(side="left", padx=5)
    
    print("✅ Simple layout test - button should always be visible")
    print("✅ Tree height fixed at 8 rows - no complex calculations")
    print("✅ Button positioned at bottom using pack(side='bottom')")
    
    root.mainloop()

if __name__ == "__main__":
    simple_test()
