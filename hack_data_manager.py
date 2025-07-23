import json
import os
import shutil
import threading
from datetime import datetime


class HackDataManager:
    """Manages hack data from processed.json with history tracking"""

    def __init__(self, json_path="processed.json", logger=None):
        self.json_path = json_path
        self.logger = logger
        self.data = self._load_data()
        self.unsaved_changes = False
        self.last_save_time = 0
        self.save_delay = 2.0  # Wait 2 seconds before auto-saving
        self._save_timer = None

    def _log(self, message, level="Information"):
        """Helper method to log messages if logger is available"""
        if self.logger:
            self.logger.log(message, level)
        # Fall back to print for backward compatibility during transition
        else:
            print(f"[{level}] {message}")

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
                        # v4.0 NEW fields
                        hack_data.setdefault("obsolete", False)
                return data
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def save_data(self):
        """Save data back to processed.json with validation"""
        try:
            # Validate we have data to save
            if not self.data:
                self._log("⚠️ Attempting to save empty data - operation cancelled", "Error")
                return False

            # Create backup of current file before saving
            if os.path.exists(self.json_path):
                backup_path = f"{self.json_path}.backup"
                shutil.copy2(self.json_path, backup_path)

            with open(self.json_path, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2)
            self._log(f"💾 Saved {len(self.data)} hack records to {self.json_path}", "Information")
            return True
        except Exception as e:
            self._log(f"❌ Failed to save hack data: {e}", "Error")
            return False

    def get_all_hacks(self, include_obsolete=False):
        """Get all hacks as a list of dictionaries

        Args:
            include_obsolete (bool): If True, include obsolete hack versions. Default False.
        """
        hacks = []

        for hack_id, hack_data in self.data.items():
            if isinstance(hack_data, dict) and "title" in hack_data:
                # Skip obsolete hacks unless explicitly requested
                if not include_obsolete and hack_data.get("obsolete", False):
                    continue

                title = hack_data.get("title", "Unknown")

                # With obsolete tracking, we may have multiple versions of the same hack
                # When include_obsolete=True, we want to include all versions (obsolete and current)
                # When include_obsolete=False, only current versions should be included
                # The obsolete system handles version management, so duplicate titles are expected when including obsolete versions

                hack_info = {
                    "id": hack_id,
                    "title": title,
                    "hack_type": hack_data.get("hack_type", "unknown").title(),  # Keep for backward compatibility
                    "hack_types": hack_data.get("hack_types", [hack_data.get("hack_type", "unknown")]),  # NEW: Include multi-type support
                    "difficulty": hack_data.get("current_difficulty", "Unknown"),  # Use current_difficulty only
                    "hall_of_fame": hack_data.get("hall_of_fame", False),
                    "sa1_compatibility": hack_data.get("sa1_compatibility", False),
                    "collaboration": hack_data.get("collaboration", False),
                    "demo": hack_data.get("demo", False),
                    "obsolete": hack_data.get("obsolete", False),  # NEW: Include obsolete status
                    # Removed file_path for privacy - contains usernames
                    "completed": hack_data.get("completed", False),
                    "completed_date": hack_data.get("completed_date", ""),
                    "personal_rating": hack_data.get("personal_rating", 0),
                    "notes": hack_data.get("notes", ""),
                    "time_to_beat": hack_data.get("time_to_beat", 0),  # v3.1 NEW: Add time_to_beat field
                    "exits": hack_data.get("exits", 0)  # v3.1 NEW: Add exits field for analytics
                }
                hacks.append(hack_info)
        return hacks

    def update_hack(self, hack_id, field, value):
        """Update a specific field for a hack with delayed saving for performance"""
        if hack_id not in self.data:
            self._log(f"❌ Hack ID {hack_id} not found in data", "Error")
            return False

        if not isinstance(self.data[hack_id], dict):
            self._log(f"❌ Hack {hack_id} data is not a dictionary", "Error")
            return False

        try:
            # Auto-set completed date when completed is checked
            if field == "completed" and value and not self.data[hack_id].get("completed_date"):
                self.data[hack_id]["completed_date"] = datetime.now().strftime("%Y-%m-%d")

            # Store old value for logging
            old_value = self.data[hack_id].get(field, None)
            self.data[hack_id][field] = value

            # Mark as having unsaved changes and schedule delayed save
            self.unsaved_changes = True
            self._schedule_delayed_save()

            self._log(f"🔄 Updated {field} for hack {hack_id}: '{old_value}' → '{value}' (will save in {self.save_delay}s)", "Debug")
            return True
        except Exception as e:
            self._log(f"❌ Exception updating hack {hack_id} field {field}: {e}", "Error")
            return False

    def _schedule_delayed_save(self):
        """Schedule a delayed save to improve performance"""
        # Cancel any existing save timer
        if self._save_timer:
            self._save_timer.cancel()

        # Schedule new save
        self._save_timer = threading.Timer(self.save_delay, self._delayed_save)
        self._save_timer.start()

    def _delayed_save(self):
        """Perform the actual delayed save"""
        if self.unsaved_changes:
            if self.save_data():
                self.unsaved_changes = False
                self._log(f"💾 Successfully saved batched changes to {self.json_path}", "Information")
            else:
                self._log("❌ Failed to save batched changes", "Error")

    def force_save(self):
        """Force immediate save of any pending changes"""
        if self._save_timer:
            self._save_timer.cancel()
            self._save_timer = None

        if self.unsaved_changes:
            success = self.save_data()
            if success:
                self.unsaved_changes = False
                self._log(f"💾 Successfully saved pending changes to {self.json_path}", "Information")
            return success
        return True

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

    def add_user_hack(self, user_id, hack_data):
        """Add a user-created hack entry"""
        try:
            self.data[user_id] = hack_data
            self.unsaved_changes = True
            self._schedule_delayed_save()
            return True
        except Exception as e:
            self._log(f"❌ Error adding user hack: {e}", "Error")
            return False

    def delete_hack(self, hack_id):
        """Delete a hack entry (typically for user-created hacks)"""
        try:
            hack_id = str(hack_id)
            if hack_id in self.data:
                # Remove from data
                del self.data[hack_id]
                self.unsaved_changes = True
                self._schedule_delayed_save()

                # For user hacks, we might want to delete associated files
                # but for now, just remove from JSON data
                return True
            else:
                self._log(f"❌ Hack ID {hack_id} not found for deletion", "Error")
                return False
        except Exception as e:
            self._log(f"❌ Error deleting hack {hack_id}: {e}", "Error")
            return False
