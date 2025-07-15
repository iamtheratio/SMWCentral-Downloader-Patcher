#!/usr/bin/env python3
"""Test script to verify multi-type filtering logic"""

# Test the filter logic that was updated
def test_type_filter():
    """Test the multi-type filtering logic"""
    
    # Mock hack data with multi-types
    hack_with_multi_types = {
        "title": "Test Hack",
        "hack_types": ["standard", "puzzle"],
        "hack_type": "standard"  # backward compatibility
    }
    
    hack_with_single_type = {
        "title": "Kaizo Hack", 
        "hack_types": ["kaizo"],
        "hack_type": "kaizo"
    }
    
    hack_with_old_format = {
        "title": "Old Format Hack",
        "hack_type": "pit"
        # No hack_types field
    }
    
    def check_type_filter(hack, type_filter_value):
        """Simulate the updated filter logic"""
        if type_filter_value == "All":
            return True
            
        hack_types = hack.get("hack_types", []) or [hack.get("hack_type", "")]
        type_matches = any(hack_type.title() == type_filter_value for hack_type in hack_types)
        return type_matches
    
    # Test cases
    test_cases = [
        (hack_with_multi_types, "Standard", True, "Multi-type hack should match 'Standard'"),
        (hack_with_multi_types, "Puzzle", True, "Multi-type hack should match 'Puzzle'"), 
        (hack_with_multi_types, "Kaizo", False, "Multi-type hack should NOT match 'Kaizo'"),
        (hack_with_single_type, "Kaizo", True, "Single-type hack should match 'Kaizo'"),
        (hack_with_single_type, "Standard", False, "Single-type hack should NOT match 'Standard'"),
        (hack_with_old_format, "Pit", True, "Old format hack should match 'Pit'"),
        (hack_with_old_format, "Kaizo", False, "Old format hack should NOT match 'Kaizo'"),
    ]
    
    print("🧪 Testing multi-type filter logic...")
    all_passed = True
    
    for hack, filter_value, expected, description in test_cases:
        result = check_type_filter(hack, filter_value)
        status = "✅ PASS" if result == expected else "❌ FAIL"
        if result != expected:
            all_passed = False
        print(f"{status}: {description}")
        print(f"   Hack: {hack.get('title')} | Filter: {filter_value} | Expected: {expected} | Got: {result}")
        
    print(f"\n{'🎉 All tests passed!' if all_passed else '💥 Some tests failed!'}")
    return all_passed

if __name__ == "__main__":
    test_type_filter()
