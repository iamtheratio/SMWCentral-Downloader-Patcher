#!/usr/bin/env python3
"""
Test script to verify the hack edit functionality works correctly
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from hack_data_manager import HackDataManager

def test_hack_edit():
    """Test editing a hack with ID 35444"""
    # Load the data manager
    data_manager = HackDataManager("processed.json")
    
    print("Testing hack edit functionality...")
    
    # Check if hack 35444 exists
    hack_id = "35444"
    if hack_id not in data_manager.data:
        print(f"ERROR: Hack ID {hack_id} not found in data")
        print(f"Available hack IDs: {list(data_manager.data.keys())[:10]}...")
        return False
    
    print(f"✓ Hack {hack_id} found in data")
    
    # Get original data
    original_notes = data_manager.data[hack_id].get("notes", "")
    print(f"Original notes: '{original_notes}'")
    
    # Try to update the notes field
    test_notes = "Test notes from edit dialog fix"
    success = data_manager.update_hack(hack_id, "notes", test_notes)
    
    if success:
        print(f"✓ Successfully updated notes for hack {hack_id}")
        
        # Verify the update
        updated_notes = data_manager.data[hack_id].get("notes", "")
        if updated_notes == test_notes:
            print(f"✓ Notes correctly updated to: '{updated_notes}'")
            
            # Restore original notes
            data_manager.update_hack(hack_id, "notes", original_notes)
            print(f"✓ Restored original notes")
            
            return True
        else:
            print(f"❌ Notes not updated correctly. Expected: '{test_notes}', Got: '{updated_notes}'")
            return False
    else:
        print(f"❌ Failed to update hack {hack_id}")
        return False

if __name__ == "__main__":
    success = test_hack_edit()
    if success:
        print("\n🎉 Edit functionality test PASSED!")
    else:
        print("\n❌ Edit functionality test FAILED!")
    sys.exit(0 if success else 1)
