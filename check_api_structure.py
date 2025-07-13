#!/usr/bin/env python3
"""Check actual API response structure"""

import requests
import json

def check_api_structure():
    """Check what fields are actually available"""
    
    hack_id = "38820"
    params = {"a": "getfile", "v": "2", "id": hack_id}
    url = "https://www.smwcentral.net/ajax.php"
    
    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        print(f"🔍 Full API response structure for hack {hack_id}:")
        print("="*60)
        print(json.dumps(data, indent=2))
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_api_structure()
