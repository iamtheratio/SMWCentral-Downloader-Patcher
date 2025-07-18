#!/usr/bin/env python3
"""Test the final layout fix"""

import tkinter as tk
from tkinter import ttk
import sv_ttk
import sys
import os

# Add the parent directory to the path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui.pages.download_page import DownloadPage

def test_final_layout():
    """Test the final layout with proper button positioning"""
    
    root = tk.Tk()
    root.title("Final Layout Test - Button Should Stay Visible")
    
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
    
    # Start with a normal window size
    root.geometry("1200x800+100+100")
    
    # Create the download page
    page = DownloadPage(root, mock_run_pipeline, mock_logger())
    frame = page.create()
    frame.pack(fill="both", expand=True)
    
    def check_button_visibility():
        """Check if button is visible"""
        try:
            root.update_idletasks()
            
            if hasattr(page, 'download_button_component') and page.download_button_component:
                button = page.download_button_component.get_button()
                if button:
                    button_y = button.winfo_y()
                    window_height = root.winfo_height()
                    
                    print(f"Button Y: {button_y}, Window height: {window_height}")
                    
                    if button_y < window_height - 50:
                        print("✅ Download button is visible")
                        return True
                    else:
                        print("❌ Download button is cut off")
                        return False
                else:
                    print("❌ Button widget not found")
                    return False
            else:
                print("❌ Download button component not found")
                return False
        except Exception as e:
            print(f"Error checking button: {e}")
            return False
    
    def test_resize_small():
        """Test resize to small window"""
        print("\n--- Testing resize to small window ---")
        root.geometry("900x600+100+100")
        root.after(500, lambda: check_button_visibility())
    
    def test_resize_large():
        """Test resize to large window"""
        print("\n--- Testing resize to large window ---")
        root.geometry("1600x1000+100+100")
        root.after(500, lambda: check_button_visibility())
    
    def test_resize_very_small():
        """Test resize to very small window"""
        print("\n--- Testing resize to very small window ---")
        root.geometry("800x500+100+100")
        root.after(500, lambda: check_button_visibility())
    
    # Create test controls
    test_frame = ttk.Frame(root)
    test_frame.pack(side="top", fill="x", padx=10, pady=5)
    
    ttk.Button(test_frame, text="Check Button", command=check_button_visibility).pack(side="left", padx=5)
    ttk.Button(test_frame, text="Resize Small", command=test_resize_small).pack(side="left", padx=5)
    ttk.Button(test_frame, text="Resize Large", command=test_resize_large).pack(side="left", padx=5)
    ttk.Button(test_frame, text="Resize Very Small", command=test_resize_very_small).pack(side="left", padx=5)
    
    # Initial check
    root.after(1000, check_button_visibility)
    
    print("✅ Layout Fix Applied:")
    print("  - Results frame: fill='x', expand=False")
    print("  - Button frame: pack(side='bottom')")
    print("  - Tree height: fixed at 8 rows")
    print("\nTest different window sizes to verify button stays visible")
    
    root.mainloop()

if __name__ == "__main__":
    test_final_layout()
