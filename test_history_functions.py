#!/usr/bin/env python3
"""Test the updated history page functions"""

import sys
sys.path.append('.')

from utils import format_types_display

# Test with the exact data from Reverie hack
hack_types = ['standard', 'puzzle']
result = format_types_display(hack_types)
print(f'format_types_display result: "{result}"')

# Test the filter logic
def test_filter_logic():
    hack_types = ['standard', 'puzzle']
    
    # Test filtering by 'Standard'
    type_matches_standard = any(hack_type.title() == 'Standard' for hack_type in hack_types)
    print(f'Filter by Standard: {type_matches_standard}')
    
    # Test filtering by 'Puzzle'  
    type_matches_puzzle = any(hack_type.title() == 'Puzzle' for hack_type in hack_types)
    print(f'Filter by Puzzle: {type_matches_puzzle}')
    
    # Test filtering by 'Kaizo' (should be False)
    type_matches_kaizo = any(hack_type.title() == 'Kaizo' for hack_type in hack_types)
    print(f'Filter by Kaizo: {type_matches_kaizo}')

test_filter_logic()

# Test importing the history components to make sure they work
try:
    from ui.history_components import TableFilters
    print('✅ History components import successful')
except Exception as e:
    print(f'❌ History components import failed: {e}')

try:
    from ui.pages.history_page import HistoryPage
    print('✅ History page import successful')
except Exception as e:
    print(f'❌ History page import failed: {e}')
