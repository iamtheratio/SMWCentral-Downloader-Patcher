import json
import os
from datetime import datetime

class HackDataManager:
    """Manages hack data from processed.json with history tracking"""
    
    def __init__(self, json_path="processed.json"):
        self.json_path = json_path
        self.data = self._load_data()
    
    def _load_data(self):
        """Load data from processed.json"""
        try:
            with open(self.json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                # Ensure all entries have the new fields
                for hack_id, hack_data in data.items():
                    if isinstance(hack_data, dict):
                        hack_data.setdefault("completed", False)
                        hack_data.setdefault("completed_date", "")
                        hack_data.setdefault("personal_rating", 0)
                        hack_data.setdefault("notes", "")
                return data
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def save_data(self):
        """Save data back to processed.json"""
        try:
            with open(self.json_path, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2)
        except Exception as e:
            print(f"Error saving hack data: {e}")
    
    def get_all_hacks(self):
        """Get all hacks as a list of dictionaries"""
        hacks = []
        for hack_id, hack_data in self.data.items():
            if isinstance(hack_data, dict) and "file_path" in hack_data:
                hack_info = {
                    "id": hack_id,
                    "title": hack_data.get("title", "Unknown"),
                    "difficulty": hack_data.get("current_difficulty", "Unknown"),
                    "file_path": hack_data.get("file_path", ""),
                    "completed": hack_data.get("completed", False),
                    "completed_date": hack_data.get("completed_date", ""),
                    "personal_rating": hack_data.get("personal_rating", 0),
                    "notes": hack_data.get("notes", "")
                }
                hacks.append(hack_info)
        return hacks
    
    def update_hack(self, hack_id, field, value):
        """Update a specific field for a hack"""
        if hack_id in self.data and isinstance(self.data[hack_id], dict):
            # Auto-set completed date when completed is checked
            if field == "completed" and value and not self.data[hack_id].get("completed_date"):
                self.data[hack_id]["completed_date"] = datetime.now().strftime("%Y-%m-%d")
            
            self.data[hack_id][field] = value
            self.save_data()
            return True
        return False
    
    def get_unique_difficulties(self):
        """Get list of unique difficulties"""
        difficulties = set()
        for hack_data in self.data.values():
            if isinstance(hack_data, dict):
                diff = hack_data.get("current_difficulty", "Unknown")
                if diff:
                    difficulties.add(diff)
        return sorted(list(difficulties))