import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from hack_data_manager import HackDataManager
from ui.hack_history_components import InlineEditor, DateValidator, NotesValidator, TableFilters, HackHistoryInlineEditor

class HackHistoryPage:
    """Simplified hack history page with extracted components"""
    
    def __init__(self, parent, logger=None):
        self.parent = parent
        self.frame = None
        self.data_manager = HackDataManager()
        self.logger = logger  # Add logger support
        
        # Initialize components - USE HackHistoryInlineEditor instead of InlineEditor
        self.filters = TableFilters(self._apply_filters)
        self.date_editor = HackHistoryInlineEditor(None, self.data_manager, self, logger)
        self.notes_editor = HackHistoryInlineEditor(None, self.data_manager, self, logger)
        self.time_editor = HackHistoryInlineEditor(None, self.data_manager, self, logger)  # v3.1 NEW
        
        # Table and data
        self.tree = None
        self.filtered_data = []
        self.status_label = None
    
    def _log(self, message, level="Information"):
        """Log a message if logger is available"""
        if self.logger:
            self.logger.log(message, level)
        
    def create(self):
        """Create the hack history page"""
        self.frame = ttk.Frame(self.parent, padding=10)
        
        # Create filter section
        filter_frame = self.filters.create_filter_ui(self.frame, self.data_manager)
        filter_frame.pack(fill="x", pady=(0, 10))
        
        # Connect refresh button
        # (This is a bit hacky but keeps the component simple)
        for widget in filter_frame.winfo_children():
            if isinstance(widget, ttk.Frame):
                for child in widget.winfo_children():
                    if isinstance(child, ttk.Frame):
                        for grandchild in child.winfo_children():
                            if isinstance(grandchild, ttk.Button) and "Refresh" in grandchild.cget("text"):
                                grandchild.configure(command=self._refresh_data_and_table)
        
        # Create table section
        self._create_table()
        
        # Load initial data
        self._refresh_data_and_table()
        
        return self.frame
    
    def show(self):
        """Called when the page becomes visible"""
        if self.frame:
            self._refresh_data_and_table()
            total_hacks = len(self.data_manager.get_all_hacks())
            completed_hacks = sum(1 for hack in self.data_manager.get_all_hacks() if hack.get("completed", False))
            self._log(f"📊 Hack History page loaded - {total_hacks} total hacks, {completed_hacks} completed", "Information")
    
    def hide(self):
        """Called when the page becomes hidden"""
        self.date_editor.cleanup()
        self.notes_editor.cleanup()
        self.time_editor.cleanup()  # v3.1 NEW
    
    def _create_table(self):
        """Create the main data table"""
        table_frame = ttk.Frame(self.frame)
        table_frame.pack(fill="both", expand=True)
        
        # Create treeview
        columns = ("completed", "title", "type", "difficulty", "rating", "completed_date", "time_to_beat", "notes")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
        
        # Configure headers and columns
        headers = ["✓", "Title", "Type", "Difficulty", "Rating", "Completed Date", "Time to Beat", "Notes"]
        widths = [45, 220, 90, 100, 90, 110, 120, 150]
        min_widths = [35, 170, 70, 80, 70, 90, 100, 120]
        anchors = ["center", "w", "center", "center", "center", "center", "center", "w"]
        
        for i, (col, header, width, min_width, anchor) in enumerate(zip(columns, headers, widths, min_widths, anchors)):
            self.tree.heading(col, text=header)
            self.tree.column(col, width=width, minwidth=min_width, anchor=anchor)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Grid layout
        self.tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid_remove()
        
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)
        
        # Configure editors with tree reference
        self.date_editor.tree = self.tree
        self.notes_editor.tree = self.tree
        self.time_editor.tree = self.tree  # v3.1 NEW
        
        # Bind events
        self.tree.bind("<Button-1>", self._on_item_click)
        self.tree.bind("<Double-1>", self._on_item_double_click)
        self.tree.bind("<Motion>", self._on_mouse_motion)
        self.tree.bind("<Configure>", lambda e: self._toggle_h_scrollbar(h_scrollbar))
        
        # Status label
        self.status_label = ttk.Label(self.frame, text="", font=("Segoe UI", 9))
        self.status_label.pack(pady=(5, 0))
    
    def _refresh_data_and_table(self):
        """Refresh data from file and update table"""
        # FIXED: Don't create new data manager - just reload the existing one's data
        try:
            old_count = len(self.data_manager.get_all_hacks())
            self.data_manager.data = self.data_manager._load_data()  # Reload from file
            new_count = len(self.data_manager.get_all_hacks())
            self.filters.refresh_dropdown_values(self.data_manager)
            self._refresh_table()
            self._log(f"🔄 Refreshed hack data from file - reloaded {new_count} hacks (was {old_count})", "Debug")
        except Exception as e:
            self._log(f"❌ Failed to refresh data: {str(e)}", "Error")
    
    def _refresh_table(self):
        """Refresh table data"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Get filtered data
        all_hacks = self.data_manager.get_all_hacks()
        self.filtered_data = self.filters.apply_filters(all_hacks)
        
        # Populate table
        for hack in self.filtered_data:
            self._insert_hack_row(hack)
        
        # Update status
        self._update_status_label(len(all_hacks), len(self.filtered_data))
    
    def _insert_hack_row(self, hack):
        """Insert a single hack row into the table"""
        completed_display = "✓" if hack.get("completed", False) else ""
        rating_display = self._get_rating_display(hack.get("personal_rating", 0))
        
        notes_display = hack.get("notes", "")
        if len(notes_display) > 30:
            notes_display = notes_display[:30] + "..."
        
        # v3.1 NEW: Format time to beat display
        time_to_beat_display = self._format_time_display(hack.get("time_to_beat", 0))
        
        hack_id = hack.get("id")
        
        self.tree.insert("", "end", values=(
            completed_display,
            hack["title"],
            hack.get("hack_type", "Unknown").title(),
            hack.get("difficulty", "Unknown"),
            rating_display,
            hack.get("completed_date", ""),
            time_to_beat_display,  # v3.1 NEW
            notes_display
        ), tags=(hack_id,))
    
    def _update_status_label(self, total_count, filtered_count):
        """Update the status label"""
        completed_count = sum(1 for hack in self.filtered_data if hack.get("completed", False))
        status_text = f"Showing {filtered_count} of {total_count} hacks"
        if filtered_count > 0:
            status_text += f" • {completed_count} completed"
        self.status_label.config(text=status_text)
    
    def _apply_filters(self):
        """Apply filters and refresh table"""
        self._refresh_table()
    
    def _on_item_click(self, event):
        """Handle single clicks on table items"""
        # Save any active edits first
        if self.date_editor.entry:
            self.date_editor.save()
            
        if self.notes_editor.entry:
            self.notes_editor.save()
        
        # v3.1 NEW: Save time editor if active
        if self.time_editor.entry:
            self.time_editor.save()
        
        # Identify clicked item and column
        item = self.tree.identify("item", event.x, event.y)
        column = self.tree.identify("column", event.x, event.y)
        
        if not item or not column:
            return
        
        # Get hack ID from tags
        tags = self.tree.item(item)["tags"]
        if not tags:
            return
        hack_id = tags[0]
        
        # Handle different column clicks
        if column == "#1":  # Completed
            self._toggle_completed(hack_id)
        elif column == "#5":  # Rating
            self._edit_rating(hack_id, item, event)
        elif column == "#6":  # Completed date
            self.date_editor.start_edit(hack_id, item, event, "completed_date", "#6", DateValidator.validate)
        elif column == "#7":  # Time to Beat (v3.1 NEW)
            self.time_editor.start_edit(hack_id, item, event, "time_to_beat", "#7", self._validate_time_input)
        elif column == "#8":  # Notes (was #7)
            self.notes_editor.start_edit(hack_id, item, event, "notes", "#8", NotesValidator.validate)
    
    def _on_item_double_click(self, event):
        """Handle double click - show hack details"""
        item = self.tree.identify("item", event.x, event.y)
        if not item:
            return
            
        tags = self.tree.item(item)["tags"]
        if not tags:
            return
        hack_id = tags[0]
        
        # Find hack data and show details
        for hack in self.filtered_data:
            if str(hack.get("id")) == str(hack_id):
                self._show_hack_details(hack)
                break
    
    def _on_mouse_motion(self, event):
        """Change cursor when hovering over clickable columns"""
        item = self.tree.identify("item", event.x, event.y)
        column = self.tree.identify("column", event.x, event.y)
        
        if item and column in ["#1", "#5", "#6", "#7"]:
            self.tree.config(cursor="hand2")
            
            # ENHANCED: Show rating preview on hover
            if column == "#5":  # Rating column
                self._show_rating_preview(item, event)
        else:
            self.tree.config(cursor="")
            
    def _show_rating_preview(self, item, event):
        """Show preview of which star would be selected"""
        # Get hack data
        tags = self.tree.item(item)["tags"]
        if not tags:
            return
        hack_id = str(tags[0])
        hack_data = self._find_hack_data(hack_id)
        if not hack_data:
            return
            
        # Calculate which star would be selected (same logic as _edit_rating)
        bbox = self.tree.bbox(item, "#5")
        if not bbox:
            return
            
        cell_x = event.x - bbox[0]
        cell_width = bbox[2]
        
        margin = cell_width * 0.02
        usable_width = cell_width - (margin * 2)
        star_zone_width = usable_width / 5
        adjusted_x = cell_x - margin
        
        # Calculate relative position for star mapping
        relative_pos = cell_x / cell_width
        
        # Custom zones based on actual user clicks
        if relative_pos <= 0.30:     # 0-30% = star 1 (your click at 24.8% was star 1)
            preview_rating = 1
        elif relative_pos <= 0.45:   # 30-45% = star 2  
            preview_rating = 2
        elif relative_pos <= 0.60:   # 45-60% = star 3
            preview_rating = 3
        elif relative_pos <= 0.72:   # 60-72% = star 4
            preview_rating = 4
        else:                        # 72-100% = star 5 (your click at 74.3% was star 5)
            preview_rating = 5
        
        # Optional: Update tooltip or status to show preview
        # For now, just ensure the cursor indicates interactivity
        self.tree.config(cursor="hand2")
    
    def _toggle_completed(self, hack_id):
        """Toggle completed status for a hack"""
        hack_id_str = str(hack_id)
        
        # Find hack data
        hack_data = self._find_hack_data(hack_id_str)
        if not hack_data:
            return
        
        # Toggle completed status
        new_completed = not hack_data.get("completed", False)
        
        if self.data_manager.update_hack(hack_id_str, "completed", new_completed):
            hack_data["completed"] = new_completed
            
            # Auto-set/clear completion date ONLY if date field is empty
            if new_completed and not hack_data.get("completed_date"):
                from datetime import datetime
                today = datetime.now().strftime("%Y-%m-%d")
                hack_data["completed_date"] = today
                if self.data_manager.update_hack(hack_id_str, "completed_date", today):
                    self._log(f"✅ Automatically set completion date to {today} for '{hack_data.get('title', 'Unknown')}' (hack #{hack_id_str})", "Debug")
                else:
                    self._log(f"❌ Failed to auto-set completion date for '{hack_data.get('title', 'Unknown')}' (hack #{hack_id_str})", "Error")
            elif not new_completed:
                # Clear the date when unchecking completed
                hack_data["completed_date"] = ""
                if self.data_manager.update_hack(hack_id_str, "completed_date", ""):
                    self._log(f"📅 Cleared completion date for '{hack_data.get('title', 'Unknown')}' (hack #{hack_id_str}) - marked as not completed", "Debug")
                else:
                    self._log(f"❌ Failed to clear completion date for '{hack_data.get('title', 'Unknown')}' (hack #{hack_id_str})", "Error")
            
            # Update the specific tree item directly (same as inline editing)
            for item in self.tree.get_children():
                item_tags = self.tree.item(item)["tags"]
                if item_tags and str(item_tags[0]) == str(hack_id_str):
                    # Get current values
                    current_values = list(self.tree.item(item)["values"])
                    
                    # Update completed checkbox
                    current_values[0] = "✓" if new_completed else ""
                    
                    # Update completion date if it changed
                    current_values[5] = hack_data.get("completed_date", "")
                    
                    # Update the tree item
                    self.tree.item(item, values=current_values)
                    completion_status = "✅ completed" if new_completed else "❌ not completed"
                    self._log(f"🔄 Updated completion status for '{hack_data.get('title', 'Unknown')}' (hack #{hack_id_str}) - now marked as {completion_status}", "Information")
                    break
    
    def _edit_rating(self, hack_id, item, event):
        """Handle rating clicks - improved star detection"""
        hack_id_str = str(hack_id)
        hack_data = self._find_hack_data(hack_id_str)
        if not hack_data:
            return
        
        # Get cell position
        bbox = self.tree.bbox(item, "#5")
        if not bbox:
            return
        
        cell_x = event.x - bbox[0]
        cell_width = bbox[2]
        
        # IMPROVED: Use character-based calculation
        # Each star character is roughly equal width in monospace display
        # Divide cell into 5 equal click zones with small margins
        margin = cell_width * 0.02  # Reduced margin to 2%
        usable_width = cell_width - (margin * 2)
        star_zone_width = usable_width / 5
        adjusted_x = cell_x - margin
        
        # Determine which star zone was clicked
        # Based on actual click testing - adjusted zones to match visual star positions
        relative_pos = cell_x / cell_width
        
        # Custom zones based on actual user clicks
        if relative_pos <= 0.30:     # 0-30% = star 1 (your click at 24.8% was star 1)
            star_position = 1
        elif relative_pos <= 0.45:   # 30-45% = star 2  
            star_position = 2
        elif relative_pos <= 0.60:   # 45-60% = star 3
            star_position = 3
        elif relative_pos <= 0.72:   # 60-72% = star 4
            star_position = 4
        else:                        # 72-100% = star 5 (your click at 74.3% was star 5)
            star_position = 5
        
        self._log(f"🌟 Rating click detected for '{hack_data.get('title', 'Unknown')}' (hack #{hack_id_str}) - position: {relative_pos:.1%}, targeting star {star_position}", "Debug")
        
        # Update rating - if clicking same rating, set to 0 (clear rating)
        current_rating = hack_data.get("personal_rating", 0)
        new_rating = 0 if current_rating == star_position else star_position
        
        if self.data_manager.update_hack(hack_id_str, "personal_rating", new_rating):
            hack_data["personal_rating"] = new_rating
            
            # IMPROVED: Use optimized tree update instead of full refresh
            for tree_item in self.tree.get_children():
                item_tags = self.tree.item(tree_item)["tags"]
                if item_tags and str(item_tags[0]) == str(hack_id_str):
                    # Get current values
                    current_values = list(self.tree.item(tree_item)["values"])
                    
                    # Update rating display
                    current_values[4] = self._get_rating_display(new_rating)
                    
                    # Update the tree item
                    self.tree.item(tree_item, values=current_values)
                    
                    # User-friendly logging
                    if new_rating == 0:
                        self._log(f"⭐ Cleared rating for '{hack_data.get('title', 'Unknown')}' (hack #{hack_id_str})", "Information")
                    else:
                        stars_text = "★" * new_rating + "☆" * (5 - new_rating)
                        self._log(f"⭐ Rated '{hack_data.get('title', 'Unknown')}' (hack #{hack_id_str}) as {new_rating}/5 stars [{stars_text}]", "Information")
                    break
        else:
            self._log(f"❌ Failed to update rating for '{hack_data.get('title', 'Unknown')}' (hack #{hack_id_str}) - data manager update failed", "Error")
    
    def _find_hack_data(self, hack_id_str):
        """Find hack data by ID"""
        for hack in self.filtered_data:
            if hack.get("id") == hack_id_str:
                return hack
        return None
    
    def _show_hack_details(self, hack_data):
        """Show detailed hack information"""
        title = hack_data.get("title", "Unknown Hack")
        details = f"Hack: {title}\n\n"
        
        # Basic info
        details += f"Type: {hack_data.get('hack_type', 'Unknown').title()}\n"
        details += f"Difficulty: {hack_data.get('difficulty', 'Unknown')}\n"
        details += f"Rating: {self._get_rating_display(hack_data.get('personal_rating', 0))}\n"
        
        # Status
        details += f"Completed: {'Yes' if hack_data.get('completed', False) else 'No'}\n"
        if hack_data.get('completed_date'):
            details += f"Completed on: {hack_data.get('completed_date')}\n"
        
        # Special flags
        if hack_data.get('hall_of_fame', False):
            details += "Hall of Fame: Yes\n"
        if hack_data.get('sa1_compatibility', False):
            details += "Uses SA-1 chip: Yes\n"
        if hack_data.get('collaboration', False):
            details += "Collaboration project: Yes\n"
        if hack_data.get('demo', False):
            details += "Demo version: Yes\n"
        
        # Notes
        if hack_data.get('notes'):
            details += f"\nNotes:\n{hack_data.get('notes')}"
        
        messagebox.showinfo(title, details)
    
    def _get_rating_display(self, rating):
        """Convert numeric rating to star display"""
        if rating == 0:
            return "☆☆☆☆☆"
        elif rating == 1:
            return "★☆☆☆☆"
        elif rating == 2:
            return "★★☆☆☆"
        elif rating == 3:
            return "★★★☆☆"
        elif rating == 4:
            return "★★★★☆"
        elif rating == 5:
            return "★★★★★"
        else:
            return "☆☆☆☆☆"
    
    def _format_time_display(self, seconds):
        """Convert seconds to readable time format (HH:MM:SS or MM:SS)"""
        if seconds == 0:
            return ""  # Empty if not set
        
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        else:
            return f"{minutes:02d}:{secs:02d}"
    
    def _parse_time_input(self, time_str):
        """Parse user time input and convert to seconds"""
        if not time_str or time_str.strip() == "":
            return 0
        
        time_str = time_str.strip()
        
        # Support flexible input formats
        # HH:MM:SS, MM:SS, MM, "2h 30m", "90m", "150 minutes", etc.
        
        import re
        
        # Pattern for "2h 30m 15s" or "2h 30m" or "90m" etc. - must have letter suffix
        pattern_units = re.match(r'(?:(\d+)h\s*)?(?:(\d+)m\s*)?(?:(\d+)s\s*)?$', time_str.lower())
        if pattern_units and any(pattern_units.groups()) and re.search(r'[hms]', time_str.lower()):
            hours = int(pattern_units.group(1) or 0)
            minutes = int(pattern_units.group(2) or 0) 
            seconds = int(pattern_units.group(3) or 0)
            return hours * 3600 + minutes * 60 + seconds
        
        # Pattern for "150 minutes" or "90 mins"
        pattern_minutes = re.match(r'(\d+)\s*(?:minutes?|mins?)$', time_str.lower())
        if pattern_minutes:
            return int(pattern_minutes.group(1)) * 60
        
        # Pattern for "HH:MM:SS" or "MM:SS"
        if ':' in time_str:
            parts = time_str.split(':')
            try:
                if len(parts) == 3:  # HH:MM:SS
                    hours, minutes, seconds = map(int, parts)
                    return hours * 3600 + minutes * 60 + seconds
                elif len(parts) == 2:  # MM:SS
                    minutes, seconds = map(int, parts)
                    return minutes * 60 + seconds
            except ValueError:
                pass
        
        # Just a number - assume minutes
        if time_str.isdigit():
            return int(time_str) * 60
        
        raise ValueError(f"Invalid time format: {time_str}")
    
    def _validate_time_input(self, time_str):
        """Validate and convert time input to seconds for storage"""
        try:
            seconds = self._parse_time_input(time_str)
            if seconds < 0:
                from tkinter import messagebox
                messagebox.showerror("Invalid Time", "Time cannot be negative")
                return None
            if seconds > 999 * 3600:  # 999 hours max
                from tkinter import messagebox
                messagebox.showerror("Invalid Time", "Time cannot exceed 999 hours")
                return None
            return seconds
        except ValueError as e:
            from tkinter import messagebox
            messagebox.showerror("Invalid Time", 
                               f"Invalid time format.\n\n"
                               f"Valid formats include:\n"
                               f"• HH:MM:SS (e.g., 1:30:45)\n"
                               f"• MM:SS (e.g., 90:30)\n"
                               f"• 2h 30m (e.g., 1h 30m 15s)\n"
                               f"• 90m or 90 minutes\n"
                               f"• 90 (assumes minutes)")
            return None
    
    def _toggle_h_scrollbar(self, scrollbar):
        """Show/hide horizontal scrollbar based on content"""
        tree_width = self.tree.winfo_width()
        content_width = sum(self.tree.column(col)["width"] for col in self.tree["columns"])
        
        if content_width > tree_width:
            scrollbar.grid(row=1, column=0, sticky="ew")
        else:
            scrollbar.grid_remove()



