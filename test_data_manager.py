#!/usr/bin/env python3
"""Test the updated hack data manager"""

import sys
sys.path.append('.')

from hack_data_manager import HackDataManager

# Test the updated data manager
dm = HackDataManager()
all_hacks = dm.get_all_hacks()

# Find the Reverie hack to test
reverie_hack = None
for hack in all_hacks:
    if 'Reverie' in hack.get('title', ''):
        reverie_hack = hack
        break

if reverie_hack:
    print('✅ Found Reverie hack:')
    print(f'  Title: {reverie_hack.get("title")}')
    print(f'  hack_type: {reverie_hack.get("hack_type")}')
    print(f'  hack_types: {reverie_hack.get("hack_types")}')
    
    # Test the display formatting
    from utils import format_types_display
    hack_types = reverie_hack.get("hack_types", [])
    formatted = format_types_display(hack_types)
    print(f'  Formatted display: "{formatted}"')
else:
    print('❌ Reverie hack not found')

print(f'\nTotal hacks loaded: {len(all_hacks)}')
