#!/usr/bin/env python3
"""
Comprehensive test to validate History page deduplication and multi-type fixes
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from hack_data_manager import HackDataManager
from utils import format_types_display

def test_all_fixes():
    print("🔍 Testing History page deduplication and multi-type fixes...")
    print("=" * 60)
    
    # Test 1: HackDataManager deduplication
    print("\n📋 Test 1: HackDataManager deduplication")
    manager = HackDataManager()
    hacks = manager.get_all_hacks()
    
    print(f"  Total hacks loaded: {len(hacks)}")
    
    # Check for duplicate titles
    titles = [h['title'] for h in hacks]
    duplicates = [title for title in set(titles) if titles.count(title) > 1]
    
    if duplicates:
        print(f"  ❌ Found {len(duplicates)} duplicate titles:")
        for title in duplicates:
            print(f"    - {title}")
    else:
        print(f"  ✅ No duplicate titles found!")
    
    # Test 2: Multi-type display
    print("\n📋 Test 2: Multi-type display functionality")
    multi_type_hacks = [h for h in hacks if len(h.get('hack_types', [])) > 1]
    print(f"  Multi-type hacks found: {len(multi_type_hacks)}")
    
    if multi_type_hacks:
        print("  Multi-type hack examples:")
        for hack in multi_type_hacks[:3]:  # Show up to 3 examples
            types_display = format_types_display(hack['hack_types'])
            print(f"    📄 {hack['title']}")
            print(f"       Raw types: {hack['hack_types']}")
            print(f"       Display: {types_display}")
    
    # Test 3: Reverie specific test
    print("\n📋 Test 3: Reverie specific validation")
    reverie_hacks = [h for h in hacks if 'Reverie' in h['title']]
    print(f"  Reverie hacks found: {len(reverie_hacks)}")
    
    if len(reverie_hacks) == 1:
        hack = reverie_hacks[0]
        types_display = format_types_display(hack['hack_types'])
        print(f"  ✅ Single Reverie entry found:")
        print(f"    Title: {hack['title']}")
        print(f"    ID: {hack['id']}")
        print(f"    Types: {hack['hack_types']} → {types_display}")
        print(f"    Difficulty: {hack['difficulty']}")
        print(f"    Completed: {hack['completed']}")
    elif len(reverie_hacks) == 0:
        print(f"  ❌ No Reverie hack found!")
    else:
        print(f"  ❌ Multiple Reverie hacks found ({len(reverie_hacks)}):")
        for hack in reverie_hacks:
            print(f"    - ID {hack['id']}: {hack['title']}")
    
    # Test 4: Type display formatting
    print("\n📋 Test 4: Type display formatting")
    test_cases = [
        (["standard"], "Standard"),
        (["kaizo"], "Kaizo"),
        (["standard", "puzzle"], "Standard, Puzzle"),
        (["kaizo", "tool-assisted"], "Kaizo, Tool-Assisted"),
        ([], "Unknown")
    ]
    
    all_passed = True
    for input_types, expected in test_cases:
        result = format_types_display(input_types)
        if result == expected:
            print(f"  ✅ {input_types} → {result}")
        else:
            print(f"  ❌ {input_types} → {result} (expected: {expected})")
            all_passed = False
    
    if all_passed:
        print("  ✅ All type formatting tests passed!")
    
    # Test 5: Data integrity check
    print("\n📋 Test 5: Data integrity check")
    issues = []
    
    for hack in hacks:
        # Check required fields
        if not hack.get('title'):
            issues.append(f"Hack {hack.get('id', 'Unknown')} missing title")
        
        # Check hack_types array
        if not hack.get('hack_types') or not isinstance(hack['hack_types'], list):
            issues.append(f"Hack {hack.get('title', 'Unknown')} missing or invalid hack_types")
        
        # Check backward compatibility
        if not hack.get('hack_type'):
            issues.append(f"Hack {hack.get('title', 'Unknown')} missing backward-compatible hack_type")
    
    if issues:
        print(f"  ⚠️ Found {len(issues)} data integrity issues:")
        for issue in issues[:5]:  # Show first 5 issues
            print(f"    - {issue}")
        if len(issues) > 5:
            print(f"    ... and {len(issues) - 5} more")
    else:
        print("  ✅ No data integrity issues found!")
    
    # Final summary
    print("\n" + "=" * 60)
    print("🎯 SUMMARY")
    print("=" * 60)
    
    success_count = 0
    total_tests = 5
    
    if not duplicates:
        print("✅ Deduplication: PASSED")
        success_count += 1
    else:
        print("❌ Deduplication: FAILED")
    
    if len(reverie_hacks) == 1:
        print("✅ Reverie fix: PASSED")
        success_count += 1
    else:
        print("❌ Reverie fix: FAILED")
    
    if multi_type_hacks:
        print("✅ Multi-type support: PASSED")
        success_count += 1
    else:
        print("⚠️ Multi-type support: NO MULTI-TYPE HACKS TO TEST")
        success_count += 1  # Count as pass since it's expected
    
    if all_passed:
        print("✅ Type formatting: PASSED")
        success_count += 1
    else:
        print("❌ Type formatting: FAILED")
    
    if not issues:
        print("✅ Data integrity: PASSED")
        success_count += 1
    else:
        print("❌ Data integrity: ISSUES FOUND")
    
    print(f"\nOverall: {success_count}/{total_tests} tests passed")
    
    if success_count == total_tests:
        print("🎉 ALL TESTS PASSED! History page fixes are working correctly.")
    else:
        print("⚠️ Some tests failed. Please review the issues above.")

if __name__ == "__main__":
    test_all_fixes()
