"""Extract all unique difficulty mappings from SMWC API"""
import requests
import json
from collections import defaultdict

def extract_difficulty_mappings():
    """Fetch multiple pages and build a complete difficulty ID -> Name mapping"""
    difficulty_map = {}
    
    # Fetch first few pages to get a good sample
    for page in range(1, 6):  # Check first 5 pages
        params = {
            "a": "getsectionlist",
            "s": "smwhacks",
            "n": page,
            "u": "0"
        }
        
        response = requests.get("https://www.smwcentral.net/ajax.php", params=params)
        data = response.json()
        
        if 'data' in data:
            for hack in data['data']:
                if 'raw_fields' in hack and 'difficulty' in hack['raw_fields']:
                    diff_id = hack['raw_fields']['difficulty']
                    diff_name = hack['fields'].get('difficulty', 'Unknown')
                    
                    if diff_id not in difficulty_map:
                        difficulty_map[diff_id] = diff_name
                        print(f"Found: {diff_id} -> {diff_name}")
    
    print("\n=== COMPLETE DIFFICULTY MAPPING ===")
    print(json.dumps(difficulty_map, indent=2, sort_keys=True))
    
    return difficulty_map

if __name__ == "__main__":
    mappings = extract_difficulty_mappings()
    print(f"\nTotal difficulty levels found: {len(mappings)}")
