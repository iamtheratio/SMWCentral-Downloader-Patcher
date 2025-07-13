#!/usr/bin/env python3
"""
Generate test data for dashboard testing
Creates randomized completion data for testing dashboard analytics
"""

import json
import random
from datetime import datetime, timedelta

def generate_test_data():
    """Generate randomized test data for dashboard testing"""
    
    print("🔄 Loading processed.json...")
    
    # Load the current processed.json
    with open("processed.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    
    hack_ids = list(data.keys())
    total_hacks = len(hack_ids)
    
    print(f"📦 Found {total_hacks} hacks")
    
    # Calculate how many to mark as completed (50%)
    completed_count = total_hacks // 2
    completed_hacks = random.sample(hack_ids, completed_count)
    
    print(f"✅ Marking {completed_count} hacks as completed")
    
    # Generate date range for the last 3 years
    end_date = datetime.now()
    start_date = end_date - timedelta(days=3*365)  # 3 years ago
    
    def random_date():
        """Generate a random date within the 3-year range"""
        time_between = end_date - start_date
        days_between = time_between.days
        random_days = random.randrange(days_between)
        return (start_date + timedelta(days=random_days)).strftime("%Y-%m-%d")
    
    # Update each hack
    rating_count = 0
    for hack_id in hack_ids:
        hack = data[hack_id]
        
        if hack_id in completed_hacks:
            # Mark as completed
            hack["completed"] = True
            hack["completed_date"] = random_date()
            
            # 70% chance of having a rating (1-5)
            if random.random() < 0.7:
                hack["personal_rating"] = random.randint(1, 5)
                rating_count += 1
            else:
                hack["personal_rating"] = 0
            
            # Random time to beat between 1 and 100 hours (in seconds)
            min_seconds = 1 * 3600  # 1 hour
            max_seconds = 100 * 3600  # 100 hours
            hack["time_to_beat"] = random.randint(min_seconds, max_seconds)
        else:
            # Mark as not completed
            hack["completed"] = False
            hack["completed_date"] = ""
            hack["personal_rating"] = 0
            hack["time_to_beat"] = 0
    
    print(f"⭐ Generated ratings for {rating_count} completed hacks")
    print(f"⏱️ Generated time-to-beat values for {completed_count} completed hacks")
    
    # Save the test data
    print("💾 Saving test data to processed.json...")
    with open("processed.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print("✅ Test data generated successfully!")
    print(f"📊 Summary:")
    print(f"   • Total hacks: {total_hacks}")
    print(f"   • Completed: {completed_count} ({completed_count/total_hacks*100:.1f}%)")
    print(f"   • With ratings: {rating_count} ({rating_count/completed_count*100:.1f}% of completed)")
    print(f"   • Date range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    print()
    print("🔄 To restore original data: Copy-Item 'processed.json.original-backup' 'processed.json'")

if __name__ == "__main__":
    generate_test_data()
