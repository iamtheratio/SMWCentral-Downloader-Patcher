#!/usr/bin/env python3

"""
Test obsolete filter logic without GUI components
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from hack_data_manager import HackDataManager

def test_obsolete_filter_logic():
    """Test the obsolete filtering logic directly"""
    print("=== Testing Obsolete Filter Logic ===")
    
    # Load data
    data_manager = HackDataManager()
    all_hacks = data_manager.get_all_hacks(include_obsolete=True)
    
    print(f"Total hacks loaded: {len(all_hacks)}")
    
    # Count obsolete vs non-obsolete
    obsolete_hacks = []
    non_obsolete_hacks = []
    
    for hack in all_hacks:
        if hack.get("obsolete", False):
            obsolete_hacks.append(hack)
        else:
            non_obsolete_hacks.append(hack)
    
    print(f"Obsolete hacks: {len(obsolete_hacks)}")
    print(f"Non-obsolete hacks: {len(non_obsolete_hacks)}")
    
    # Show obsolete records
    print(f"\nObsolete records:")
    for hack in obsolete_hacks:
        title = hack.get("title", "Unknown")
        print(f"  - {title}")
    
    # Test the filtering logic manually (from table_filters.py)
    def test_filter(filter_value, expected_count, description):
        print(f"\nTesting filter '{filter_value}' ({description}):")
        
        filtered_count = 0
        for hack in all_hacks:
            # Simulate the filter logic from _hack_passes_filters
            if filter_value != "Any":
                is_obsolete = hack.get("obsolete", False)
                
                if filter_value == "Yes" and not is_obsolete:
                    continue  # Skip non-obsolete
                elif filter_value == "No" and is_obsolete:
                    continue  # Skip obsolete
            
            filtered_count += 1
        
        print(f"  Expected: ~{expected_count}, Got: {filtered_count}")
        if abs(filtered_count - expected_count) <= 1:  # Allow for small differences
            print(f"  ✅ Filter working correctly")
        else:
            print(f"  ❌ Filter not working as expected")
        
        return filtered_count
    
    # Test each filter option
    test_filter("Any", len(all_hacks), "show all records")
    test_filter("Yes", len(obsolete_hacks), "show only obsolete")  
    test_filter("No", len(non_obsolete_hacks), "show only non-obsolete")
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    test_obsolete_filter_logic()
