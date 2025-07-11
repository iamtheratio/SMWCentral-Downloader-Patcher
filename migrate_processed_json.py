import json

def migrate_processed_json():
    """Clean up redundant fields in processed.json"""
    
    with open("processed.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    
    for hack_id, hack_data in data.items():
        if isinstance(hack_data, dict):
            # Remove redundant difficulty field (keep current_difficulty)
            if "difficulty" in hack_data:
                del hack_data["difficulty"]
            
            # Convert "Any" strings to False (since we don't have real API data for existing hacks)
            for field in ["hall_of_fame", "sa1_compatibility", "collaboration", "demo"]:
                if hack_data.get(field) == "Any":
                    hack_data[field] = False
            
            # Add missing history fields if not present
            hack_data.setdefault("completed", False)
            hack_data.setdefault("completed_date", "")
            hack_data.setdefault("personal_rating", 0) 
            hack_data.setdefault("notes", "")
    
    # Save cleaned data
    with open("processed.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    
    print("✅ Migrated processed.json - removed redundant fields and converted to booleans")

if __name__ == "__main__":
    migrate_processed_json()