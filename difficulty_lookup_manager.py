"""
Difficulty Lookup Manager
Fetches and caches difficulty mappings from SMWC API

Copyright (c) 2025 iamtheratio
Licensed under the MIT License - see LICENSE file for details
"""

import requests
from typing import Dict, Optional

def fetch_difficulty_lookup_from_api() -> Optional[Dict[str, str]]:
    """
    Fetch difficulty ID -> friendly name mappings from SMWC API.
    
    Returns:
        Dictionary mapping difficulty IDs to friendly names, or None if failed
        Example: {"diff_1": "Newcomer", "diff_2": "Casual", ...}
    """
    try:
        params = {
            "a": "getsectioninfo",
            "s": "smwhacks"
        }
        
        response = requests.get("https://www.smwcentral.net/ajax.php", params=params, timeout=10)
        
        if response.status_code != 200:
            return None
        
        data = response.json()
        
        # Find the difficulty field in the fields array
        fields = data.get("fields", [])
        difficulty_field = None
        
        for field in fields:
            if field.get("id") == "difficulty":
                difficulty_field = field
                break
        
        if not difficulty_field or not difficulty_field.get("options"):
            return None
        
        # Build the mapping
        lookup = {}
        for option in difficulty_field["options"]:
            difficulty_id = option.get("id")
            friendly_name = option.get("friendly_name")
            
            if difficulty_id and friendly_name:
                lookup[difficulty_id] = friendly_name
        
        return lookup if lookup else None
        
    except Exception as e:
        print(f"Error fetching difficulty lookup from API: {e}")
        return None


def get_difficulty_lookup(config_manager=None) -> Dict[str, str]:
    """
    Get difficulty lookup, preferring cached version from config.
    Falls back to hardcoded defaults if API fetch fails.
    
    Args:
        config_manager: ConfigManager instance (optional)
    
    Returns:
        Dictionary mapping difficulty IDs to friendly names
    """
    # Hardcoded fallback (current as of v4.8)
    FALLBACK_LOOKUP = {
        "diff_1": "Newcomer",
        "diff_2": "Casual",
        "diff_3": "Intermediate",
        "diff_4": "Advanced",
        "diff_5": "Expert",
        "diff_6": "Master",
        "diff_7": "Grandmaster"
    }
    
    # Try to get cached version from config
    if config_manager:
        cached = config_manager.get_difficulty_lookup()
        if cached and isinstance(cached, dict) and len(cached) > 0:
            return cached
    
    # Try to fetch from API
    fetched = fetch_difficulty_lookup_from_api()
    
    if fetched:
        # Save to config if we have a config manager
        if config_manager:
            config_manager.set_difficulty_lookup(fetched)
        return fetched
    
    # Fall back to hardcoded
    return FALLBACK_LOOKUP


def update_difficulty_lookup(config_manager) -> bool:
    """
    Force update difficulty lookup from SMWC API and save to config.
    
    Args:
        config_manager: ConfigManager instance
    
    Returns:
        True if successful, False if failed
    """
    fetched = fetch_difficulty_lookup_from_api()
    
    if fetched:
        config_manager.set_difficulty_lookup(fetched)
        return True
    
    return False
