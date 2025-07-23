#!/usr/bin/env python3
"""Debug script to check analytics data structure and time progression calculation"""

import json
from datetime import datetime, timedelta
from collections import defaultdict

def debug_analytics():
    """Check what's in the analytics data for time progression"""
    
    # Load the hack data using the same path resolution
    from utils import PROCESSED_JSON_PATH
    processed_path = PROCESSED_JSON_PATH
    
    try:
        with open(processed_path, 'r', encoding='utf-8') as f:
            all_data = json.load(f)
    except FileNotFoundError:
        print(f"{processed_path} not found")
        return
    
    print("=== DEBUG: Checking Time Progression Data ===")
    
    # Calculate six months ago
    six_months_ago = datetime.now() - timedelta(days=180)
    print(f"Six months ago: {six_months_ago.strftime('%Y-%m-%d')}")
    
    # Find completed hacks
    completed_hacks = []
    for hack_id, hack_data in all_data.items():
        if hack_data.get('completed', False):
            completed_date = hack_data.get('completed_date')
            time_to_beat = hack_data.get('time_to_beat', 0)
            difficulty = hack_data.get('current_difficulty', 'Unknown')
            
            completed_hacks.append({
                'id': hack_id,
                'name': hack_data.get('hack_name', 'Unknown'),
                'completed_date': completed_date,
                'time_to_beat': time_to_beat,
                'difficulty': difficulty
            })
    
    print(f"\nTotal completed hacks: {len(completed_hacks)}")
    
    # Show recent completed hacks
    recent_hacks = []
    monthly_data = defaultdict(lambda: defaultdict(list))
    
    for hack in completed_hacks:
        if not hack['completed_date']:
            continue
            
        try:
            date_obj = datetime.strptime(hack['completed_date'], '%Y-%m-%d')
            if date_obj >= six_months_ago:
                recent_hacks.append(hack)
                
                # Add to monthly data if has time
                if hack['time_to_beat'] > 0:
                    month_key = date_obj.strftime('%Y-%m')
                    time_hours = hack['time_to_beat'] / 3600
                    monthly_data[month_key][hack['difficulty']].append({
                        'time': time_hours,
                        'hack_name': hack['name']
                    })
                    
        except ValueError:
            continue
    
    print(f"Recent completed hacks (last 6 months): {len(recent_hacks)}")
    
    # Show hacks with time data
    hacks_with_time = [h for h in recent_hacks if h['time_to_beat'] > 0]
    print(f"Recent hacks with time data: {len(hacks_with_time)}")
    
    for hack in hacks_with_time[:5]:  # Show first 5
        time_hours = hack['time_to_beat'] / 3600
        print(f"  - {hack['name'][:40]}: {hack['time_to_beat']}s = {time_hours:.3f}h ({hack['difficulty']}) on {hack['completed_date']}")
    
    # Show monthly breakdown
    print(f"\nMonthly data breakdown:")
    for month_key, difficulties in monthly_data.items():
        print(f"  {month_key}:")
        for difficulty, times in difficulties.items():
            avg_time = sum(t['time'] for t in times) / len(times)
            print(f"    {difficulty}: {len(times)} hacks, avg {avg_time:.3f}h")
            for time_data in times:
                print(f"      - {time_data['hack_name'][:30]}: {time_data['time']:.3f}h")
    
    # Check if any monthly data exists
    print(f"\nMonthly data exists: {bool(monthly_data)}")
    print(f"Month keys: {list(monthly_data.keys())}")

if __name__ == "__main__":
    debug_analytics()
