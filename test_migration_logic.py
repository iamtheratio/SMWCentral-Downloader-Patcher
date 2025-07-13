#!/usr/bin/env python3
"""Test migration logic with mocked API data"""

def test_migration_logic():
    """Test the migration logic with the actual API response structure"""
    
    # Simulate the API response we found
    api_response = {
        "data": {
            "id": 38820,
            "name": "A Haunting at Chateau Cousseaux",
            "authors": [
                {
                    "id": 52803,
                    "name": "NixKillsMyths"
                }
            ],
            "raw_fields": {
                "hof": False,
                "length": 9,
                "demo": False,
                "sa1": False,
                "collab": False,
                "difficulty": "diff_7"
            }
        }
    }
    
    # Test the migration logic
    if "data" in api_response:
        file_data = api_response["data"]
        
        # Get metadata like the migration does
        raw_fields = file_data.get("raw_fields", {})
        length = raw_fields.get("length", 0)
        authors = file_data.get("authors", [])
        
        # Process authors like migration does
        authors_list = []
        for author in authors:
            if isinstance(author, dict) and "name" in author:
                authors_list.append(author["name"])
        
        print(f"🔍 Testing migration logic:")
        print(f"   Original API length: {length} (type: {type(length)})")
        print(f"   Original API authors: {authors}")
        print(f"   Processed authors: {authors_list}")
        
        # Simulate what would be stored in processed.json
        result = {
            "exits": length,
            "authors": authors_list
        }
        
        print(f"\n✅ Migration would store:")
        print(f"   exits: {result['exits']}")
        print(f"   authors: {result['authors']}")
        
        if result['exits'] > 0:
            print(f"✅ Success: Would populate exits with {result['exits']}")
        else:
            print(f"❌ Problem: exits would still be 0")
            
        if result['authors']:
            print(f"✅ Success: Would populate authors with {len(result['authors'])} authors")
        else:
            print(f"❌ Problem: authors would still be empty")

if __name__ == "__main__":
    test_migration_logic()
