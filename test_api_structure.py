#!/usr/bin/env python3
"""
Test script to examine SMWC API response structure and look for version/obsolete fields
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from smwc_api_proxy import smwc_api_get
import json

def test_api_structure():
    print("🔍 Testing SMWC API structure for version/obsolete fields...")
    
    # Search for Beautiful Dangerous specifically
    params = {
        "a": "getsectionlist", 
        "s": "smwhacks", 
        "n": 1,
        "u": "0",
        "f[name]": "Beautiful Dangerous"
    }
    
    try:
        response = smwc_api_get("https://www.smwcentral.net/ajax.php", params=params)
        response_data = response.json()
        raw_data = response_data.get("data", [])
        
        print(f"📊 Found {len(raw_data)} results for 'Beautiful Dangerous'")
        
        for i, hack in enumerate(raw_data):
            print(f"\n📋 Result {i+1}:")
            print(f"  ID: {hack.get('id')}")
            print(f"  Name: {hack.get('name')}")
            print(f"  URL: {hack.get('url', 'N/A')}")
            
            # Check for version-related fields
            version_fields = ['version', 'obsolete', 'superseded', 'deprecated', 'status']
            for field in version_fields:
                if field in hack:
                    print(f"  {field}: {hack[field]}")
            
            # Check raw_fields for version info
            raw_fields = hack.get("raw_fields", {})
            print(f"  Raw fields keys: {list(raw_fields.keys())}")
            
            for field in version_fields:
                if field in raw_fields:
                    print(f"  raw_fields.{field}: {raw_fields[field]}")
            
            # Show all available fields for first result
            if i == 0:
                print(f"\n📝 All available fields for first result:")
                for key, value in hack.items():
                    if key != "raw_fields":
                        print(f"    {key}: {type(value).__name__} = {value}")
                
                print(f"\n📝 All raw_fields for first result:")
                for key, value in raw_fields.items():
                    print(f"    raw_fields.{key}: {type(value).__name__} = {value}")
        
        # Also test a broader search to see if any hack has obsolete field
        print(f"\n🔍 Testing broader search for obsolete field...")
        
        broad_params = {
            "a": "getsectionlist", 
            "s": "smwhacks", 
            "n": 1,
            "u": "0"
        }
        
        response = smwc_api_get("https://www.smwcentral.net/ajax.php", params=broad_params)
        response_data = response.json()
        broad_data = response_data.get("data", [])
        
        obsolete_found = False
        for hack in broad_data[:10]:  # Check first 10 results
            raw_fields = hack.get("raw_fields", {})
            if "obsolete" in hack or "obsolete" in raw_fields:
                print(f"  ✅ Found obsolete field in hack {hack.get('id')}: {hack.get('name')}")
                print(f"    obsolete: {hack.get('obsolete', raw_fields.get('obsolete'))}")
                obsolete_found = True
        
        if not obsolete_found:
            print(f"  ⚠️ No 'obsolete' field found in first 10 results")
            
    except Exception as e:
        print(f"❌ Error testing API: {e}")

if __name__ == "__main__":
    test_api_structure()
