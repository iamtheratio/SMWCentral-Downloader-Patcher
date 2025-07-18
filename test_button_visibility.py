#!/usr/bin/env python3
"""
Comprehensive test for the responsive layout fix
Tests the specific issue: Download button visibility on screens < 1920x1080
"""

import sys
import os
import tkinter as tk
from tkinter import ttk

# Add path for imports
sys.path.append(os.path.dirname(__file__))

try:
    from ui.download_components import DownloadResults, DownloadButton
    import sv_ttk
    
    def test_button_visibility_fix():
        """Test that the download button remains visible on smaller screens"""
        print("Testing download button visibility fix...")
        
        # Test cases for different screen resolutions
        test_cases = [
            ("Small laptop", 1366, 768),
            ("Medium laptop", 1440, 900),
            ("Standard desktop", 1920, 1080),
            ("Large desktop", 2560, 1440)
        ]
        
        for name, width, height in test_cases:
            print(f"\n--- Testing {name} ({width}x{height}) ---")
            
            # Create a test window
            root = tk.Tk()
            root.title(f"Test - {name}")
            
            # Simulate the screen resolution by setting window size
            # We'll use a slightly smaller window than screen to simulate realistic usage
            window_width = min(width - 100, 1050)  # Leave some border
            window_height = min(height - 100, 900)  # Leave some border
            
            root.geometry(f"{window_width}x{window_height}")
            root.minsize(800, 600)
            
            # Mock the screen size for testing
            root.winfo_screenwidth = lambda: width
            root.winfo_screenheight = lambda: height
            
            # Set up theme
            sv_ttk.set_theme("dark")
            
            # Create main frame (simulating the download page layout)
            main_frame = ttk.Frame(root, padding=25)
            main_frame.pack(fill="both", expand=True)
            
            # Simulate the filters section
            filters_frame = ttk.LabelFrame(main_frame, text="Filters", padding=15)
            filters_frame.pack(fill="x", pady=(0, 10))
            ttk.Label(filters_frame, text="Search filters would go here...").pack(pady=20)
            
            # Simulate the difficulty section
            difficulty_frame = ttk.LabelFrame(main_frame, text="Difficulty", padding=15)
            difficulty_frame.pack(fill="x", pady=(0, 10))
            ttk.Label(difficulty_frame, text="Difficulty checkboxes would go here...").pack(pady=20)
            
            # Create DownloadResults component
            def dummy_callback():
                pass
                
            results = DownloadResults(main_frame, dummy_callback)
            
            # Create DownloadButton component
            download_button = DownloadButton(main_frame, dummy_callback)
            
            # Update window to get accurate measurements
            root.update_idletasks()
            
            # Test the height calculation
            calculated_height = results._calculate_tree_height()
            print(f"Tree height: {calculated_height} rows")
            
            # Calculate expected tree area height
            tree_area_height = calculated_height * 25  # 25px per row
            print(f"Tree area height: {tree_area_height}px")
            
            # Check if button would be visible
            total_content_height = (
                60 +  # Navigation
                50 +  # Page padding
                80 +  # Filters
                60 +  # Difficulty
                tree_area_height +  # Tree
                80 +  # Button area
                60    # Status and margins
            )
            
            print(f"Total content height: {total_content_height}px")
            print(f"Window height: {window_height}px")
            
            if total_content_height <= window_height:
                print("✅ Download button WILL be visible")
            else:
                print("❌ Download button MIGHT be hidden")
                overflow = total_content_height - window_height
                print(f"   Overflow: {overflow}px")
            
            # Test specific small screen behavior
            if height <= 768:
                expected_max_height = 6
                if calculated_height <= expected_max_height:
                    print("✅ Small screen height constraint working correctly")
                else:
                    print(f"❌ Small screen height too large: {calculated_height} > {expected_max_height}")
            
            root.destroy()
        
        print("\n✅ Button visibility test completed!")
        
    if __name__ == "__main__":
        test_button_visibility_fix()
        
except ImportError as e:
    print(f"❌ Import error: {e}")
except Exception as e:
    print(f"❌ Test failed: {e}")
    import traceback
    traceback.print_exc()
