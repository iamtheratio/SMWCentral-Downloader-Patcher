import json
import os
import tkinter as tk
from tkinter import messagebox, ttk
import threading
import requests
from datetime import datetime
import time
from smwc_api_proxy import smwc_api_get
from api_pipeline import fetch_file_metadata
from utils import set_window_icon

class MigrationManager:
    """Handles migration from pre-v3.1 to v3.1 processed.json format"""
    
    def __init__(self, json_path=None):
        # If no path specified, use the same path resolution as download operations
        if json_path is None:
            from utils import PROCESSED_JSON_PATH
            json_path = PROCESSED_JSON_PATH
            
        self.json_path = json_path
        self.backup_path = f"{json_path}.pre-v3.1.backup"
        
    def needs_migration(self):
        """Check if processed.json needs migration to v3.1 format"""
        if not os.path.exists(self.json_path):
            return False
            
        try:
            with open(self.json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # Check if any hack is missing v3.0 or v3.1 fields
            for hack_id, hack_data in data.items():
                if isinstance(hack_data, dict):
                    # Check for very old format (only title, current_difficulty, type)
                    if len(hack_data) <= 3 and "type" in hack_data:
                        return True
                        
                    # Check for missing v3.0 required fields
                    v3_fields = ["hack_type", "hall_of_fame", "sa1_compatibility", 
                               "collaboration", "demo", "completed", "completed_date", 
                               "personal_rating", "notes"]
                    
                    missing_v3_fields = 0
                    for field in v3_fields:
                        if field not in hack_data:
                            missing_v3_fields += 1
                    
                    # If missing most v3.1 fields, we need migration
                    if missing_v3_fields >= 7:  # Missing most v3.0 fields
                        return True
                    
                    # Check for missing v3.1 fields (new structure and fields)
                    v3_1_fields = ["time_to_beat", "exits", "authors"]
                    missing_v3_1_fields = 0
                    for field in v3_1_fields:
                        if field not in hack_data:
                            missing_v3_1_fields += 1
                    
                    # If missing ALL v3.1 fields, we need migration
                    # Changed from > 0 to >= 3 to be less strict
                    if missing_v3_1_fields >= 3:
                        return True
                        
            return False  # All hacks have v3.1 format
            
        except (json.JSONDecodeError, Exception):
            return False  # Invalid file, let normal loading handle it
    
    def show_migration_dialog(self, root):
        """Show migration dialog to user"""
        result = messagebox.askyesno(
            "Database Upgrade Required - v3.1",
            "SMWC Downloader & Patcher v3.1 includes enhanced Hack Collection features:\n\n"
            "🕒 Time to Beat tracking for completed hacks\n"
            "🧠 Additional metadata (Authors, Exit count)\n"
            "🔄 Improved metadata synchronization\n\n"
            "To enable these features, your hack database needs to be upgraded with additional information from the SMWC API.\n\n"
            "This is a ONE-TIME process that will:\n"
            "• Preserve all your existing hack files and data\n"
            "• Keep any completion status and notes you've added\n"
            "• Download missing metadata for better filtering\n"
            "• Create a backup of your current database\n\n"
            "The upgrade takes 1-2 minutes and is significantly faster than v3.0.\n\n"
            "Would you like to proceed with the upgrade?",
            icon="question"
        )
        
        if not result:
            messagebox.showinfo(
                "Upgrade Cancelled", 
                "The application will now close. You can run the upgrade later by restarting the application."
            )
            root.quit()
            return False
            
        return True
    
    def migrate_with_progress(self, root, callback=None):
        """Run migration with progress dialog"""
        # Create progress window
        progress_window = tk.Toplevel(root)
        progress_window.title("Upgrading Database...")
        progress_window.geometry("600x300")
        progress_window.resizable(False, False)
        progress_window.transient(root)
        progress_window.grab_set()
        
        # Set the same icon as the main application
        set_window_icon(progress_window)
        
        # Center the window
        progress_window.update_idletasks()
        x = (progress_window.winfo_screenwidth() // 2) - (progress_window.winfo_width() // 2)
        y = (progress_window.winfo_screenheight() // 2) - (progress_window.winfo_height() // 2)
        progress_window.geometry(f"+{x}+{y}")
        
        # Progress widgets
        ttk.Label(progress_window, text="Upgrading hack database to v3.1 format...", 
                 font=("Segoe UI", 10, "bold")).pack(pady=20)
        
        progress_var = tk.StringVar(value="Preparing upgrade...")
        progress_label = ttk.Label(progress_window, textvariable=progress_var)
        progress_label.pack(pady=10)
        
        progress_bar = ttk.Progressbar(progress_window, mode='determinate')
        progress_bar.pack(pady=10, padx=40, fill="x")
        
        # Add log area for real-time updates
        log_frame = ttk.Frame(progress_window)
        log_frame.pack(pady=10, padx=20, fill="both", expand=True)
        
        ttk.Label(log_frame, text="Progress Log:", font=("Segoe UI", 8, "bold")).pack(anchor="w")
        
        log_text = tk.Text(log_frame, height=5, width=70, font=("Consolas", 8), 
                          wrap=tk.WORD, state="disabled")
        log_scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=log_text.yview)
        log_text.configure(yscrollcommand=log_scrollbar.set)
        
        log_text.pack(side="left", fill="both", expand=True)
        log_scrollbar.pack(side="right", fill="y")
        
        ttk.Label(progress_window, text="Please wait... Do not close the application.", 
                 font=("Segoe UI", 8)).pack(pady=5)
        
        # Helper function to add log messages
        def add_log(message):
            def _append():
                try:
                    log_text.config(state="normal")
                    log_text.insert(tk.END, f"{message}\n")
                    log_text.see(tk.END)  # Auto-scroll to bottom
                    log_text.config(state="disabled")
                except tk.TclError:
                    pass

            try:
                progress_window.after(0, _append)
            except tk.TclError:
                pass

        # Thread-safe UI helpers (must marshal to Tk main thread)
        def set_progress(text):
            try:
                progress_window.after(0, lambda t=text: progress_var.set(t))
            except tk.TclError:
                pass

        def set_progress_max(value):
            try:
                progress_window.after(0, lambda v=value: progress_bar.configure(maximum=v))
            except tk.TclError:
                pass

        def set_progress_value(value):
            try:
                progress_window.after(0, lambda v=value: progress_bar.configure(value=v))
            except tk.TclError:
                pass
        
        # Run migration in thread
        def migration_thread():
            try:
                self.perform_migration(set_progress, set_progress_max, set_progress_value, add_log)
                
                # Success
                progress_window.after(0, lambda: [
                    progress_window.destroy(),
                    messagebox.showinfo(
                        "Upgrade Complete!", 
                        "Your hack database has been successfully upgraded to v3.1!\n\n"
                        "You can now use the enhanced Hack Collection features including Time to Beat tracking.\n\n"
                        "A backup of your original database was saved as 'processed.json.pre-v3.1.backup'."
                    ),
                    callback() if callback else None
                ])
                
            except Exception as e:
                # Error - capture error message to avoid closure issues
                error_msg = str(e)
                progress_window.after(0, lambda: [
                    progress_window.destroy(),
                    messagebox.showerror(
                        "Upgrade Failed", 
                        f"An error occurred during the upgrade:\n\n{error_msg}\n\n"
                        "Your original database file was preserved. The application will continue with your existing data."
                    ),
                    callback() if callback else None  # Continue instead of quitting
                ])
        
        thread = threading.Thread(target=migration_thread, daemon=True)
        thread.start()
    
    def perform_migration(self, set_progress, set_progress_max, set_progress_value, add_log):
        """Perform the actual migration"""
        # Load existing data
        set_progress("Loading existing hack database...")
        add_log("📂 Loading existing hack database...")
        
        with open(self.json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        # Create backup
        set_progress("Creating backup...")
        add_log("💾 Creating backup of current database...")
        
        import shutil
        shutil.copy2(self.json_path, self.backup_path)
        add_log(f"✅ Backup created: {self.backup_path}")
        
        # Count hacks needing migration
        hacks_to_migrate = []
        for hack_id, hack_data in data.items():
            if isinstance(hack_data, dict) and "title" in hack_data:
                hacks_to_migrate.append((hack_id, hack_data))
        
        total_hacks = len(hacks_to_migrate)
        set_progress_max(total_hacks + 50)  # Add some for API pages
        add_log(f"📊 Found {total_hacks} hacks to migrate")
        
        # First, fetch all hack metadata from SMWC API in bulk
        set_progress("Fetching hack metadata from SMWC API...")
        add_log("🌐 Fetching hack metadata from SMWC API...")
        
        from api_pipeline import fetch_hack_list
        api_metadata = {}
        hack_ids = set(data.keys())
        
        # Use bulk API fetching like bulk_api_migrate.py
        page = 1
        total_fetched = 0
        while True:
            config = {}  # Empty config = no filters
            response = fetch_hack_list(config, page=page)
            
            if not response or not response.get("data"):
                break
            
            hacks = response["data"]
            page_matches = 0
            
            for hack in hacks:
                hack_id = str(hack.get("id", ""))
                if hack_id in hack_ids:  # Only process hacks we have
                    raw_fields = hack.get("raw_fields", {})
                    
                    api_metadata[hack_id] = {
                        "hall_of_fame": bool(raw_fields.get("hof", 0)),
                        "sa1_compatibility": bool(raw_fields.get("sa1", 0)),
                        "collaboration": bool(raw_fields.get("collab", 0)),
                        "demo": bool(raw_fields.get("demo", 0)),
                        # v3.1 OPTIMIZED: Extract exits and authors from page data instead of individual API calls
                        "length": raw_fields.get("length", 0),  # exits count
                        "authors": hack.get("authors", []),     # authors array
                        "basic_fetched": True
                    }
                    total_fetched += 1
                    page_matches += 1
            
            # Update progress and log
                    set_progress_value(min(page, 50))
            add_log(f"📄 Page {page}: Found {page_matches} matching hacks")
            
            # Check if we're on the last page
            if page >= response.get("last_page", 1):
                break
            
            page += 1
            time.sleep(0.5)  # Small delay between pages
        
        add_log(f"🎯 Fetched metadata for {total_fetched} hacks from API")
        
        # v3.1 OPTIMIZED: Skip individual API calls - exits and authors already extracted from page data
        # This provides significant speed improvement over v3.0 by eliminating hundreds of individual API calls
        add_log(f"✨ Enhanced all {total_fetched} hacks with complete metadata from page data")
        
        # Now migrate each hack with API data
        set_progress_max(total_hacks + 50)  # Reset for hack migration
        for i, (hack_id, hack_data) in enumerate(hacks_to_migrate):
            title = hack_data.get('title', 'Unknown')[:30]
            set_progress(f"Upgrading hack {i+1} of {total_hacks}: {title}...")
            set_progress_value(50 + i)  # Start after API pages
            
            # Log every 50th hack to avoid spam
            if i % 50 == 0 or i < 5:
                add_log(f"⚡ Upgrading: {title}")
            
            # Migration with API metadata
            self.migrate_single_hack_with_api_data(hack_data, hack_id, api_metadata.get(hack_id, {}))
        
        # Save updated data
        set_progress("Saving upgraded database...")
        add_log("💾 Saving upgraded database...")
        
        with open(self.json_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        
        # Final statistics
        api_hits = len([h for h in api_metadata.values() if h])
        sa1_count = len([h for h in data.values() if isinstance(h, dict) and h.get('sa1_compatibility')])
        hof_count = len([h for h in data.values() if isinstance(h, dict) and h.get('hall_of_fame')])
        exits_count = len([h for h in data.values() if isinstance(h, dict) and h.get('exits', 0) > 0])
        authors_count = len([h for h in data.values() if isinstance(h, dict) and h.get('authors', [])])
        
        set_progress_value(total_hacks + 50)
        add_log(f"✅ Migration completed!")
        add_log(f"📊 {total_hacks} hacks migrated, {api_hits} with API data")
        add_log(f"🚀 Found {sa1_count} SA-1 hacks, {hof_count} Hall of Fame")
        add_log(f"📈 Enhanced with {exits_count} exit counts, {authors_count} author lists")
        set_progress("Upgrade completed successfully!")
    
    def migrate_single_hack(self, hack_data, hack_id, progress_var=None, progress_window=None):
        """Migrate a single hack entry to v3.1 format with API metadata lookup"""
        
        # Handle very old format (only title, current_difficulty, type)
        if "type" in hack_data and len(hack_data) <= 3:
            # Map old "type" to new "hack_type" if needed
            if hack_data.get("type", "").lower() == "kaizo":
                hack_data["hack_type"] = "kaizo"
            else:
                hack_data["hack_type"] = "standard"
            
            # Generate folder_name and file_path based on difficulty
            difficulty = hack_data.get("current_difficulty", "")
            difficulty_mapping = {
                "Easy": "01 - Easy",
                "Normal": "02 - Normal", 
                "Skilled": "03 - Skilled",
                "Expert": "04 - Expert",
                "Master": "05 - Master",
                "Grandmaster": "07 - Grandmaster"
            }
            
            folder_name = difficulty_mapping.get(difficulty, "99 - Unknown")
            hack_data["folder_name"] = folder_name
            
            # Create a basic file path (user will need to update these)
            title = hack_data.get("title", "Unknown")
            hack_data["file_path"] = f"C:/Users/username/Desktop/SMWCentralDownloader/Romhacks\\Kaizo\\{folder_name}\\{title}.smc"
            
            # Remove old "type" field
            del hack_data["type"]
        
        # Add missing fields with defaults
        hack_data.setdefault("hack_type", "standard")
        hack_data.setdefault("current_difficulty", hack_data.get("difficulty", "Unknown"))
        hack_data.setdefault("hall_of_fame", False)
        hack_data.setdefault("sa1_compatibility", False)
        hack_data.setdefault("collaboration", False)
        hack_data.setdefault("demo", False)
        
        # Fetch metadata from SMWC API
        api_metadata = self.fetch_hack_metadata_with_retry(hack_id, progress_var, progress_window)
        if api_metadata:
            # Update with actual API metadata
            hack_data["hall_of_fame"] = api_metadata.get("hall_of_fame", False)
            hack_data["sa1_compatibility"] = api_metadata.get("sa1_compatibility", False)
            hack_data["collaboration"] = api_metadata.get("collaboration", False)
            hack_data["demo"] = api_metadata.get("demo", False)
        
        # Add collection tracking fields
        hack_data.setdefault("completed", False)
        hack_data.setdefault("completed_date", "")
        hack_data.setdefault("personal_rating", 0)
        hack_data.setdefault("notes", "")
        
        # Clean up old redundant fields
        if "difficulty" in hack_data and "current_difficulty" in hack_data:
            del hack_data["difficulty"]
        
        # PRIVACY FIX: Remove file_path as it contains usernames
        if "file_path" in hack_data:
            del hack_data["file_path"]
        
        # Convert "Any" values to False
        for field in ["hall_of_fame", "sa1_compatibility", "collaboration", "demo"]:
            if hack_data.get(field) == "Any":
                hack_data[field] = False
    
    def migrate_single_hack_with_api_data(self, hack_data, hack_id, api_metadata):
        """Migrate a single hack entry to v3.1 format using pre-fetched API metadata"""
        
        # Handle very old format (only title, current_difficulty, type)
        if "type" in hack_data:
            # Map old "type" to new "hack_type"
            if hack_data.get("type", "").lower() == "kaizo":
                hack_data["hack_type"] = "kaizo"
            else:
                hack_data["hack_type"] = "standard"
            
            # Generate folder_name based on difficulty
            difficulty = hack_data.get("current_difficulty", "Unknown")
            difficulty_mapping = {
                "Easy": "01 - Easy",
                "Normal": "02 - Normal", 
                "Skilled": "03 - Skilled",
                "Expert": "04 - Expert",
                "Master": "05 - Master",
                "Grandmaster": "07 - Grandmaster"
            }
            hack_data["folder_name"] = difficulty_mapping.get(difficulty, "99 - Unknown")
            
            # Remove old "type" field
            del hack_data["type"]
        
        # Add missing v3.1 fields
        hack_data.setdefault("hack_type", "standard")
        hack_data.setdefault("current_difficulty", hack_data.get("difficulty", "Unknown"))
        
        # Use API metadata if available, otherwise defaults
        if api_metadata:
            hack_data.setdefault("hall_of_fame", api_metadata.get("hall_of_fame", False))
            hack_data.setdefault("sa1_compatibility", api_metadata.get("sa1_compatibility", False))
            hack_data.setdefault("collaboration", api_metadata.get("collaboration", False))
            hack_data.setdefault("demo", api_metadata.get("demo", False))
            
            # v3.1 NEW: Add exits field from API length
            if "length" in api_metadata:
                hack_data["exits"] = api_metadata["length"]
            else:
                hack_data.setdefault("exits", 0)
            
            # v3.1 NEW: Add authors field from API authors array
            if "authors" in api_metadata and isinstance(api_metadata["authors"], list):
                # Convert authors array from [{id: 46333, name: "Lush_50"}] to ["Lush_50"]
                authors_list = []
                for author in api_metadata["authors"]:
                    if isinstance(author, dict) and "name" in author:
                        authors_list.append(author["name"])
                hack_data["authors"] = authors_list
            else:
                hack_data.setdefault("authors", [])
        else:
            # Fallback to defaults
            hack_data.setdefault("hall_of_fame", False)
            hack_data.setdefault("sa1_compatibility", False)
            hack_data.setdefault("collaboration", False)
            hack_data.setdefault("demo", False)
            hack_data.setdefault("exits", 0)  # v3.1 NEW
            hack_data.setdefault("authors", [])  # v3.1 NEW
        
        hack_data.setdefault("completed", False)
        hack_data.setdefault("completed_date", "")
        hack_data.setdefault("personal_rating", 0)
        hack_data.setdefault("notes", "")
        
        # v3.1 NEW: Add time_to_beat field (stored as total seconds, 0 = not set)
        hack_data.setdefault("time_to_beat", 0)
        
        # Clean up old redundant fields
        if "difficulty" in hack_data and "current_difficulty" in hack_data:
            del hack_data["difficulty"]
        
        # Remove file_path for privacy
        if "file_path" in hack_data:
            del hack_data["file_path"]

    def migrate_single_hack_fast(self, hack_data, hack_id):
        """Migrate a single hack entry to v3.1 format without API calls (fast mode)"""
        
        # Handle very old format (only title, current_difficulty, type)
        if "type" in hack_data:
            # Map old "type" to new "hack_type"
            if hack_data.get("type", "").lower() == "kaizo":
                hack_data["hack_type"] = "kaizo"
            else:
                hack_data["hack_type"] = "standard"
            
            # Generate folder_name based on difficulty
            difficulty = hack_data.get("current_difficulty", "Unknown")
            difficulty_mapping = {
                "Easy": "01 - Easy",
                "Normal": "02 - Normal", 
                "Skilled": "03 - Skilled",
                "Expert": "04 - Expert",
                "Master": "05 - Master",
                "Grandmaster": "07 - Grandmaster"
            }
            hack_data["folder_name"] = difficulty_mapping.get(difficulty, "99 - Unknown")
            
            # Remove old "type" field
            del hack_data["type"]
        
        # Add missing v3.1 fields with defaults (no API calls)
        hack_data.setdefault("hack_type", "standard")
        hack_data.setdefault("current_difficulty", hack_data.get("difficulty", "Unknown"))
        hack_data.setdefault("hall_of_fame", False)
        hack_data.setdefault("sa1_compatibility", False)
        hack_data.setdefault("collaboration", False)
        hack_data.setdefault("demo", False)
        hack_data.setdefault("completed", False)
        hack_data.setdefault("completed_date", "")
        hack_data.setdefault("personal_rating", 0)
        hack_data.setdefault("notes", "")
        
        # v3.1 NEW: Add new fields with defaults (no API calls in fast mode)
        hack_data.setdefault("time_to_beat", 0)  # 0 = not set
        hack_data.setdefault("exits", 0)  # 0 = unknown
        hack_data.setdefault("authors", [])  # empty array = unknown
        
        # Clean up old redundant fields
        if "difficulty" in hack_data and "current_difficulty" in hack_data:
            del hack_data["difficulty"]
        
        # Remove file_path for privacy
        if "file_path" in hack_data:
            del hack_data["file_path"]

    def fetch_hack_metadata_with_retry(self, hack_id, progress_var=None, progress_window=None, max_retries=3):
        """Fetch hack metadata from SMWC API with rate limiting and retry logic"""

        def _set_progress(text):
            if not progress_var:
                return
            if progress_window:
                try:
                    progress_window.after(0, lambda t=text: progress_var.set(t))
                except tk.TclError:
                    return
            else:
                # Assume caller is already on the UI thread
                try:
                    progress_var.set(text)
                except Exception:
                    return
        
        delay = 1.5  # Start with 1.5 second delay
        
        for attempt in range(max_retries):
            try:
                _set_progress(f"Fetching metadata for hack {hack_id} (attempt {attempt + 1}/{max_retries})...")
                
                # Rate limiting delay
                time.sleep(delay)
                
                # Fetch metadata using existing API function
                response = fetch_file_metadata(hack_id)
                
                if response and "data" in response:
                    hack_info = response["data"]
                    
                    # Extract metadata from raw_fields as done in api_pipeline.py
                    raw_fields = hack_info.get("raw_fields", {})
                    
                    metadata = {
                        "hall_of_fame": bool(raw_fields.get("hof", 0)),
                        "sa1_compatibility": bool(raw_fields.get("sa1", 0)),
                        "collaboration": bool(raw_fields.get("collab", 0)),
                        "demo": bool(raw_fields.get("demo", 0))
                    }
                    
                    return metadata
                
                # If no data returned, continue to next attempt
                continue
                
            except Exception as e:
                if "rate limit" in str(e).lower() or "429" in str(e):
                    # Rate limited - increase delay and retry
                    delay = min(delay * 1.5, 3.0)  # Increase delay, max 3 seconds
                    _set_progress(f"Rate limited for hack {hack_id}, retrying in {delay:.1f}s...")
                    time.sleep(delay)
                    continue
                else:
                    # Other error - log and continue with next attempt
                    _set_progress(f"Error fetching metadata for hack {hack_id}: {str(e)[:50]}...")
                    time.sleep(delay)
                    continue
        
        # All attempts failed - return None (will use defaults)
        return None

    def needs_multi_type_migration(self):
        """Check if processed.json needs migration to support multiple types (v4.1)"""
        if not os.path.exists(self.json_path):
            return False
            
        try:
            with open(self.json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # Check if any hack has single hack_type but no hack_types array
            for hack_id, hack_data in data.items():
                if isinstance(hack_data, dict):
                    # If we have hack_type but no hack_types, we need migration
                    if "hack_type" in hack_data and "hack_types" not in hack_data:
                        return True
                        
            return False  # All hacks have multi-type format
            
        except (json.JSONDecodeError, Exception):
            return False  # Invalid file, let normal loading handle it

    def migrate_to_multi_type_support(self, progress_callback=None):
        """Migrate processed.json to support multiple types per hack"""
        if not os.path.exists(self.json_path):
            return
        
        # Load existing data
        with open(self.json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        # Create backup
        backup_path = f"{self.json_path}.pre-multi-type.backup"
        import shutil
        shutil.copy2(self.json_path, backup_path)
        
        migrated_count = 0
        total_hacks = len([k for k, v in data.items() if isinstance(v, dict)])
        
        for hack_id, hack_data in data.items():
            if isinstance(hack_data, dict):
                # Convert single hack_type to hack_types array
                if "hack_type" in hack_data and "hack_types" not in hack_data:
                    single_type = hack_data["hack_type"]
                    hack_data["hack_types"] = [single_type] if single_type else ["standard"]
                    migrated_count += 1
                
                # Ensure backward compatibility - keep hack_type as primary type
                if "hack_types" in hack_data and hack_data["hack_types"]:
                    hack_data["hack_type"] = hack_data["hack_types"][0]
                
                if progress_callback:
                    progress_callback(migrated_count, total_hacks)
        
        # Save updated data
        with open(self.json_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        
        return migrated_count


def needs_v48_migration():
    """Check if processed.json needs migration to v4.8 format (current_difficulty field)"""
    from utils import PROCESSED_JSON_PATH
    
    if not os.path.exists(PROCESSED_JSON_PATH):
        return False
    
    try:
        with open(PROCESSED_JSON_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        # Check if any hack is missing current_difficulty field
        for hack_id, hack_data in data.items():
            if isinstance(hack_data, dict):
                # If has difficulty but no current_difficulty, needs migration
                if "difficulty" in hack_data and "current_difficulty" not in hack_data:
                    return True
        
        return False
    except Exception:
        return False


def migrate_to_v48():
    """
    Migrate processed.json to v4.8 format.
    Adds current_difficulty and difficulty_id fields for compatibility with new system.
    """
    from utils import PROCESSED_JSON_PATH, DIFFICULTY_LOOKUP
    
    if not os.path.exists(PROCESSED_JSON_PATH):
        return {"success": False, "message": "processed.json not found"}
    
    try:
        # Load data
        with open(PROCESSED_JSON_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        # Create backup
        backup_path = f"{PROCESSED_JSON_PATH}.pre-v4.8.backup"
        with open(backup_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        # Create reverse mapping: difficulty_name -> difficulty_id
        name_to_id = {}
        for diff_id, diff_name in DIFFICULTY_LOOKUP.items():
            if diff_name:
                name_to_id[diff_name] = diff_id
        
        # Add backward compatibility mappings
        name_to_id["Skilled"] = "diff_3"  # Old name for Intermediate
        
        migrated_count = 0
        
        for hack_id, hack_data in data.items():
            if not isinstance(hack_data, dict):
                continue
            
            # Get the old difficulty field
            difficulty = hack_data.get("difficulty", "")
            
            # If missing current_difficulty, copy from difficulty
            if "current_difficulty" not in hack_data and difficulty:
                hack_data["current_difficulty"] = difficulty
                migrated_count += 1
            
            # If missing difficulty_id, try to add it
            if "difficulty_id" not in hack_data:
                current_diff = hack_data.get("current_difficulty", difficulty)
                if current_diff and current_diff in name_to_id:
                    hack_data["difficulty_id"] = name_to_id[current_diff]
        
        # Save updated data
        with open(PROCESSED_JSON_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        return {
            "success": True,
            "migrated_count": migrated_count,
            "message": f"Successfully migrated {migrated_count} hacks to v4.8 format"
        }
        
    except Exception as e:
        return {"success": False, "message": f"Migration failed: {str(e)}"}


# Global function for easy access
def check_and_migrate(root, callback=None):
    """Check if migration is needed and run it if necessary"""
    try:
        # Check for v4.8 migration first (silent, fast)
        if needs_v48_migration():
            result = migrate_to_v48()
            if result.get("success"):
                print(f"✅ v4.8 Migration: {result.get('message')}")
        
        migration_manager = MigrationManager()
        
        needs_migration = migration_manager.needs_migration()
        
        if needs_migration:
            if migration_manager.show_migration_dialog(root):
                migration_manager.migrate_with_progress(root, callback)
            else:
                return False  # User cancelled
        else:
            # No migration needed, run callback immediately
            if callback:
                callback()
        
        return True
    except Exception as e:
        print(f"Error in migration: {e}")
        import traceback
        traceback.print_exc()
        # Fallback to running callback if migration fails
        if callback:
            callback()
        return True
