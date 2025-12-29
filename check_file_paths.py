"""Check why folder icons aren't appearing for Intermediate hacks"""
import json
import os

try:
    with open('processed.json', 'r', encoding='utf-8') as f:
        processed = json.load(f)
    
    print("Checking folder icon display logic for Intermediate hacks...\n")
    
    intermediate_hacks = []
    
    for hack_id, hack_data in processed.items():
        if not isinstance(hack_data, dict):
            continue
        
        current_diff = hack_data.get("current_difficulty", "")
        
        if current_diff == "Intermediate":
            file_path = hack_data.get("file_path", "")
            exists = os.path.exists(file_path) if file_path else False
            
            intermediate_hacks.append({
                "title": hack_data.get("title", "Unknown"),
                "file_path": file_path,
                "exists": exists
            })
    
    # Show first 5 examples
    print("Sample Intermediate hacks (first 5):\n")
    for i, hack in enumerate(intermediate_hacks[:5], 1):
        print(f"{i}. {hack['title']}")
        print(f"   file_path: {hack['file_path']}")
        print(f"   File exists: {'✅ YES' if hack['exists'] else '❌ NO'}")
        print()
    
    # Summary
    existing_count = sum(1 for h in intermediate_hacks if h['exists'])
    missing_count = len(intermediate_hacks) - existing_count
    
    print(f"Summary:")
    print(f"Total Intermediate hacks: {len(intermediate_hacks)}")
    print(f"Files that exist: {existing_count}")
    print(f"Files that DON'T exist: {missing_count}")
    
    if missing_count > 0:
        print(f"\n❌ PROBLEM FOUND: {missing_count} files don't exist at their file_path!")
        print("This is why folder icons aren't appearing.")
        print("\nShowing paths that don't exist:")
        for hack in intermediate_hacks:
            if not hack['exists']:
                print(f"  - {hack['file_path']}")
                if len([h for h in intermediate_hacks if not h['exists'] and hack == h]) >= 3:
                    print(f"  ... and {missing_count - 3} more")
                    break
    else:
        print(f"\n✅ All files exist - folder icons should appear!")
        print("If icons still don't show, check the UI code logic.")

except FileNotFoundError:
    print("❌ processed.json not found")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
