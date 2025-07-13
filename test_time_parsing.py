#!/usr/bin/env python3
"""Test the enhanced time parsing functionality"""

import re

def test_parse_time_input(time_str):
    """Parse user time input and convert to seconds - TEST VERSION"""
    if not time_str or time_str.strip() == "":
        return 0
    
    time_str = time_str.strip()
    
    # NEW: Pattern for flexible shortened formats with days
    # "14d 10" -> 14 days, 10 hours, 0 minutes, 0 seconds
    # "14d 10h 2" -> 14 days, 10 hours, 2 minutes, 0 seconds  
    # "14d 10h 2m 1" -> 14 days, 10 hours, 2 minutes, 1 second
    pattern_flexible = re.match(r'(?:(\d+)d\s*)?(?:(\d+)h?\s*)?(?:(\d+)m?\s*)?(?:(\d+)s?\s*)?$', time_str.lower())
    if pattern_flexible and any(pattern_flexible.groups()):
        days = int(pattern_flexible.group(1) or 0)
        hours = int(pattern_flexible.group(2) or 0)
        minutes = int(pattern_flexible.group(3) or 0) 
        seconds = int(pattern_flexible.group(4) or 0)
        
        # If there's a 'd' in the input, treat it as the day format
        if 'd' in time_str.lower():
            return days * 86400 + hours * 3600 + minutes * 60 + seconds
        
        # If no 'd', check for standard letter suffixes
        if re.search(r'[hms]', time_str.lower()):
            return hours * 3600 + minutes * 60 + seconds
    
    # Pattern for "2h 30m 15s" or "2h 30m" or "90m" etc. - must have letter suffix
    pattern_units = re.match(r'(?:(\d+)h\s*)?(?:(\d+)m\s*)?(?:(\d+)s\s*)?$', time_str.lower())
    if pattern_units and any(pattern_units.groups()) and re.search(r'[hms]', time_str.lower()):
        hours = int(pattern_units.group(1) or 0)
        minutes = int(pattern_units.group(2) or 0) 
        seconds = int(pattern_units.group(3) or 0)
        return hours * 3600 + minutes * 60 + seconds
    
    # Just a number - assume minutes
    if time_str.isdigit():
        return int(time_str) * 60
    
    raise ValueError(f"Invalid time format: {time_str}")

def format_seconds(seconds):
    """Convert seconds back to readable format for verification"""
    days = seconds // 86400
    hours = (seconds % 86400) // 3600
    mins = (seconds % 3600) // 60
    secs = seconds % 60
    
    parts = []
    if days > 0:
        parts.append(f"{days}d")
    if hours > 0:
        parts.append(f"{hours}h")
    if mins > 0:
        parts.append(f"{mins}m")
    if secs > 0:
        parts.append(f"{secs}s")
    
    return " ".join(parts) if parts else "0s"

# Test the new formats
test_cases = [
    "14d 10",           # 14 days, 10 hours -> 1,242,000 seconds
    "14d 10h 2",        # 14 days, 10 hours, 2 minutes -> 1,242,120 seconds  
    "14d 10h 2m 1",     # 14 days, 10 hours, 2 minutes, 1 second -> 1,242,121 seconds
    "1h 30m",           # Traditional format still works
    "90",               # Just minutes
    "2h 30m 15s",       # Full traditional format
]

print("Testing enhanced time parsing:")
print("=" * 50)

for test_input in test_cases:
    try:
        result_seconds = test_parse_time_input(test_input)
        formatted = format_seconds(result_seconds)
        print(f"'{test_input}' -> {result_seconds} seconds ({formatted})")
    except ValueError as e:
        print(f"'{test_input}' -> ERROR: {e}")

print("\nExpected results:")
print("14d 10 -> 14 days, 10 hours = 1,242,000 seconds")
print("14d 10h 2 -> 14 days, 10 hours, 2 minutes = 1,242,120 seconds")
print("14d 10h 2m 1 -> 14 days, 10 hours, 2 minutes, 1 second = 1,242,121 seconds")
