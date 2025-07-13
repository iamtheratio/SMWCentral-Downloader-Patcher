#!/usr/bin/env python3
"""Test time validation function"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the hack history page to test validation
from ui.pages.hack_history_page import HackHistoryPage

def test_time_validation():
    """Test the time validation function"""
    
    # Create a mock page instance just for testing the validation method
    class MockPage:
        def _parse_time_input(self, time_str):
            # Copy the parse method logic for testing
            if not time_str or time_str.strip() == "":
                return 0
            
            time_str = time_str.strip()
            import re
            
            # Pattern for "2h 30m 15s" or "2h 30m" or "90m" etc.
            pattern_units = re.match(r'(?:(\d+)h\s*)?(?:(\d+)m\s*)?(?:(\d+)s\s*)?$', time_str.lower())
            if pattern_units and any(pattern_units.groups()) and re.search(r'[hms]', time_str.lower()):
                hours = int(pattern_units.group(1) or 0)
                minutes = int(pattern_units.group(2) or 0) 
                seconds = int(pattern_units.group(3) or 0)
                return hours * 3600 + minutes * 60 + seconds
            
            # Pattern for "150 minutes" or "90 mins"
            pattern_minutes = re.match(r'(\d+)\s*(?:minutes?|mins?)$', time_str.lower())
            if pattern_minutes:
                return int(pattern_minutes.group(1)) * 60
            
            # Pattern for "HH:MM:SS" or "MM:SS"
            if ':' in time_str:
                parts = time_str.split(':')
                try:
                    if len(parts) == 3:  # HH:MM:SS
                        hours, minutes, seconds = map(int, parts)
                        return hours * 3600 + minutes * 60 + seconds
                    elif len(parts) == 2:  # MM:SS
                        minutes, seconds = map(int, parts)
                        return minutes * 60 + seconds
                except ValueError:
                    pass
            
            # Just a number - assume minutes
            if time_str.isdigit():
                return int(time_str) * 60
            
            raise ValueError(f"Invalid time format: {time_str}")
        
        def _validate_time_input(self, time_str):
            try:
                seconds = self._parse_time_input(time_str)
                if seconds < 0:
                    print("❌ Validation failed: Time cannot be negative")
                    return None
                if seconds > 999 * 3600:
                    print("❌ Validation failed: Time cannot exceed 999 hours")
                    return None
                return seconds
            except ValueError as e:
                print(f"❌ Validation failed: {e}")
                return None
    
    mock = MockPage()
    
    # Test cases
    test_cases = [
        "2h 30m",      # Should return 9000 seconds
        "90m",         # Should return 5400 seconds  
        "1:30:45",     # Should return 5445 seconds
        "30:15",       # Should return 1815 seconds
        "120",         # Should return 7200 seconds (120 minutes)
        "",            # Should return 0
        "invalid",     # Should return None
        "-30m",        # Should return None (negative)
    ]
    
    print("🔍 Testing time validation:")
    print("="*50)
    
    for test_input in test_cases:
        result = mock._validate_time_input(test_input)
        if result is None:
            print(f"❌ '{test_input}' -> FAILED validation")
        else:
            print(f"✅ '{test_input}' -> {result} seconds")

if __name__ == "__main__":
    test_time_validation()
