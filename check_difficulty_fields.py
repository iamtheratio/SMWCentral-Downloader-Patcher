"""Quick diagnostic script to check difficulty fields in processed.json"""
import json

try:
    with open('processed.json', 'r', encoding='utf-8') as f:
        processed = json.load(f)
    
    print("Checking difficulty fields for Intermediate hacks...\n")
    
    intermediate_count = 0
    mismatch_count = 0
    
    for hack_id, hack_data in processed.items():
        if not isinstance(hack_data, dict):
            continue
        
        current_diff = hack_data.get("current_difficulty", "")
        difficulty = hack_data.get("difficulty", "")
        difficulty_id = hack_data.get("difficulty_id", "")
        file_path = hack_data.get("file_path", "")
        
        if current_diff == "Intermediate" or "Intermediate" in file_path:
            intermediate_count += 1
            
            # Check for mismatch
            if difficulty != current_diff:
                mismatch_count += 1
                if mismatch_count <= 5:  # Show first 5 examples
                    print(f"Hack: {hack_data.get('title', 'Unknown')}")
                    print(f"  difficulty_id: {difficulty_id}")
                    print(f"  current_difficulty: {current_diff}")
                    print(f"  difficulty: {difficulty}")
                    print(f"  file_path: {file_path}")
                    print()
    
    print(f"\nSummary:")
    print(f"Total Intermediate hacks: {intermediate_count}")
    print(f"Hacks with field mismatch: {mismatch_count}")
    
    if mismatch_count > 0:
        print(f"\n⚠️ Found {mismatch_count} hacks where 'difficulty' doesn't match 'current_difficulty'")
        print("This is why folder icons are missing!")
    else:
        print("\n✅ All fields are synced correctly")
        print("The issue might be something else...")

except FileNotFoundError:
    print("❌ processed.json not found in current directory")
except Exception as e:
    print(f"❌ Error: {e}")
