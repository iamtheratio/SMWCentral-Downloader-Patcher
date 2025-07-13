#!/usr/bin/env python3
"""Debug migration API calls"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api_pipeline import fetch_file_metadata
import json

def test_api_responses():
    """Test what the API actually returns for some hack IDs"""
    
    # Test with a few hack IDs from the processed.json
    test_hacks = ["38820", "38765", "37478"]  # A few from the list
    
    for hack_id in test_hacks:
        print(f"\n🔍 Testing hack ID: {hack_id}")
        print("="*50)
        
        try:
            # Test the file metadata fetch
            response = fetch_file_metadata(hack_id)
            
            if response:
                print(f"✅ API Response received")
                print(f"📦 Response keys: {list(response.keys())}")
                
                if "data" in response:
                    data = response["data"]
                    print(f"📄 Data keys: {list(data.keys())}")
                    
                    # Check specifically for the fields we want
                    title = data.get("title", "N/A")
                    length = data.get("length", "NOT_FOUND")
                    authors = data.get("authors", "NOT_FOUND")
                    
                    print(f"📝 Title: {title}")
                    print(f"🚪 Length (exits): {length}")
                    print(f"👥 Authors: {authors}")
                    
                    if length != "NOT_FOUND" and length > 0:
                        print(f"✅ Found exits data: {length}")
                    else:
                        print(f"❌ No exits data found")
                        
                    if authors != "NOT_FOUND" and authors:
                        print(f"✅ Found authors data: {len(authors)} authors")
                        for i, author in enumerate(authors[:3]):  # Show first 3
                            print(f"   👤 Author {i+1}: {author}")
                    else:
                        print(f"❌ No authors data found")
                else:
                    print(f"❌ No 'data' key in response")
                    print(f"🔍 Full response: {json.dumps(response, indent=2)[:500]}...")
            else:
                print(f"❌ No response from API")
                
        except Exception as e:
            print(f"💥 Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_api_responses()
