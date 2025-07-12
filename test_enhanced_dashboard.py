#!/usr/bin/env python3
"""
Test the enhanced dashboard functionality
"""

import tkinter as tk
from tkinter import ttk
import sys, os

# Add the project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from ui.pages.dashboard_page import DashboardPage

print('Testing new enhanced dashboard...')

root = tk.Tk()
root.withdraw()
test_frame = ttk.Frame(root)

dashboard = DashboardPage(test_frame)
dashboard._load_analytics_data()

print(f'✓ Total hacks: {dashboard.analytics_data.get("total_hacks", 0)}')
print(f'✓ Completed: {dashboard.analytics_data.get("completed_hacks", 0)}')
print(f'✓ Completion rate: {dashboard.analytics_data.get("completion_rate", 0):.1f}%')
print(f'✓ Average rating: {dashboard.analytics_data.get("average_rating", 0):.1f}')
print(f'✓ Estimated playtime: {dashboard.analytics_data.get("total_playtime_estimate", 0)}h')
print(f'✓ Completion velocity: {dashboard.analytics_data.get("completion_velocity", 0):.1f}/mo')
print(f'✓ Perfectionist score: {dashboard.analytics_data.get("perfectionist_score", 0):.1f}%')
print(f'✓ Favorite difficulty: {dashboard.analytics_data.get("favorite_difficulty", "N/A")}')
print(f'✓ Favorite type: {dashboard.analytics_data.get("favorite_type", "N/A")}')

# Test completion data
completion_by_diff = dashboard.analytics_data.get("completion_by_difficulty", {})
print(f'✓ Difficulties tracked: {len(completion_by_diff)}')

completion_by_type = dashboard.analytics_data.get("completion_by_type", {})
print(f'✓ Types tracked: {len(completion_by_type)}')

top_rated = dashboard.analytics_data.get("top_rated", [])
print(f'✓ Top rated hacks: {len(top_rated)}')

hardest = dashboard.analytics_data.get("hardest_completed", [])
print(f'✓ Hardest completed: {len(hardest)}')

root.destroy()
print('\n🎉 Enhanced dashboard test successful!')
