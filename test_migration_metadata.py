#!/usr/bin/env python3
"""Test migration metadata fetching"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api_pipeline import fetch_file_metadata

def test_detailed_metadata():
    """Test fetching detailed file metadata for a known hack"""
    # Test with hack ID 38820 (A Haunting At Chateau Cousseaux)
    hack_id = "38820"
    
    print(f"🔍 Testing detailed metadata fetch for hack {hack_id}...")
    
    try:
        file_meta = fetch_file_metadata(hack_id)
        
        if file_meta and "data" in file_meta:
            file_data = file_meta["data"]
            
            print(f"✅ Successfully fetched metadata:")
            print(f"  Title: {file_data.get('title', 'Unknown')}")
            print(f"  Length (exits): {file_data.get('length', 0)}")
            print(f"  Authors: {file_data.get('authors', [])}")
            
            if file_data.get('length', 0) > 0:
                print(f"🎯 Found {file_data['length']} exits")
            else:
                print("⚠️ No exit count found")
                
            if file_data.get('authors'):
                author_names = []
                for author in file_data['authors']:
                    if isinstance(author, dict) and "name" in author:
                        author_names.append(author["name"])
                print(f"👥 Authors: {author_names}")
            else:
                print("⚠️ No authors found")
        else:
            print("❌ No data returned from API")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_detailed_metadata()
