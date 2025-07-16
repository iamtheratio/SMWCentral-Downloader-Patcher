#!/usr/bin/env python3
"""
Test script to verify History page multi-type display functionality
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from hack_data_manager import HackDataManager
from utils import format_types_display

def test_history_display():
    print("🔍 Testing History page multi-type display...")
    
    # Test HackDataManager
    manager = HackDataManager()
    hacks = manager.get_all_hacks()
    
    print(f"📊 Total hacks loaded: {len(hacks)}")
    
    # Find multi-type hacks
    multi_type_hacks = [h for h in hacks if len(h.get('hack_types', [])) > 1]
    print(f"🔄 Multi-type hacks found: {len(multi_type_hacks)}")
    
    # Display some examples
    for hack in multi_type_hacks[:5]:  # Show first 5 multi-type hacks
        types_display = format_types_display(hack['hack_types'])
        print(f"  📋 {hack['title']} - Types: {types_display}")
    
    # Test Reverie specifically
    reverie = [h for h in hacks if 'Reverie' in h['title']]
    if reverie:
        hack = reverie[0]
        types_display = format_types_display(hack['hack_types'])
        print(f"\n✅ Reverie test:")
        print(f"  Title: {hack['title']}")
        print(f"  Raw types: {hack['hack_types']}")
        print(f"  Display types: {types_display}")
    else:
        print("\n❌ Reverie not found!")
    
    # Test deduplication by checking for any duplicate titles
    titles = [h['title'] for h in hacks]
    duplicates = [title for title in set(titles) if titles.count(title) > 1]
    
    if duplicates:
        print(f"\n⚠️ Found {len(duplicates)} duplicate titles:")
        for title in duplicates:
            print(f"  - {title}")
    else:
        print(f"\n✅ No duplicate titles found - deduplication working!")

if __name__ == "__main__":
    test_history_display()
