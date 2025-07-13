import json
import os
import shutil
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
                # Ensure all entries have the v3.0 and v3.1 fields
                for hack_id, hack_data in data.items():
                    if isinstance(hack_data, dict):
                        # v3.0 fields
                        hack_data.setdefault("completed", False)
                        hack_data.setdefault("completed_date", "")
                        hack_data.setdefault("personal_rating", 0)
                        hack_data.setdefault("notes", "")
                        # v3.1 NEW fields
                        hack_data.setdefault("time_to_beat", 0)
                        hack_data.setdefault("exits", 0)
                        hack_data.setdefault("authors", [])
                return data
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def save_data(self):
        """Save data back to processed.json with validation"""
        try:
            # Validate we have data to save
            if not self.data:
                print("WARNING: Attempting to save empty data - operation cancelled")
                return False
                
            # Create backup of current file before saving
            import shutil
            if os.path.exists(self.json_path):
                backup_path = f"{self.json_path}.backup"
                shutil.copy2(self.json_path, backup_path)
            
            with open(self.json_path, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2)
            print(f"SUCCESS: Saved {len(self.data)} hack records to {self.json_path}")
            return True
        except Exception as e:
            print(f"ERROR: Failed to save hack data: {e}")
            return False
    
    def get_all_hacks(self):
        """Get all hacks as a list of dictionaries"""
        hacks = []
        for hack_id, hack_data in self.data.items():
            if isinstance(hack_data, dict) and "title" in hack_data:
                hack_info = {
                    "id": hack_id,
                    "title": hack_data.get("title", "Unknown"),
                    "hack_type": hack_data.get("hack_type", "unknown").title(),  # Capitalize for display
                    "difficulty": hack_data.get("current_difficulty", "Unknown"),  # Use current_difficulty only
                    "hall_of_fame": hack_data.get("hall_of_fame", False),
                    "sa1_compatibility": hack_data.get("sa1_compatibility", False),
                    "collaboration": hack_data.get("collaboration", False),
                    "demo": hack_data.get("demo", False),
                    # Removed file_path for privacy - contains usernames
                    "completed": hack_data.get("completed", False),
                    "completed_date": hack_data.get("completed_date", ""),
                    "personal_rating": hack_data.get("personal_rating", 0),
                    "notes": hack_data.get("notes", "")
                }
                hacks.append(hack_info)
        return hacks
    
    def update_hack(self, hack_id, field, value):
        """Update a specific field for a hack with validation"""
        if hack_id not in self.data:
            print(f"ERROR: Hack ID {hack_id} not found in data")
            return False
            
        if not isinstance(self.data[hack_id], dict):
            print(f"ERROR: Hack {hack_id} data is not a dictionary")
            return False
            
        try:
            # Auto-set completed date when completed is checked
            if field == "completed" and value and not self.data[hack_id].get("completed_date"):
                self.data[hack_id]["completed_date"] = datetime.now().strftime("%Y-%m-%d")
            
            # Store old value for logging
            old_value = self.data[hack_id].get(field, None)
            self.data[hack_id][field] = value
            
            # Save and validate
            if self.save_data():
                print(f"SUCCESS: Updated {field} for hack {hack_id}: '{old_value}' → '{value}'")
                return True
            else:
                print(f"ERROR: Failed to save data after updating {field} for hack {hack_id}")
                return False
        except Exception as e:
            print(f"ERROR: Exception updating hack {hack_id} field {field}: {e}")
            return False
    
    def get_unique_types(self):
        """Get list of unique hack types"""
        return ["Kaizo", "Pit", "Puzzle", "Standard", "Tool-Assisted"]  # Fixed list in alphabetical order

    def get_unique_difficulties(self):
        """Get list of unique difficulties in logical order"""
        difficulties = set()
        for hack_data in self.data.values():
            if isinstance(hack_data, dict):
                diff = hack_data.get("current_difficulty", "Unknown")
                if diff and diff != "Unknown":
                    difficulties.add(diff)
        
        # Define the logical order from easiest to hardest
        difficulty_order = ["Newcomer", "Casual", "Skilled", "Advanced", "Expert", "Master", "Grandmaster"]
        
        # Sort difficulties by their position in the defined order
        ordered_difficulties = []
        for difficulty in difficulty_order:
            if difficulty in difficulties:
                ordered_difficulties.append(difficulty)
        
        # Add any unknown difficulties at the end (alphabetically sorted)
        remaining = sorted([d for d in difficulties if d not in difficulty_order])
        ordered_difficulties.extend(remaining)
        
        return ordered_difficulties