#!/usr/bin/env python3
"""Simple API test"""

import requests
import time

def test_simple_api():
    """Test SMWC API directly"""
    
    # Test with a known hack ID
    hack_id = "38820"  # A Haunting At Chateau Cousseaux
    
    print(f"🔍 Testing API call for hack {hack_id}...")
    
    try:
        # Direct API call like fetch_file_metadata does
        params = {"a": "getfile", "v": "2", "id": hack_id}
        url = "https://www.smwcentral.net/ajax.php"
        
        print(f"📡 Making request to: {url}")
        print(f"📋 Parameters: {params}")
        
        response = requests.get(url, params=params, timeout=10)
        
        print(f"📊 Status code: {response.status_code}")
        print(f"📏 Content length: {len(response.text)} chars")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"✅ Valid JSON response")
                print(f"🔑 JSON keys: {list(data.keys())}")
                
                if "data" in data:
                    file_data = data["data"]
                    print(f"📄 File data keys: {list(file_data.keys())}")
                    
                    title = file_data.get("title", "N/A")
                    length = file_data.get("length", "N/A") 
                    authors = file_data.get("authors", "N/A")
                    
                    print(f"📝 Title: {title}")
                    print(f"🚪 Length: {length}")
                    print(f"👥 Authors type: {type(authors)}")
                    print(f"👥 Authors value: {authors}")
                    
                else:
                    print(f"❌ No 'data' key found")
                    print(f"📋 Available keys: {list(data.keys())}")
                    
            except Exception as json_error:
                print(f"❌ JSON parse error: {json_error}")
                print(f"📄 Raw response (first 500 chars): {response.text[:500]}")
        else:
            print(f"❌ HTTP error: {response.status_code}")
            print(f"📄 Error response: {response.text[:200]}")
            
    except Exception as e:
        print(f"💥 Request failed: {e}")

if __name__ == "__main__":
    test_simple_api()
