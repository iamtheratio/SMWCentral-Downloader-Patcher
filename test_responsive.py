#!/usr/bin/env python3
"""
Test script to verify responsive layout functionality
"""

import sys
import os
import tkinter as tk
from tkinter import ttk

# Add path for imports
sys.path.append(os.path.dirname(__file__))

try:
    from ui.download_components import DownloadResults
    import sv_ttk
    
    def test_responsive_layout():
        """Test the responsive layout functionality"""
        print("Testing responsive layout...")
        
        # Create a test window
        root = tk.Tk()
        root.title("Responsive Layout Test")
        root.geometry("800x600")  # Small window to test responsive behavior
        
        # Set up theme
        sv_ttk.set_theme("dark")
        
        # Create a test frame
        main_frame = ttk.Frame(root, padding=25)
        main_frame.pack(fill="both", expand=True)
        
        # Create DownloadResults component
        def dummy_callback():
            pass
            
        results = DownloadResults(main_frame, dummy_callback)
        
        # Test the height calculation
        height = results._calculate_tree_height()
        print(f"Calculated tree height for 800x600 window: {height} rows")
        
        # Test with different window sizes
        for width, height_px in [(800, 600), (1024, 768), (1920, 1080)]:
            root.geometry(f"{width}x{height_px}")
            root.update_idletasks()
            calculated_height = results._calculate_tree_height()
            print(f"Window {width}x{height_px}: Tree height = {calculated_height} rows")
        
        print("✅ Responsive layout test completed successfully!")
        root.destroy()
        
    if __name__ == "__main__":
        test_responsive_layout()
        
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure all required dependencies are installed.")
except Exception as e:
    print(f"❌ Test failed: {e}")
