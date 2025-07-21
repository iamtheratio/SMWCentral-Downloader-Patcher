#!/usr/bin/env python3

"""
Quick test to verify obsolete records filtering fix
"""

import sys
import os

# Add the project directory to the path
sys.path.append(os.path.dirname(__file__))

from hack_data_manager import HackDataManager
from ui.components.table_filters import TableFilters

def test_obsolete_filter():
    """Test that obsolete records are properly loaded and filtered"""
    print("=== Testing Obsolete Records Filter ===")
    
    # Initialize data manager
    data_manager = HackDataManager()
    
    # Test 1: Load all hacks without including obsolete
    print("\n1. Loading hacks without obsolete records:")
    hacks_no_obsolete = data_manager.get_all_hacks(include_obsolete=False)
    print(f"   Found {len(hacks_no_obsolete)} non-obsolete hacks")
    
    # Test 2: Load all hacks including obsolete
    print("\n2. Loading hacks including obsolete records:")
    all_hacks = data_manager.get_all_hacks(include_obsolete=True)
    print(f"   Found {len(all_hacks)} total hacks")
    
    obsolete_count = len(all_hacks) - len(hacks_no_obsolete)
    print(f"   Obsolete records: {obsolete_count}")
    
    # Test 3: Show some obsolete records
    print("\n3. Sample obsolete records:")
    obsolete_found = 0
    for hack in all_hacks:
        if hack.get("obsolete", False):
            print(f"   - {hack.get('title', 'Unknown')} (obsolete: {hack.get('obsolete')})")
            obsolete_found += 1
            if obsolete_found >= 3:  # Show first 3
                break
    
    if obsolete_found == 0:
        print("   No obsolete records found")
    
    # Test 4: Test filter functionality
    print("\n4. Testing table filters:")
    
    def dummy_callback():
        pass
    
    filters = TableFilters(dummy_callback)
    
    # Test filter with "Any" (should include all)
    filters.obsolete_filter.set("Any")
    filtered_any = filters.apply_filters(all_hacks)
    print(f"   Filter 'Any': {len(filtered_any)} records")
    
    # Test filter with "Yes" (should include only obsolete)
    filters.obsolete_filter.set("Yes")
    filtered_yes = filters.apply_filters(all_hacks)
    print(f"   Filter 'Yes': {len(filtered_yes)} records")
    
    # Test filter with "No" (should exclude obsolete)
    filters.obsolete_filter.set("No")
    filtered_no = filters.apply_filters(all_hacks)
    print(f"   Filter 'No': {len(filtered_no)} records")
    
    # Verify the "Yes" filter shows only obsolete records
    print("\n5. Verifying 'Yes' filter shows only obsolete records:")
    all_obsolete = True
    for hack in filtered_yes[:5]:  # Check first 5
        is_obsolete = hack.get("obsolete", False)
        print(f"   - {hack.get('title', 'Unknown')}: obsolete={is_obsolete}")
        if not is_obsolete:
            all_obsolete = False
    
    if all_obsolete and len(filtered_yes) > 0:
        print("   ✅ Filter working correctly - all records are obsolete")
    elif len(filtered_yes) == 0:
        print("   ❌ Filter not working - no obsolete records found")
    else:
        print("   ❌ Filter not working - some records are not obsolete")
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    test_obsolete_filter()
