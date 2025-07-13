#!/usr/bin/env python3
"""Test the fixed fetch_file_metadata function"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api_pipeline import fetch_file_metadata

def test_fixed_api():
    """Test the fixed API function"""
    
    hack_id = "38820"
    print(f"🔍 Testing fixed fetch_file_metadata for hack {hack_id}...")
    
    try:
        result = fetch_file_metadata(hack_id)
        
        if result and "data" in result:
            data = result["data"]
            print(f"✅ API call successful")
            
            # Test the fields we need for migration
            raw_fields = data.get("raw_fields", {})
            exits = raw_fields.get("length", 0)
            authors = data.get("authors", [])
            title = data.get("name", "Unknown")
            
            print(f"📝 Title: {title}")
            print(f"🚪 Exits: {exits} (type: {type(exits)})")
            print(f"👥 Authors: {len(authors)} authors")
            
            if authors:
                for i, author in enumerate(authors[:3]):
                    print(f"   👤 Author {i+1}: {author}")
            
            print(f"\n🎯 Migration would set:")
            print(f"   exits: {exits}")
            print(f"   authors: {[a.get('name') for a in authors if isinstance(a, dict)]}")
            
        else:
            print(f"❌ API call failed or no data")
            
    except Exception as e:
        print(f"💥 Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_fixed_api()
