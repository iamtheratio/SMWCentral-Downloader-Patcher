#!/usr/bin/env python3
"""
Test the specific scenario where users might maximize or resize the window 
to be larger, causing the button to be pushed out of view
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
    
    def test_edge_cases():
        """Test edge cases where the button might get pushed out"""
        print("Testing edge cases for button visibility")
        print("=" * 50)
        
        # Test cases that might cause problems
        edge_cases = [
            ("Small window on large screen", 800, 600, 1920, 1080),
            ("Tall narrow window", 900, 1000, 1920, 1080), 
            ("Very small window", 800, 500, 1366, 768),
            ("Maximized on small screen", 1366, 728, 1366, 768),  # Full screen minus taskbar
        ]
        
        for name, win_w, win_h, screen_w, screen_h in edge_cases:
            print(f"\n🧪 Testing {name}")
            print(f"   Window: {win_w}x{win_h}, Screen: {screen_w}x{screen_h}")
            print("-" * 40)
            
            # Create test window
            root = tk.Tk()
            root.title(f"Edge Case Test - {name}")
            root.geometry(f"{win_w}x{win_h}")
            
            # Mock screen size if different
            if screen_w != root.winfo_screenwidth() or screen_h != root.winfo_screenheight():
                root.winfo_screenwidth = lambda: screen_w
                root.winfo_screenheight = lambda: screen_h
            
            # Set up UI
            sv_ttk.set_theme("dark")
            main_frame = ttk.Frame(root, padding=25)
            main_frame.pack(fill="both", expand=True)
            
            # Add some UI elements to simulate the real app
            # Filters section
            filters = ttk.LabelFrame(main_frame, text="Search Filters", padding=15)
            filters.pack(fill="x", pady=(0, 10))
            filter_content = ttk.Frame(filters)
            filter_content.pack(fill="x")
            for i in range(3):  # Simulate multiple rows of filters
                row = ttk.Frame(filter_content)
                row.pack(fill="x", pady=2)
                ttk.Label(row, text=f"Filter {i+1}:").pack(side="left")
                ttk.Entry(row, width=20).pack(side="left", padx=(5,0))
            
            # Difficulty section  
            difficulty = ttk.LabelFrame(main_frame, text="Difficulty", padding=15)
            difficulty.pack(fill="x", pady=(0, 10))
            diff_frame = ttk.Frame(difficulty)
            diff_frame.pack()
            for i in range(4):  # Simulate difficulty checkboxes
                ttk.Checkbutton(diff_frame, text=f"Difficulty {i+1}").pack(side="left", padx=5)
            
            # Results component
            results = DownloadResults(main_frame, lambda: None)
            
            # Download button area
            button_frame = ttk.Frame(main_frame)
            button_frame.pack(fill="x", pady=(10, 0))
            download_btn = ttk.Button(button_frame, text="Download & Patch", style="Large.Accent.TButton")
            download_btn.pack()
            
            # Update layout
            root.update_idletasks()
            
            # Get actual measurements
            tree_height = results._calculate_tree_height()
            
            # Check if button is visible by getting its position
            try:
                btn_y = download_btn.winfo_y() + download_btn.winfo_height()
                window_height = root.winfo_height()
                content_height = btn_y + 50  # Add some margin
                
                print(f"Tree height: {tree_height} rows")
                print(f"Button bottom position: {btn_y}px")
                print(f"Window height: {window_height}px")
                print(f"Required height: {content_height}px")
                
                if content_height <= window_height:
                    margin = window_height - content_height
                    print(f"✅ Button IS visible (margin: {margin}px)")
                else:
                    overflow = content_height - window_height
                    print(f"❌ Button MAY BE hidden (overflow: {overflow}px)")
                    
                    # This shouldn't happen with our fix
                    if overflow > 50:  # Significant overflow
                        print("🚨 POTENTIAL ISSUE: Significant overflow detected!")
                
            except Exception as e:
                print(f"⚠️  Could not measure button position: {e}")
                print(f"Tree height: {tree_height} rows (conservative estimate)")
            
            root.destroy()
        
        print(f"\n{'=' * 50}")
        print("✅ Edge case testing completed!")
        
    if __name__ == "__main__":
        test_edge_cases()
        
except ImportError as e:
    print(f"❌ Import error: {e}")
except Exception as e:
    print(f"❌ Test failed: {e}")
    import traceback
    traceback.print_exc()
