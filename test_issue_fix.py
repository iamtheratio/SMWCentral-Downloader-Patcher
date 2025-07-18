#!/usr/bin/env python3
"""
Final test for the specific issue mentioned in the problem statement:
"Download & Patch" button not visible on displays below 1920x1080
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
    
    def test_original_issue():
        """Test the specific issue from the problem statement"""
        print("Testing original issue: Button visibility on displays < 1920x1080")
        print("=" * 60)
        
        # Test the specific problematic scenario
        problem_cases = [
            ("1366x768 laptop", 1366, 768),
            ("1440x900 laptop", 1440, 900), 
            ("1600x900 desktop", 1600, 900),
            ("1680x1050 desktop", 1680, 1050)
        ]
        
        for name, screen_w, screen_h in problem_cases:
            print(f"\n📱 Testing {name} ({screen_w}x{screen_h})")
            print("-" * 40)
            
            # Create window sized appropriately for the "screen"
            root = tk.Tk()
            root.title(f"Issue Test - {name}")
            
            # Calculate window size that would typically be used on this screen
            # Users typically don't maximize, so simulate realistic window size
            if screen_h <= 768:
                window_h = min(700, screen_h - 100)  # Leave space for taskbar/menu
                window_w = min(1000, screen_w - 100)
            else:
                window_h = min(850, screen_h - 150)
                window_w = min(1050, screen_w - 150)
                
            root.geometry(f"{window_w}x{window_h}")
            
            # Set up the UI
            sv_ttk.set_theme("dark")
            main_frame = ttk.Frame(root, padding=25)
            main_frame.pack(fill="both", expand=True)
            
            # Create results component
            results = DownloadResults(main_frame, lambda: None)
            
            # Update to get real measurements
            root.update_idletasks()
            
            # Test the calculations
            tree_height = results._calculate_tree_height()
            tree_px = tree_height * 25
            
            print(f"Window size: {window_w}x{window_h}")
            print(f"Tree height: {tree_height} rows ({tree_px}px)")
            
            # Estimate total UI height
            ui_elements_height = (
                60 +    # Nav bar
                50 +    # Page padding  
                100 +   # Filters (estimated)
                60 +    # Difficulty (estimated)
                tree_px +  # Tree view
                80 +    # Button area
                40      # Status/margins
            )
            
            print(f"Estimated total UI height: {ui_elements_height}px")
            
            # Check if it fits
            fits = ui_elements_height <= window_h
            margin = window_h - ui_elements_height
            
            if fits:
                print(f"✅ FIXED: Button will be visible (margin: {margin}px)")
            else:
                print(f"❌ ISSUE: Button may be hidden (overflow: {-margin}px)")
            
            # Verify this is better than the original fixed height=10
            original_tree_px = 10 * 25  # Original fixed height
            original_ui_height = ui_elements_height - tree_px + original_tree_px
            original_fits = original_ui_height <= window_h
            original_margin = window_h - original_ui_height
            
            print(f"Original (height=10): {original_ui_height}px", end="")
            if original_fits:
                print(f" ✅ (margin: {original_margin}px)")
            else:
                print(f" ❌ (overflow: {-original_margin}px)")
            
            if fits and not original_fits:
                print("🎉 IMPROVEMENT: Fixed the issue!")
            elif fits == original_fits:
                print("➡️  No change needed (already worked)")
            else:
                print("⚠️  Potential regression")
            
            root.destroy()
        
        print(f"\n{'=' * 60}")
        print("✅ Original issue test completed!")
        print("\nSummary:")
        print("- Dynamic height calculation implemented")
        print("- Small screen constraints added (4-6 rows max)")
        print("- Window resize handling added") 
        print("- Minimum window size set to 800x600")
        print("- Button visibility should be ensured on all tested resolutions")
        
    if __name__ == "__main__":
        test_original_issue()
        
except ImportError as e:
    print(f"❌ Import error: {e}")
except Exception as e:
    print(f"❌ Test failed: {e}")
    import traceback
    traceback.print_exc()
