#!/usr/bin/env python3
"""
Test script for v3.1 Time to Beat functionality
"""
import sys
import os

# Add path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_time_parsing():
    """Test the time parsing functionality"""
    # Import and create a real instance
    from ui.pages.hack_history_page import HackHistoryPage
    
    # Create a mock data manager and logger
    class MockDataManager:
        pass
    
    class MockLogger:
        def log(self, message, level="info"):
            pass
    
    # Create a real page instance to test with
    import tkinter as tk
    root = tk.Tk()
    root.withdraw()  # Hide the window
    
    try:
        page = HackHistoryPage(root, MockLogger())
        page.data_manager = MockDataManager()
        
        # Test cases for time parsing
        test_cases = [
            # (input, expected_seconds)
            ("2h 30m", 9000),      # 2*3600 + 30*60 = 9000
            ("90m", 5400),         # 90*60 = 5400
            ("1:30:45", 5445),     # 1*3600 + 30*60 + 45 = 5445
            ("25:30", 1530),       # 25*60 + 30 = 1530
            ("120", 7200),         # 120*60 = 7200 (assume minutes)
            ("150 minutes", 9000), # 150*60 = 9000
            ("2h", 7200),          # 2*3600 = 7200
            ("30s", 30),           # 30 seconds
            ("", 0),               # Empty string
        ]
        
        print("Testing time parsing...")
        for input_str, expected in test_cases:
            try:
                result = page._parse_time_input(input_str)
                if result == expected:
                    print(f"✅ '{input_str}' -> {result}s (expected {expected}s)")
                else:
                    print(f"❌ '{input_str}' -> {result}s (expected {expected}s)")
            except Exception as e:
                print(f"❌ '{input_str}' -> ERROR: {e}")
        
        # Test time formatting
        print("\nTesting time formatting...")
        format_cases = [
            (0, ""),           # 0 seconds = empty
            (30, "00:30"),     # 30 seconds = 00:30
            (90, "01:30"),     # 90 seconds = 01:30
            (3661, "01:01:01"), # 1 hour 1 minute 1 second
            (7200, "02:00:00"), # 2 hours exactly
        ]
        
        for seconds, expected in format_cases:
            result = page._format_time_display(seconds)
            if result == expected:
                print(f"✅ {seconds}s -> '{result}' (expected '{expected}')")
            else:
                print(f"❌ {seconds}s -> '{result}' (expected '{expected}')")
                
    finally:
        root.destroy()

if __name__ == "__main__":
    test_time_parsing()
    print("\nTime to Beat functionality test completed!")
