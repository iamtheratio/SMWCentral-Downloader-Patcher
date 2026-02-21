import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os
import platform
import subprocess
import shlex
import re
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from hack_data_manager import HackDataManager
from ui.collection_components import InlineEditor, DateValidator, NotesValidator, HackCollectionInlineEditor
from ui.components.table_filters import TableFilters
from ui_constants import get_page_padding, get_section_padding
from file_explorer_utils import open_file_in_explorer, get_file_icon_unicode

# Info icon unicode (using standard info symbol)
INFO_ICON = "ℹ"
from config_manager import ConfigManager

# Platform-specific cursor
HOVER_CURSOR = "pointinghand" if platform.system() == "Darwin" else "hand2"
from utils import get_sorted_folder_name, move_hack_to_new_difficulty, get_primary_type, format_types_display
from colors import get_colors

# Import VERSION from main module
try:
    from main import VERSION
except ImportError:
    from version_manager import get_version
    VERSION = get_version()

class CollectionPage:
    """Simplified hack collection page with extracted components"""
    
    def __init__(self, parent, logger=None):
        self.parent = parent
        self.frame = None
        self.logger = logger  # Add logger support
        self.data_manager = HackDataManager(logger=logger)
        
        # v3.1 NEW: Pagination state
        self.current_page = 1
        self.page_size = 50  # Default page size
        self.total_pages = 1
        
        # Sorting state - Default to title ascending
        self.sort_column = "title"
        self.sort_reverse = False
        
        # Column Configuration (ID, Header, Width, MinWidth, Anchor)
        # DEFAULT_COLUMNS stores the original default order - never modified
        self.DEFAULT_COLUMNS = [
            {"id": "completed", "header": "✓", "width": 45, "min_width": 35, "anchor": "center"},
            {"id": "play", "header": "▶", "width": 35, "min_width": 25, "anchor": "center"},
            {"id": "folder", "header": get_file_icon_unicode(), "width": 35, "min_width": 25, "anchor": "center"},
            {"id": "title", "header": "Title", "width": 220, "min_width": 170, "anchor": "w"},
            {"id": "type", "header": "Type(s)", "width": 90, "min_width": 70, "anchor": "center"},
            {"id": "difficulty", "header": "Difficulty", "width": 100, "min_width": 80, "anchor": "center"},
            {"id": "rating", "header": "Rating", "width": 90, "min_width": 70, "anchor": "center"},
            {"id": "completed_date", "header": "Completed Date", "width": 110, "min_width": 90, "anchor": "center"},
            {"id": "time_to_beat", "header": "Time to Beat", "width": 120, "min_width": 100, "anchor": "center"},
            {"id": "release_date", "header": "Released", "width": 100, "min_width": 80, "anchor": "center"}, # NEW
            {"id": "notes", "header": "Notes", "width": 120, "min_width": 90, "anchor": "w"}
        ]
        
        # COLUMNS is the working copy that can be reordered based on user config
        self.COLUMNS = [col.copy() for col in self.DEFAULT_COLUMNS]
        
        # Load column visibility and order from config
        from config_manager import ConfigManager
        self.config_manager = ConfigManager()
        
        # Load visible columns and column order from config
        self.visible_columns = self.config_manager.get("visible_columns", [c["id"] for c in self.COLUMNS])
        column_order = self.config_manager.get("column_order", None)
        
        # If we have a saved column order, use it; otherwise use default order
        if column_order:
            ordered_columns = []
            # Add columns in saved order
            for col_id in column_order:
                col_def = next((c for c in self.COLUMNS if c["id"] == col_id), None)
                if col_def:
                    ordered_columns.append(col_def)
            
            # Add any new columns that might not be in saved order (for backward compatibility)
            existing_ids = [col["id"] for col in ordered_columns]
            for col in self.COLUMNS:
                if col["id"] not in existing_ids:
                    ordered_columns.append(col)
            
            self.COLUMNS = ordered_columns
        
        # Initialize components - USE HackCollectionInlineEditor instead of InlineEditor
        self.filters = TableFilters(self._apply_filters, self._select_random_hack)
        self.date_editor = HackCollectionInlineEditor(None, self.data_manager, self, logger)
        self.notes_editor = HackCollectionInlineEditor(None, self.data_manager, self, logger)
        self.time_editor = HackCollectionInlineEditor(None, self.data_manager, self, logger)  # v3.1 NEW
        
        # Track open dialogs to prevent duplicates
        self.column_config_dialog = None
        
        # Debounce timer for scrollbar toggle
        self.scrollbar_toggle_timer = None
        
        # Table and data
        self.tree = None
        self.filtered_data = []
        self.status_label = None
        
        # Cache ConfigManager instance and emulator path for performance
        self.config_manager = ConfigManager()
        self._emulator_path = self.config_manager.get("emulator_path", "")
    
    def refresh_emulator_cache(self):
        """Refresh cached emulator settings - called when settings change"""
        old_path = self._emulator_path
        # Create NEW ConfigManager instance to reload config from disk
        self.config_manager = ConfigManager()
        self._emulator_path = self.config_manager.get("emulator_path", "")
        self._log(f"🔄 Emulator cache refreshed: '{old_path}' -> '{self._emulator_path}'", "Debug")
        # Refresh table to update play icons
        if self.tree:
            self._log("🔄 Refreshing collection table to update play icons...", "Debug")
            self._refresh_table()
        else:
            self._log("⚠️ Tree not initialized yet, skipping table refresh", "Debug")
    
    def _log(self, message, level="Information"):
        """Log a message if logger is available"""
        if self.logger:
            self.logger.log(message, level)
        
    def create(self):
        """Create the hack collection page"""
        self.frame = ttk.Frame(self.parent, padding=get_page_padding())
        
        # Create filter section
        _, section_padding_y = get_section_padding()
        filter_frame = self.filters.create_filter_ui(self.frame, self.data_manager)
        filter_frame.pack(fill="x", pady=(0, section_padding_y))
        
        # Create download status indicator
        self.status_frame = ttk.Frame(self.frame)
        self.status_frame.pack(fill="x", pady=(0, 5))
        
        self.download_status_label = ttk.Label(
            self.status_frame, 
            text="", 
            font=("Segoe UI", 9, "bold"),
            foreground="#FF6B6B"  # Red color for warning
        )
        self.download_status_label.pack()
        
        # Register for download state changes
        try:
            from download_state_manager import register_callback
            register_callback(self._on_download_state_change)
        except ImportError:
            pass  # Download state manager not available
        
        # Connect refresh button
        # (This is a bit hacky but keeps the component simple)
        for widget in filter_frame.winfo_children():
            if isinstance(widget, ttk.Frame):
                for child in widget.winfo_children():
                    if isinstance(child, ttk.Frame):
                        for grandchild in child.winfo_children():
                            if isinstance(grandchild, ttk.Button) and "Refresh" in grandchild.cget("text"):
                                grandchild.configure(command=self._refresh_data_and_table)
        
        # v3.1 NEW: Create pagination controls
        self._create_pagination_controls()
        
        # Create table section
        self._create_table()
        
        # Load initial data
        self._refresh_data_and_table()
        
        return self.frame
    
    def show(self):
        """Called when the page becomes visible"""
        if self.frame:
            # Only refresh when showing - don't duplicate if user just clicked refresh
            # Check if we need to refresh (e.g., returning from another page)
            total_hacks = len(self.data_manager.get_all_hacks())
            completed_hacks = sum(1 for hack in self.data_manager.get_all_hacks() if hack.get("completed", False))
            self._log(f"📊 Hack Collection page loaded - {total_hacks} total hacks, {completed_hacks} completed", "Information")
    
    def hide(self):
        """Called when the page becomes hidden"""
        self.date_editor.cleanup()
        self.notes_editor.cleanup()
        self.time_editor.cleanup()  # v3.1 NEW
    
    def cleanup(self):
        """Clean up resources and ensure data is saved"""
        # Unregister download state callback
        try:
            from download_state_manager import unregister_callback
            unregister_callback(self._on_download_state_change)
        except ImportError:
            pass
            
        # Force save any pending changes
        self.data_manager.force_save()
    
    def _on_download_state_change(self, download_active):
        """Handle download state changes"""
        if hasattr(self, 'download_status_label') and self.download_status_label:
            if download_active:
                self.download_status_label.config(
                    text="⚠️ Download in progress - Collection editing is temporarily disabled",
                    foreground="#FF6B6B"  # Red
                )
            else:
                self.download_status_label.config(text="", foreground="#4ECDC4")  # Clear text
    
    def _create_table(self):
        """Create the main data table"""
        table_frame = ttk.Frame(self.frame)
        table_frame.pack(fill="both", expand=True)
        
        # Create treeview with custom Collection style
        column_ids = [col["id"] for col in self.COLUMNS]
        self.tree = ttk.Treeview(table_frame, columns=column_ids, show="headings", height=15, style="Collection.Treeview")
        
        # Configure headers and columns
        for col_config in self.COLUMNS:
            col_id = col_config["id"]
            self.tree.heading(col_id, text=col_config["header"], command=lambda c=col_id: self._sort_by_column(c))
            self.tree.column(col_id, width=col_config["width"], minwidth=col_config["min_width"], anchor=col_config["anchor"])
            
        # Set initial visibility
        self.tree["displaycolumns"] = self.visible_columns
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.h_scrollbar = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=self.h_scrollbar.set)
        
        # Grid layout
        self.tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        self.h_scrollbar.grid_remove()
        
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
        self.tree.bind("<Configure>", lambda e: self._toggle_h_scrollbar(self.h_scrollbar))
        
        # Status label - positioned in a footer frame after pagination
        footer_frame = ttk.Frame(self.frame)
        footer_frame.pack(fill="x", pady=(23, 0))  # Increased top padding from 5 to 20
        
        self.status_label = ttk.Label(footer_frame, text="", font=("Segoe UI", 9))
        self.status_label.pack(anchor="center")
    
    def _refresh_data_and_table(self):
        """Reload all data and refresh the table"""
        # Guard against duplicate calls
        if hasattr(self, '_is_refreshing') and self._is_refreshing:
            self._log("DEBUG: Skipping duplicate refresh call", "Debug")
            return
        
        self._is_refreshing = True
        
        try:
            # Debug: Add stack trace to find duplicate calls
            import traceback
            stack_summary = traceback.extract_stack()
            self._log(f"DEBUG: _refresh_data_and_table called from {stack_summary[-2].filename.split('/')[-1].split(chr(92))[-1]}:{stack_summary[-2].lineno}", "Debug")
            
            self.config_manager.reload()  # Reload config to get latest emulator settings
            # CRITICAL: Force save any pending changes before refreshing to prevent data loss
            if hasattr(self.data_manager, 'unsaved_changes') and self.data_manager.unsaved_changes:
                self._log("💾 Saving pending changes before refresh to prevent data loss...", "Information")
                if self.data_manager.force_save():
                    pass # Saved successfully
                else:
                    self._log("❌ Failed to save changes before refresh", "Error")
            
            # Reload data from disk to pick up external changes (e.g. metadata fetch)
            self.data_manager.reload_data()
            self.filters.refresh_dropdown_values(self.data_manager)
            
            # Apply filters and sorting
            self._apply_filters()
            self._refresh_table()
            
            self._log(f"🔄 Refreshed hack data from file", "Debug")
        finally:
            self._is_refreshing = False
    
    def _refresh_table(self):
        """Refresh table data with pagination and sorting"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Get filtered data - include obsolete hacks so table filters can handle them
        all_hacks = self.data_manager.get_all_hacks(include_obsolete=True)
        self.filtered_data = self.filters.apply_filters(all_hacks)
        
        # Apply sorting
        self._sort_filtered_data()
        
        # Update column headers to show sort indicators
        self._update_column_headers()
        
        # Calculate pagination
        total_hacks = len(self.filtered_data)
        self.total_pages = max(1, (total_hacks + self.page_size - 1) // self.page_size)
        
        # Ensure current page is valid
        if self.current_page > self.total_pages:
            self.current_page = self.total_pages
            self.page_var.set(str(self.current_page))
        
        # Calculate page slice
        start_index = (self.current_page - 1) * self.page_size
        end_index = min(start_index + self.page_size, total_hacks)
        page_data = self.filtered_data[start_index:end_index]
        
        # Populate table with page data
        for hack in page_data:
            self._insert_hack_row(hack)
        
        # Update status with pagination info
        if total_hacks > self.page_size:
            sort_info = f" (sorted by {self.sort_column})" if self.sort_column else ""
            status_text = f"Showing {len(page_data)} of {total_hacks} hack(s) (Page {self.current_page} of {self.total_pages}){sort_info}"
        else:
            sort_info = f" (sorted by {self.sort_column})" if self.sort_column else ""
            status_text = f"Displaying {total_hacks} hack(s){sort_info}"
        self._update_status_label(len(all_hacks), total_hacks, status_text)
        
        # Update pagination controls
        self._update_pagination_controls()
    
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
        
        # Use new helper function for type display
        hack_types = hack.get("hack_types", []) or [hack.get("hack_type", "standard")]
        type_display = format_types_display(hack_types)
        
        # Check if hack file exists for folder icon display
        file_path = hack.get("file_path", "")
        folder_icon = get_file_icon_unicode() if file_path and os.path.exists(file_path) else ""
        
        # Check if emulator is configured for play icon display
        play_icon = self._get_play_icon(hack)
        
        release_date = hack.get("date", "")
        if not release_date and hack.get("time"):
            try:
                from datetime import datetime
                ts = int(hack.get("time"))
                release_date = datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
            except:
                pass

        # Prepare values dict for easy mapping
        row_data = {
            "completed": completed_display,
            "play": play_icon,
            "folder": folder_icon,
            "title": hack["title"],
            "type": type_display,
            "difficulty": hack.get("difficulty", "Unknown"),
            "rating": rating_display,
            "completed_date": hack.get("completed_date", ""),
            "time_to_beat": time_to_beat_display,
            "release_date": release_date,  # Updated
            "notes": notes_display
        }
        
        # Build values tuple in correct order based on currently configured columns
        values = [row_data.get(col["id"], "") for col in self.COLUMNS]
        
        self.tree.insert("", "end", values=values, tags=(hack_id,))
    
    def _update_status_label(self, total_count, filtered_count, custom_text=None):
        """Update the status label"""
        if custom_text:
            # Use custom text when provided (for pagination)
            status_text = custom_text
        else:
            # Use default format
            completed_count = sum(1 for hack in self.filtered_data if hack.get("completed", False))
            status_text = f"Showing {filtered_count} of {total_count} hacks"
            if filtered_count > 0:
                status_text += f" • {completed_count} completed"
        self.status_label.config(text=status_text)
    
    def _apply_filters(self):
        """Apply filters and refresh table"""
        self._refresh_table()

    def _select_random_hack(self):
        """Select a random hack from the current filtered list and jump to it"""
        import random
        
        # Check if there are any hacks to select from
        if not self.filtered_data:
            messagebox.showinfo("Random Hack", "No hacks available in the current list.")
            return

        # Pick a random hack
        selected_hack = random.choice(self.filtered_data)
        hack_id = selected_hack.get("id")
        title = selected_hack.get("title", "Unknown")
        
        self._log(f"🎲 Randomly selected hack: '{title}' (ID: {hack_id})", "Information")
        
        # Find which page this hack is on
        # We need to find the index of the hack in the filtered data
        try:
            hack_index = self.filtered_data.index(selected_hack)
            
            # Calculate page number (1-based)
            target_page = (hack_index // self.page_size) + 1
            
            # Switch to that page if needed
            if target_page != self.current_page:
                self.current_page = target_page
                self.page_var.set(str(self.current_page))
                self._refresh_table() # This will populate the tree with the correct page data
                
            # Scroll to and select the item in the tree
            self._select_hack_in_tree(hack_id)
            
        except ValueError:
            self._log(f"❌ Failed to find selected hack '{title}' in filtered data", "Error")

    def _select_hack_in_tree(self, hack_id):
        """Find a hack in the current tree view, select it, and ensure it's visible"""
        hack_id_str = str(hack_id)
        
        # Iterate through tree items to find the match
        for item in self.tree.get_children():
            tags = self.tree.item(item)["tags"]
            if tags and str(tags[0]) == hack_id_str:
                # Found it!
                self.tree.selection_set(item)
                self.tree.focus(item)
                self.tree.see(item)
                return
        
        self._log(f"⚠️ Could not find hack {hack_id} in tree view", "Warning")
    
    def _on_item_click(self, event):
        """Handle single clicks on table items"""
        # Check if download is active - prevent editing during downloads
        try:
            from download_state_manager import is_download_active
            if is_download_active():
                messagebox.showwarning(
                    "Download in Progress", 
                    "Cannot edit hack collection while a download is in progress.\n\n"
                    "Please wait for the download to complete or cancel it before making changes."
                )
                return
        except ImportError:
            pass  # If download state manager not available, allow editing
        
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
        
        hack_id = tags[0]
        
        col_id = self._get_column_id(column)
        if not col_id:
            return

        # Handle different column clicks
        if col_id == "completed":
            self._toggle_completed(hack_id)
        elif col_id == "play":
            self._launch_emulator(hack_id)
        elif col_id == "folder":
            self._open_hack_in_explorer(hack_id)
        elif col_id == "rating":
            self._edit_rating(hack_id, item, event, col_id)
        elif col_id == "completed_date":
            self.date_editor.start_edit(hack_id, item, event, "completed_date", col_id, DateValidator.validate)
        elif col_id == "time_to_beat":
            self.time_editor.start_edit(hack_id, item, event, "time_to_beat", col_id, self._validate_time_input)
        elif col_id == "notes":
            self.notes_editor.start_edit(hack_id, item, event, "notes", col_id, NotesValidator.validate)

    def _get_column_id(self, col_idx_str):
        """Convert treeview column index (e.g. '#1') to logical column ID"""
        try:
            # Extract index (1-based)
            idx = int(col_idx_str.replace("#", "")) - 1
            
            # Check if index is valid for current columns
            if 0 <= idx < len(self.COLUMNS):
                return self.COLUMNS[idx]["id"]
            return None
        except (ValueError, IndexError):
            return None
    
    def _on_item_double_click(self, event):
        """Handle double click - show edit hack dialog"""
        # Check if download is active - prevent editing during downloads
        try:
            from download_state_manager import is_download_active
            if is_download_active():
                messagebox.showwarning(
                    "Download in Progress", 
                    "Cannot edit hack collection while a download is in progress.\n\n"
                    "Please wait for the download to complete or cancel it before making changes."
                )
                return
        except ImportError:
            pass  # If download state manager not available, allow editing
            
        item = self.tree.identify("item", event.x, event.y)
        if not item:
            return
            
        tags = self.tree.item(item)["tags"]
        if not tags:
            return
        hack_id = tags[0]
        
        # Find hack data and show edit dialog
        for hack in self.filtered_data:
            if str(hack.get("id")) == str(hack_id):
                self.filters.show_edit_hack_dialog(hack, hack_id)
                break
    
    def _on_mouse_motion(self, event):
        """Change cursor when hovering over clickable columns"""
        item = self.tree.identify("item", event.x, event.y)
        column = self.tree.identify("column", event.x, event.y)
        
        col_id = self._get_column_id(column)
        clickable_cols = ["completed", "play", "folder", "info", "rating", "completed_date", "time_to_beat", "notes"]
        
        if item and col_id in clickable_cols:
            self.tree.config(cursor=HOVER_CURSOR)
            
            # ENHANCED: Show rating preview on hover
            if col_id == "rating":
                self._show_rating_preview(item, event, column)
        else:
            self.tree.config(cursor="")

    def _show_info_dialog(self, hack_id):
        """Show the hack info dialog"""
        hack_data = self._find_hack_data(str(hack_id))
        if hack_data:
            dialog = HackInfoDialog(self.parent, hack_data)
            dialog.show()
            
    def _show_column_config(self):
        """Show column configuration dialog"""
        # Prevent multiple dialogs from opening
        if self.column_config_dialog is not None:
            try:
                # If dialog still exists, focus it instead of opening a new one
                self.column_config_dialog.dialog.lift()
                self.column_config_dialog.dialog.focus_force()
                return
            except:
                # Dialog was closed, reset the reference
                self.column_config_dialog = None
        
        from ui.components.column_config_dialog import ColumnConfigDialog
        
        self.column_config_dialog = ColumnConfigDialog(
            self.parent,
            self.COLUMNS,
            self.visible_columns,
            self._apply_column_config,
            self.config_manager,
            self.DEFAULT_COLUMNS  # Pass original default order
        )
        
        # Clear reference when dialog is closed
        def on_dialog_close():
            self.column_config_dialog = None
        
        self.column_config_dialog.show()
        
        # Bind to dialog destruction to clear reference
        if self.column_config_dialog.dialog:
            self.column_config_dialog.dialog.bind("<Destroy>", lambda e: on_dialog_close())
        
    def _apply_column_config(self, new_visible_cols):
        """Apply new column configuration"""
        self.visible_columns = new_visible_cols
        
        # Reload config to get updated column_order and visible_columns
        self.config_manager.reload()
        column_order = self.config_manager.get("column_order", None)
        updated_visible = self.config_manager.get("visible_columns", new_visible_cols)
        
        # Reorder COLUMNS based on column_order (if available)
        if column_order:
            ordered_columns = []
            for col_id in column_order:
                col_def = next((c for c in self.COLUMNS if c["id"] == col_id), None)
                if col_def:
                    ordered_columns.append(col_def)
            
            # Add any new columns not in saved order
            existing_ids = [col["id"] for col in ordered_columns]
            for col in self.COLUMNS:
                if col["id"] not in existing_ids:
                    ordered_columns.append(col)
            
            self.COLUMNS = ordered_columns
        
        # Update table visibility
        self.tree["displaycolumns"] = updated_visible
        
        # Force scrollbar update after column change
        self.tree.update_idletasks()
        self._toggle_h_scrollbar(self.h_scrollbar)
            
    def _show_rating_preview(self, item, event, col_idx_str):
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
        # Use the column index string passed from event
        bbox = self.tree.bbox(item, col_idx_str)
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
        self.tree.config(cursor=HOVER_CURSOR)
    
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
                    
                    # Update completed checkbox (respect current column ordering)
                    try:
                        completed_col_idx = next(i for i, c in enumerate(self.COLUMNS) if c["id"] == "completed")
                        current_values[completed_col_idx] = "✓" if new_completed else ""
                    except StopIteration:
                        # "completed" column might be hidden or missing
                        pass
                    
                    # Update completion date if it changed dynamically
                    try:
                        date_col_idx = next(i for i, c in enumerate(self.COLUMNS) if c["id"] == "completed_date")
                        current_values[date_col_idx] = hack_data.get("completed_date", "")
                    except StopIteration:
                        pass # Column might be hidden/missing
                    
                    # Update the tree item
                    self.tree.item(item, values=current_values)
                    completion_status = "✅ completed" if new_completed else "❌ not completed"
                    self._log(f"🔄 Updated completion status for '{hack_data.get('title', 'Unknown')}' (hack #{hack_id_str}) - now marked as {completion_status}", "Information")
                    break
    
    def _edit_rating(self, hack_id, item, event, col_id="rating"):
        """Handle rating clicks - improved star detection"""
        hack_id_str = str(hack_id)
        hack_data = self._find_hack_data(hack_id_str)
        if not hack_data:
            return
        
        # Get cell position using column ID
        bbox = self.tree.bbox(item, col_id)
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
                    
                    # Update rating in the correct column dynamically
                    try:
                        rating_col_idx = next(i for i, c in enumerate(self.COLUMNS) if c["id"] == "rating")
                        current_values[rating_col_idx] = self._get_rating_display(new_rating)
                    except StopIteration:
                        pass
                    
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
    
    def _open_hack_in_explorer(self, hack_id):
        """Open the hack file location in the system file explorer"""
        
        hack_data = self._find_hack_data(hack_id)
        if not hack_data:
            return
        
        file_path = hack_data.get("file_path", "")
        hack_title = hack_data.get("title", "Unknown")
        
        # Silently return if no file path (hack not downloaded) - don't show error
        if not file_path:
            return
        
        # Only show error if file_path exists but file is missing (was moved/deleted)
        if not os.path.exists(file_path):
            self._log(f"⚠️ File not found: {file_path} for '{hack_title}'", "Warning")
            messagebox.showwarning(
                "File Not Found",
                f"The file for '{hack_title}' could not be found:\n\n"
                f"{file_path}\n\n"
                f"The file may have been moved or deleted."
            )
            return
        
        # Try to open the file in the system explorer
        success = open_file_in_explorer(file_path)
        
        if success:
            self._log(f"📂 Opened file location for '{hack_title}' in system explorer", "Information")
        else:
            # Fallback message if the explorer couldn't be opened
            self._log(f"❌ Failed to open file explorer for '{hack_title}'", "Error")
            messagebox.showerror(
                "Explorer Error",
                f"Could not open file explorer for '{hack_title}'.\n\n"
                f"File path: {file_path}"
            )
    
    def _get_play_icon(self, hack):
        """Get play icon if emulator is configured and file exists"""
        # Only show play icon if emulator is configured and file exists
        # Use cached emulator path for performance
        file_path = hack.get("file_path", "")
        if self._emulator_path and file_path and os.path.exists(file_path):
            return "▶"
        return ""
    
    def _convert_app_to_executable(self, app_path):
        """Convert macOS .app bundle path to actual executable path"""
        # Extract app name from path
        app_name = os.path.basename(app_path).replace(".app", "")
        
        # Standard macOS app structure: AppName.app/Contents/MacOS/AppName
        executable_path = os.path.join(app_path, "Contents", "MacOS", app_name)
        
        # Check if the standard executable exists
        if os.path.exists(executable_path):
            self._log(f"Converted .app bundle to executable: {executable_path}", "Debug")
            return executable_path
        
        # Fallback: Try to find any executable in Contents/MacOS/
        macos_dir = os.path.join(app_path, "Contents", "MacOS")
        if os.path.exists(macos_dir):
            for file in os.listdir(macos_dir):
                file_path = os.path.join(macos_dir, file)
                if os.path.isfile(file_path) and os.access(file_path, os.X_OK):
                    self._log(f"Found executable in .app bundle: {file_path}", "Debug")
                    return file_path
        
        # If no executable found, return original path with warning
        self._log(f"Could not find executable in .app bundle, using bundle path", "Warning")
        return app_path
    
    def _parse_emulator_args(self, args_string):
        """Parse emulator arguments string into a list, handling platform-specific quoting.
        
        Args:
            args_string: String containing emulator arguments
            
        Returns:
            List of parsed argument strings
        """
        if platform.system() == "Windows":
            # Windows: Split by spaces but keep quoted strings together
            # Use a more efficient regex pattern to avoid ReDoS vulnerability
            parts = re.findall(r'[^\s"]+|"[^"]*"', args_string)
            # Remove quotes only from fully-quoted strings
            return [p[1:-1] if p.startswith('"') and p.endswith('"') else p for p in parts]
        else:
            # Unix: use shlex for proper quote handling
            return shlex.split(args_string)

    def _normalize_emulator_arg(self, arg):
        """Normalize a single emulator argument token (expand ~, env vars, and common macOS RetroArch mistakes)."""
        if not arg:
            return arg

        expanded = os.path.expanduser(os.path.expandvars(arg))

        # Common macOS path typo: "Application/Support" instead of "Application Support"
        if platform.system() == "Darwin" and "/Library/Application/Support/" in expanded:
            alt = expanded.replace("/Library/Application/Support/", "/Library/Application Support/")
            # Prefer the correct path if it exists; otherwise fall back only if original exists.
            if os.path.exists(alt) or not os.path.exists(expanded):
                expanded = alt

        # Common macOS RetroArch core extension mismatch: .dll -> .dylib
        if platform.system() == "Darwin" and expanded.lower().endswith(".dll"):
            alt = expanded[:-4] + ".dylib"
            if os.path.exists(alt) and not os.path.exists(expanded):
                expanded = alt

        return expanded

    def _build_emulator_command(self, emulator_path, emulator_args, emulator_args_enabled, rom_path):
        """Build a safe subprocess command list for launching the emulator."""
        command = [emulator_path]
        rom_added = False

        if emulator_args_enabled and emulator_args:
            placeholders = ("%1", "$1", "{rom}", "{ROM}")
            if any(ph in emulator_args for ph in placeholders):
                args_with_rom = emulator_args
                for ph in placeholders:
                    args_with_rom = args_with_rom.replace(ph, rom_path)
                parsed = self._parse_emulator_args(args_with_rom)
                rom_added = True
            else:
                parsed = self._parse_emulator_args(emulator_args)

            normalized = [self._normalize_emulator_arg(a) for a in parsed]

            # Users sometimes paste a full command line including the emulator path.
            # If the first token matches the emulator executable (or macOS .app bundle), drop it.
            if normalized:
                try:
                    first = os.path.normpath(normalized[0])
                    exe_norm = os.path.normpath(emulator_path)
                    bundle_path = self._find_macos_app_bundle(emulator_path)
                    bundle_norm = os.path.normpath(bundle_path) if bundle_path else None

                    if first == exe_norm or (bundle_norm and first == bundle_norm):
                        normalized = normalized[1:]
                except Exception:
                    pass

            command.extend(normalized)

        if not rom_added:
            command.append(rom_path)

        return command

    def _find_macos_app_bundle(self, executable_path):
        """If executable_path is inside a .app bundle, return the bundle path, else None."""
        if platform.system() != "Darwin" or not executable_path:
            return None

        # Typical layout: <App>.app/Contents/MacOS/<binary>
        marker = ".app/Contents/MacOS/"
        idx = executable_path.find(marker)
        if idx == -1:
            return None

        bundle_path = executable_path[: idx + len(".app")]
        if os.path.isdir(bundle_path):
            return bundle_path
        return None
    
    def _launch_emulator(self, hack_id):
        """Launch the emulator with the ROM file"""
        hack_data = self._find_hack_data(hack_id)
        if not hack_data:
            return
        
        file_path = hack_data.get("file_path", "")
        hack_title = hack_data.get("title", "Unknown")
        
        # Check if file exists
        if not file_path or not os.path.exists(file_path):
            self._log(f"⚠️ Cannot launch '{hack_title}' - file not found", "Warning")
            messagebox.showwarning(
                "File Not Found",
                f"The ROM file for '{hack_title}' could not be found:\n\n"
                f"{file_path}\n\n"
                f"The file may have been moved or deleted."
            )
            return
        
        # Load emulator configuration from cached instance
        emulator_path = (self.config_manager.get("emulator_path", "") or "").strip()
        emulator_args = self.config_manager.get("emulator_args", "")
        emulator_args_enabled = self.config_manager.get("emulator_args_enabled", False)

        system = platform.system()

        # macOS: Convert .app bundle to executable if needed
        if system == "Darwin" and emulator_path:
            # Normalize possible trailing slash and handle case-insensitive suffix
            emulator_path_normalized = emulator_path.rstrip("/")
            if emulator_path_normalized.lower().endswith(".app") and os.path.isdir(emulator_path_normalized):
                emulator_path = self._convert_app_to_executable(emulator_path_normalized)
        
        if not emulator_path:
            self._log("⚠️ No emulator configured", "Warning")
            messagebox.showwarning(
                "No Emulator Configured",
                "Please configure an emulator in Settings before launching games."
            )
            return
        
        if not os.path.exists(emulator_path):
            self._log(f"⚠️ Emulator not found: {emulator_path}", "Warning")
            messagebox.showwarning(
                "Emulator Not Found",
                f"The configured emulator could not be found:\n\n"
                f"{emulator_path}\n\n"
                f"Please check your emulator settings."
            )
            return
        
        # Security: Validate emulator path points to an actual file (not a directory)
        if not os.path.isfile(emulator_path):
            self._log(f"⚠️ Emulator path is not a file: {emulator_path}", "Warning")
            messagebox.showwarning(
                "Invalid Emulator",
                f"The configured emulator path is not a valid file:\n\n"
                f"{emulator_path}\n\n"
                f"Please configure a valid emulator executable in Settings."
            )
            return
        
        # Security: Normalize path first to prevent bypassing validation
        emulator_path = os.path.normpath(emulator_path)
        if not os.path.isabs(emulator_path):
            self._log(f"⚠️ Emulator path must be absolute: {emulator_path}", "Warning")
            messagebox.showwarning(
                "Invalid Emulator Path",
                f"The configured emulator path must be an absolute path.\n\n"
                f"Please configure a valid emulator path in Settings."
            )
            return
        
        # Security: Check if file is executable
        if platform.system() == "Windows":
            # Windows: Validate file has an executable extension
            valid_extensions = ('.exe', '.bat', '.cmd', '.com')
            if not emulator_path.lower().endswith(valid_extensions):
                self._log(f"⚠️ Emulator is not a valid executable: {emulator_path}", "Warning")
                messagebox.showwarning(
                    "Invalid Emulator",
                    f"The configured emulator must be a valid executable file (.exe, .bat, .cmd, or .com):\n\n"
                    f"{emulator_path}\n\n"
                    f"Please configure a valid emulator in Settings."
                )
                return
        else:
            # Unix/macOS: Check if file is executable
            if not os.access(emulator_path, os.X_OK):
                self._log(f"⚠️ Emulator is not executable: {emulator_path}", "Warning")
                messagebox.showwarning(
                    "Emulator Not Executable",
                    f"The configured emulator is not executable:\n\n"
                    f"{emulator_path}\n\n"
                    f"Please check file permissions or configure a valid emulator."
                )
                return
        
        # Security: Validate emulator path doesn't contain dangerous shell metacharacters
        # This prevents paths like "/bin/sh;malicious" or "cmd.exe|evil"
        # Note: We allow spaces and normal path characters like (), {}, [], *, ? which may appear
        # in legitimate Windows paths (e.g., "Program Files (x86)"). Since we use shell=False,
        # these won't be interpreted as shell metacharacters.
        dangerous_chars = [';', '|', '&', '>', '<', '`', '\n', '\r', '$']
        if any(char in emulator_path for char in dangerous_chars):
            self._log(f"⚠️ Emulator path contains invalid characters: {emulator_path}", "Warning")
            messagebox.showwarning(
                "Invalid Emulator Path",
                f"The configured emulator path contains invalid characters.\n\n"
                f"Please configure a valid emulator path in Settings."
            )
            return
        
        try:
            command = self._build_emulator_command(
                emulator_path=emulator_path,
                emulator_args=emulator_args,
                emulator_args_enabled=emulator_args_enabled,
                rom_path=file_path,
            )

            # Log the exact command for debugging
            self._log(f"Launching emulator command: {command}", "Debug")

            # macOS: Prefer launching GUI apps via `open -a` when using a .app bundle.
            # This avoids cases where executing the internal Mach-O directly causes immediate exit.
            bundle_path = self._find_macos_app_bundle(emulator_path)
            if platform.system() == "Darwin" and bundle_path:
                open_command = ["open", "-a", bundle_path, "--args"] + command[1:]
                self._log(f"Launching macOS app bundle via open: {open_command}", "Debug")
                subprocess.Popen(open_command, shell=False)
                self._log(f"🎮 Launched '{hack_title}' with emulator", "Information")
                return
            
            # Launch emulator
            # Security: Explicitly use shell=False to prevent shell injection attacks
            # Set cwd to emulator directory so relative paths (like 'cores/snes9x.dll') work correctly
            emulator_dir = os.path.dirname(emulator_path)
            
            if platform.system() == "Windows":
                # Windows: use CREATE_NO_WINDOW to hide console and shell=False for security
                subprocess.Popen(command, shell=False, cwd=emulator_dir, creationflags=subprocess.CREATE_NO_WINDOW)
            else:
                # Unix: standard Popen with shell=False for security
                subprocess.Popen(command, shell=False, cwd=emulator_dir)
            
            self._log(f"🎮 Launched '{hack_title}' with emulator", "Information")
            
        except Exception as e:
            self._log(f"❌ Failed to launch emulator: {str(e)}", "Error")
            messagebox.showerror(
                "Launch Failed",
                f"Failed to launch emulator:\n\n{str(e)}"
            )
    
    def _find_hack_data(self, hack_id_str):
        """Find hack data by ID"""
        # Convert to string for comparison to handle both string and integer IDs
        hack_id_str = str(hack_id_str)
        for hack in self.filtered_data:
            if str(hack.get("id")) == hack_id_str:
                return hack
        return None
    
    def _open_hack_in_explorer(self, hack_id):
        """Open the hack file location in the system file explorer"""
        
        hack_data = self._find_hack_data(hack_id)
        if not hack_data:
            self._log(f"❌ Could not find hack data for ID: {hack_id}", "Error")
            return
        
        file_path = hack_data.get("file_path", "")
        hack_title = hack_data.get("title", "Unknown")
        
        if not file_path:
            self._log(f"📁 No file path available for '{hack_title}' - this hack may not be downloaded yet", "Warning")
            messagebox.showinfo(
                "File Not Available", 
                f"No file location found for '{hack_title}'.\n\n"
                f"This hack may not have been downloaded yet, or the file may have been moved."
            )
            return
        
        if not os.path.exists(file_path):
            self._log(f"📁 File not found: {file_path} for '{hack_title}'", "Warning")
            messagebox.showwarning(
                "File Not Found", 
                f"The file for '{hack_title}' could not be found:\n\n"
                f"{file_path}\n\n"
                f"The file may have been moved or deleted."
            )
            return
        
        # Try to open the file in the system explorer
        success = open_file_in_explorer(file_path)
        
        if success:
            self._log(f"📁 Opened file location for '{hack_title}' in system explorer", "Information")
        else:
            # Fallback message if the explorer couldn't be opened
            self._log(f"❌ Failed to open file explorer for '{hack_title}'", "Error")
            messagebox.showerror(
                "Explorer Error", 
                f"Could not open the file explorer for '{hack_title}'.\n\n"
                f"File location: {file_path}\n\n"
                f"You can manually navigate to this location using your file manager."
            )
    
    def _show_hack_details(self, hack_data):
        """Show detailed hack information"""
        title = hack_data.get("title", "Unknown Hack")
        details = f"Hack: {title}\n\n"
        
        # Basic info - Use multi-type display
        hack_types = hack_data.get("hack_types", []) or [hack_data.get("hack_type", "Unknown")]
        type_display = format_types_display(hack_types)
        details += f"Type: {type_display}\n"
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
        """Convert seconds to readable time format (Xd Xh Xm Xs)"""
        if seconds == 0:
            return ""  # Empty if not set
        
        # Convert to days, hours, minutes, seconds
        days = seconds // 86400  # 86400 seconds in a day
        remaining = seconds % 86400
        hours = remaining // 3600
        remaining = remaining % 3600
        minutes = remaining // 60
        secs = remaining % 60
        
        # Build the display string
        parts = []
        if days > 0:
            parts.append(f"{days}d")
        if hours > 0:
            parts.append(f"{hours}h")
        if minutes > 0:
            parts.append(f"{minutes}m")
        if secs > 0 or not parts:  # Always show seconds if no other parts, or if seconds > 0
            parts.append(f"{secs}s")
        
        return " ".join(parts)
    
    def _parse_time_input(self, time_str):
        """Parse user time input and convert to seconds"""
        if not time_str or time_str.strip() == "":
            return 0
        
        time_str = time_str.strip()
        
        # Support flexible input formats
        # HH:MM:SS, MM:SS, MM, "2h 30m", "90m", "150 minutes", etc.
        # NEW: Support shortened formats like "14d 10", "14d 10h 2", "14d 10h 2m 1"
        
        import re
        
        # Pattern for "HH:MM:SS" or "MM:SS" - handle this first to avoid regex conflicts
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
        
        # Pattern for "150 minutes" or "90 mins"
        pattern_minutes = re.match(r'(\d+)\s*(?:minutes?|mins?)$', time_str.lower())
        if pattern_minutes:
            return int(pattern_minutes.group(1)) * 60
        
        # Pattern for "2h 30m 15s" or "2h 30m" or "90m" etc. - must have letter suffix
        pattern_units = re.match(r'(?:(\d+)h\s*)?(?:(\d+)m\s*)?(?:(\d+)s\s*)?$', time_str.lower())
        if pattern_units and any(pattern_units.groups()) and re.search(r'[hms]', time_str.lower()):
            hours = int(pattern_units.group(1) or 0)
            minutes = int(pattern_units.group(2) or 0) 
            seconds = int(pattern_units.group(3) or 0)
            return hours * 3600 + minutes * 60 + seconds
        
        # NEW: Pattern for flexible shortened formats with days (only if 'd' is present)
        # "14d 10" -> 14 days, 10 hours, 0 minutes, 0 seconds
        # "14d 10h 2" -> 14 days, 10 hours, 2 minutes, 0 seconds  
        # "14d 10h 2m 1" -> 14 days, 10 hours, 2 minutes, 1 second
        if 'd' in time_str.lower():
            pattern_flexible = re.match(r'(?:(\d+)d\s*)?(?:(\d+)h?\s*)?(?:(\d+)m?\s*)?(?:(\d+)s?\s*)?$', time_str.lower())
            if pattern_flexible and any(pattern_flexible.groups()):
                days = int(pattern_flexible.group(1) or 0)
                hours = int(pattern_flexible.group(2) or 0)
                minutes = int(pattern_flexible.group(3) or 0) 
                seconds = int(pattern_flexible.group(4) or 0)
                return days * 86400 + hours * 3600 + minutes * 60 + seconds
        
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
                               f"• 90 (assumes minutes)\n"
                               f"• 14d 10 (14 days, 10 hours)\n"
                               f"• 14d 10h 2 (14 days, 10 hours, 2 minutes)\n"
                               f"• 14d 10h 2m 1 (14 days, 10 hours, 2 minutes, 1 second)")
            return None
    
    def _toggle_h_scrollbar(self, scrollbar):
        """Show/hide horizontal scrollbar based on content (debounced)"""
        # Cancel pending timer if exists
        if self.scrollbar_toggle_timer:
            self.frame.after_cancel(self.scrollbar_toggle_timer)
        
        # Schedule scrollbar update with small delay
        self.scrollbar_toggle_timer = self.frame.after(100, lambda: self._do_toggle_h_scrollbar(scrollbar))
    
    def _do_toggle_h_scrollbar(self, scrollbar):
        """Actually toggle the scrollbar"""
        self.scrollbar_toggle_timer = None
        
        tree_width = self.tree.winfo_width()
        
        # Only sum widths of VISIBLE columns
        visible_cols = self.tree["displaycolumns"]
        if visible_cols:  # displaycolumns can be empty or a list
            content_width = sum(self.tree.column(col)["width"] for col in visible_cols)
        else:
            content_width = 0
        
        if content_width > tree_width:
            scrollbar.grid(row=1, column=0, sticky="ew")
        else:
            scrollbar.grid_remove()
    
    def _create_pagination_controls(self):
        """Create pagination controls"""
        pagination_frame = ttk.Frame(self.frame)
        pagination_frame.pack(fill="x", pady=(0, 10))
        
        # Left side - Page size selector
        left_frame = ttk.Frame(pagination_frame)
        left_frame.pack(side="left")
        
       
        
        ttk.Label(left_frame, text="Show:").pack(side="left", padx=(0, 5))
        
        self.page_size_var = tk.StringVar(value="50")
        page_size_combo = ttk.Combobox(left_frame, textvariable=self.page_size_var, 
                                      values=["25", "50", "100", "200"], width=8, state="readonly")
        page_size_combo.pack(side="left", padx=(0, 5))
        page_size_combo.bind("<<ComboboxSelected>>", self._on_page_size_change)
        
        ttk.Label(left_frame, text="").pack(side="left")

          # Add Columns button
        ttk.Button(left_frame, text="⚙ Columns", command=self._show_column_config).pack(side="left", padx=(0, 15))
        
        # Center - Page info
        center_frame = ttk.Frame(pagination_frame)
        center_frame.pack(side="left", expand=True)
        
        self.page_info_label = ttk.Label(center_frame, text="Page 1 of 1")
        self.page_info_label.pack()
        
        # Right side - Navigation buttons
        right_frame = ttk.Frame(pagination_frame)
        right_frame.pack(side="right")
        
        self.first_btn = ttk.Button(right_frame, text="⏮", width=3, command=self._go_to_first_page)
        self.first_btn.pack(side="left", padx=(0, 2))
        
        self.prev_btn = ttk.Button(right_frame, text="◀", width=3, command=self._go_to_prev_page)
        self.prev_btn.pack(side="left", padx=(0, 2))
        
        # Page input
        self.page_var = tk.StringVar(value="1")
        self.page_entry = ttk.Entry(right_frame, textvariable=self.page_var, width=5, justify="center")
        self.page_entry.pack(side="left", padx=(0, 2))
        self.page_entry.bind("<Return>", self._on_page_entry_change)
        self.page_entry.bind("<FocusOut>", self._on_page_entry_change)
        
        self.next_btn = ttk.Button(right_frame, text="▶", width=3, command=self._go_to_next_page)
        self.next_btn.pack(side="left", padx=(0, 2))
        
        self.last_btn = ttk.Button(right_frame, text="⏭", width=3, command=self._go_to_last_page)
        self.last_btn.pack(side="left")
    
    def _on_page_size_change(self, event=None):
        """Handle page size change"""
        try:
            new_size = int(self.page_size_var.get())
            if new_size != self.page_size:
                self.page_size = new_size
                self.current_page = 1  # Reset to first page
                self._refresh_table()
        except ValueError:
            pass
    
    def _on_page_entry_change(self, event=None):
        """Handle manual page entry"""
        try:
            new_page = int(self.page_var.get())
            if 1 <= new_page <= self.total_pages and new_page != self.current_page:
                self.current_page = new_page
                self._refresh_table()
            else:
                # Reset to current page if invalid
                self.page_var.set(str(self.current_page))
        except ValueError:
            self.page_var.set(str(self.current_page))
    
    def _go_to_first_page(self):
        """Go to first page"""
        if self.current_page != 1:
            self.current_page = 1
            self.page_var.set("1")
            self._refresh_table()
    
    def _go_to_prev_page(self):
        """Go to previous page"""
        if self.current_page > 1:
            self.current_page -= 1
            self.page_var.set(str(self.current_page))
            self._refresh_table()
    
    def _go_to_next_page(self):
        """Go to next page"""
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.page_var.set(str(self.current_page))
            self._refresh_table()
    
    def _go_to_last_page(self):
        """Go to last page"""
        if self.current_page != self.total_pages:
            self.current_page = self.total_pages
            self.page_var.set(str(self.total_pages))
            self._refresh_table()
    
    def _update_pagination_controls(self):
        """Update pagination control states"""
        # Update page info
        self.page_info_label.configure(text=f"Page {self.current_page} of {self.total_pages}")
        
        # Update button states
        first_page = self.current_page == 1
        last_page = self.current_page == self.total_pages
        
        self.first_btn.configure(state="disabled" if first_page else "normal")
        self.prev_btn.configure(state="disabled" if first_page else "normal")
        self.next_btn.configure(state="disabled" if last_page else "normal")
        self.last_btn.configure(state="disabled" if last_page else "normal")
    
    def _sort_by_column(self, column):
        """Sort the data by the specified column"""
        # Toggle sort direction if clicking the same column
        if self.sort_column == column:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_column = column
            self.sort_reverse = False
        
        # Update header to show sort direction
        self._update_column_headers()
        
        # Apply sort and refresh table
        self._refresh_table()
    
    def _update_column_headers(self):
        """Update column headers to show sort indicators"""
        headers = ["✓", "Title", "Type(s)", "Difficulty", "Rating", "Completed Date", "Time to Beat", "Released", "Notes"]
        columns = ("completed", "title", "type", "difficulty", "rating", "completed_date", "time_to_beat", "release_date", "notes")
        
        for i, (col, base_header) in enumerate(zip(columns, headers)):
            if col == self.sort_column:
                # Add sort indicator
                indicator = " ▼" if self.sort_reverse else " ▲"
                header_text = base_header + indicator
            else:
                header_text = base_header
            
            self.tree.heading(col, text=header_text, command=lambda c=col: self._sort_by_column(c))
    
    def _sort_filtered_data(self):
        """Sort the filtered data based on current sort settings"""
        if not self.sort_column or not self.filtered_data:
            return
        
        def get_sort_key(hack):
            value = hack.get(self.sort_column, "")
            
            # Handle different data types for proper sorting
            if self.sort_column == "completed":
                # Sort completed status: completed items first, then uncompleted
                return (not hack.get("completed", False), hack.get("title", "").lower())
            elif self.sort_column in ["rating"]:
                # Numeric sorting for rating - use actual numeric value from data, not display value
                rating = hack.get("personal_rating", 0)
                try:
                    return float(rating) if rating else 0
                except (ValueError, TypeError):
                    return 0
            elif self.sort_column == "completed_date":
                # Date sorting - handle empty dates
                if not value:
                    return "0000-00-00"  # Empty dates sort first
                return value
            elif self.sort_column == "time_to_beat":
                # Time sorting - convert to numeric for proper ordering
                if not value:
                    return 0
                try:
                    # If it's already numeric (seconds), use it
                    if isinstance(value, (int, float)):
                        return value
                    # If it's a string, try to parse it
                    return float(value)
                except (ValueError, TypeError):
                    return 0
            elif self.sort_column == "release_date":
                # Release date sorting - use numeric timestamp for proper chronological ordering
                timestamp = hack.get("time", 0)
                try:
                    return int(timestamp) if timestamp else 0
                except (ValueError, TypeError):
                    return 0
            else:
                # String sorting (case-insensitive)
                return str(value).lower()
        
        self.filtered_data.sort(key=get_sort_key, reverse=self.sort_reverse)
