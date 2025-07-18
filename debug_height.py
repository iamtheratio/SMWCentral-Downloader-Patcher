#!/usr/bin/env python3
"""
Debug script to analyze tree height calculation
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
    
    def debug_height_calculation():
        """Debug the height calculation with detailed output"""
        print("Debugging tree height calculation...")
        
        # Create a test window
        root = tk.Tk()
        root.title("Height Calculation Debug")
        
        # Set up theme
        sv_ttk.set_theme("dark")
        
        # Create a test frame
        main_frame = ttk.Frame(root, padding=25)
        main_frame.pack(fill="both", expand=True)
        
        # Create DownloadResults component
        def dummy_callback():
            pass
            
        results = DownloadResults(main_frame, dummy_callback)
        
        # Test with different window sizes
        for width, height_px in [(800, 600), (1024, 768), (1366, 768), (1920, 1080)]:
            root.geometry(f"{width}x{height_px}")
            root.update_idletasks()
            
            # Get screen dimensions
            screen_width = root.winfo_screenwidth()
            screen_height = root.winfo_screenheight()
            window_height = root.winfo_height()
            
            print(f"\n--- Window {width}x{height_px} ---")
            print(f"Screen: {screen_width}x{screen_height}")
            print(f"Window height: {window_height}")
            
            # Check display type
            is_small_display = screen_height <= 768 or screen_width <= 1366
            is_medium_display = screen_height <= 1080
            
            print(f"Small display: {is_small_display}")
            print(f"Medium display: {is_medium_display}")
            
            # Calculate available space
            reserved_space = 60 + 50 + 160 + 80 + 80 + 60 + 40  # ~530px
            if is_small_display:
                reserved_space += 50
            
            available_height = max(150, window_height - reserved_space)
            row_height = 25
            calculated_height = available_height // row_height
            
            print(f"Reserved space: {reserved_space}px")
            print(f"Available height: {available_height}px")
            print(f"Raw calculated height: {calculated_height}")
            
            # Apply constraints
            if is_small_display:
                final_height = max(4, min(6, calculated_height))
            elif is_medium_display:
                final_height = max(6, min(10, calculated_height))
            else:
                final_height = max(8, min(15, calculated_height))
                
            print(f"Final height: {final_height} rows")
        
        print("\n✅ Debug completed!")
        root.destroy()
        
    if __name__ == "__main__":
        debug_height_calculation()
        
except ImportError as e:
    print(f"❌ Import error: {e}")
except Exception as e:
    print(f"❌ Debug failed: {e}")
    import traceback
    traceback.print_exc()
