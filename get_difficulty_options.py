"""Get complete field info including difficulty options"""
import requests
import json

response = requests.get("https://www.smwcentral.net/ajax.php", params={"a": "getsectioninfo", "s": "smwhacks"})
data = response.json()

print("=== ALL FIELDS ===\n")
for field in data.get('fields', []):
    print(f"\nField: {field['id']}")
    print(f"  Name: {field['friendly_name']}")
    print(f"  Type: {field['type']}")
    
    if field.get('options'):
        print(f"  Options: {json.dumps(field['options'], indent=4)}")
    
    # If this is difficulty, show full details
    if 'diff' in field['id'].lower():
        print("\n🎯 DIFFICULTY FIELD FOUND!")
        print(json.dumps(field, indent=2))
