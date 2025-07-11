import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import os
import subprocess
import platform
from datetime import datetime
import sv_ttk
import calendar
from tkinter import Toplevel

# Fix the import path
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from hack_data_manager import HackDataManager

class HackHistoryPage:
    """Simple hack history page with inline editing"""
    
    def __init__(self, parent):
        self.parent = parent
        self.frame = None
        self.data_manager = HackDataManager()
        
        # ADDED: Initialize combobox references
        self.type_combo = None
        self.diff_combo = None
        
        # Initialize filter variables
        self.name_filter = tk.StringVar()
        self.type_filter = tk.StringVar(value="All")
        self.difficulty_filter = tk.StringVar(value="All")
        self.completed_filter = tk.StringVar(value="All")
        self.rating_filter = tk.StringVar(value="All")
        self.hall_of_fame_filter = tk.StringVar(value="All")
        self.sa1_filter = tk.StringVar(value="All")
        self.collaboration_filter = tk.StringVar(value="All")
        self.demo_filter = tk.StringVar(value="All")
        
        # Initialize other variables
        self.filtered_data = []
        self.tree = None
        self.edit_widget = None
        self.original_value = None
        self.edit_item = None
        self.edit_column = None
        
    def create(self):
        """Create the hack history page"""
        self.frame = ttk.Frame(self.parent, padding=10)
        
        # REMOVED: Title label to move filters up
        
        # Create filter section
        self._create_filters()
        
        # Create table section
        self._create_table()
        
        # Load initial data
        self._refresh_data_and_table()
        
        return self.frame
    
    def show(self):
        """Called when the page becomes visible - refresh data"""
        print("HackHistoryPage.show() called")  # DEBUG
        if self.frame:
            print("Refreshing data and table...")  # DEBUG
            self._refresh_data_and_table()
    
    def hide(self):
        """Called when the page becomes hidden"""
        # Cancel any active editing
        if hasattr(self, 'date_entry') and self.date_entry:
            self._cancel_date_edit()
    
        if hasattr(self, 'notes_entry') and self.notes_entry:
            self._cancel_notes_edit()

    def _refresh_data_and_table(self):
        """Refresh data from file and update table"""
        # ADDED: Reload data from processed.json to pick up new downloads
        self.data_manager = HackDataManager()  # Reinitialize to reload data
        
        # ADDED: Refresh dropdown filter values
        self._refresh_filter_dropdowns()
        
        self._refresh_table()

    def _create_filters(self):
        """Create organized filter controls in 2x3 grid layout"""
        filter_frame = ttk.LabelFrame(self.frame, text="Filters", padding=15)
        filter_frame.pack(fill="x", pady=(0, 10))
        
        # Create main grid container
        grid_container = ttk.Frame(filter_frame)
        grid_container.pack(fill="x")
        
        # === COLUMN 1 (Left - Name and Dropdowns) ===
        col1_frame = ttk.Frame(grid_container)
        col1_frame.pack(side="left", fill="x", padx=(0, 15))
        
        # Column 1, Row 1: Name
        name_frame = ttk.Frame(col1_frame)
        name_frame.pack(fill="x", pady=(0, 8))
        ttk.Label(name_frame, text="Name:", font=("Segoe UI", 9, "bold")).pack(anchor="w")
        name_entry = ttk.Entry(name_frame, textvariable=self.name_filter, width=90)
        name_entry.pack(fill="x", pady=(2, 0))
        name_entry.bind("<KeyRelease>", lambda e: self._apply_filters())
        
        # Column 1, Row 2: Type, Difficulty, Completed, Rating (4 dropdowns in a row)
        dropdowns_frame = ttk.Frame(col1_frame)
        dropdowns_frame.pack(fill="x")
        
        # Type filter - STORE REFERENCE
        type_frame = ttk.Frame(dropdowns_frame)
        type_frame.pack(side="left", padx=(0, 12))
        ttk.Label(type_frame, text="Type:", font=("Segoe UI", 9, "bold")).pack(anchor="w")
        types = ["All"] + self.data_manager.get_unique_types()
        self.type_combo = ttk.Combobox(type_frame, textvariable=self.type_filter, 
                         values=types, state="readonly", width=14)  # STORED: as self.type_combo
        self.type_combo.pack(pady=(2, 0))
        self.type_combo.bind("<<ComboboxSelected>>", lambda e: self._apply_filters())
        
        # Difficulty filter - STORE REFERENCE
        diff_frame = ttk.Frame(dropdowns_frame)
        diff_frame.pack(side="left", padx=(0, 12))
        ttk.Label(diff_frame, text="Difficulty:", font=("Segoe UI", 9, "bold")).pack(anchor="w")
        difficulties = ["All"] + self.data_manager.get_unique_difficulties()
        self.diff_combo = ttk.Combobox(diff_frame, textvariable=self.difficulty_filter, 
                         values=difficulties, state="readonly", width=14)  # STORED: as self.diff_combo
        self.diff_combo.pack(pady=(2, 0))
        self.diff_combo.bind("<<ComboboxSelected>>", lambda e: self._apply_filters())
        
        # Completed filter - FIXED: Smaller width
        completed_frame = ttk.Frame(dropdowns_frame)
        completed_frame.pack(side="left", padx=(0, 12))  # CHANGED: No expand, less padding
        ttk.Label(completed_frame, text="Completed:", font=("Segoe UI", 9, "bold")).pack(anchor="w")
        completed_combo = ttk.Combobox(completed_frame, textvariable=self.completed_filter,
                                      values=["All", "Yes", "No"], state="readonly", width=14)  # ADDED: Fixed width
        completed_combo.pack(pady=(2, 0))
        completed_combo.bind("<<ComboboxSelected>>", lambda e: self._apply_filters())
        
        # Rating filter - FIXED: Smaller width
        rating_frame = ttk.Frame(dropdowns_frame)
        rating_frame.pack(side="left")  # CHANGED: No expand, no padding
        ttk.Label(rating_frame, text="Rating:", font=("Segoe UI", 9, "bold")).pack(anchor="w")
        rating_combo = ttk.Combobox(rating_frame, textvariable=self.rating_filter,
                                   values=["All", "★★★★★", "★★★★☆", "★★★☆☆", "★★☆☆☆", "★☆☆☆☆", "☆☆☆☆☆"],
                                   state="readonly", width=14)  # ADDED: Fixed width
        rating_combo.pack(pady=(2, 0))
        rating_combo.bind("<<ComboboxSelected>>", lambda e: self._apply_filters())
        
        # === COLUMN 2 (Center - HoF and SA-1) ===
        col2_frame = ttk.Frame(grid_container)
        col2_frame.pack(side="left", padx=(0, 15))  # CHANGED: Reduced padding
        
        # Column 2, Row 1: HoF
        hof_frame = ttk.Frame(col2_frame)
        hof_frame.pack(pady=(0, 8))
        ttk.Label(hof_frame, text="HoF:", font=("Segoe UI", 9, "bold")).pack(anchor="w")
        hof_radio_frame = ttk.Frame(hof_frame)
        hof_radio_frame.pack(pady=(2, 0))
        
        hof_options = [("Any", "All"), ("Yes", "Yes"), ("No", "No")]
        for display, value in hof_options:
            ttk.Radiobutton(hof_radio_frame, text=display, variable=self.hall_of_fame_filter,
                           value=value, command=self._apply_filters).pack(side="left", padx=(0, 5))  # CHANGED: Less padding
        
        # Column 2, Row 2: SA-1
        sa1_frame = ttk.Frame(col2_frame)
        sa1_frame.pack()
        ttk.Label(sa1_frame, text="SA-1:", font=("Segoe UI", 9, "bold")).pack(anchor="w")
        sa1_radio_frame = ttk.Frame(sa1_frame)
        sa1_radio_frame.pack(pady=(2, 0))
        
        sa1_options = [("Any", "All"), ("Yes", "Yes"), ("No", "No")]
        for display, value in sa1_options:
            ttk.Radiobutton(sa1_radio_frame, text=display, variable=self.sa1_filter,
                           value=value, command=self._apply_filters).pack(side="left", padx=(0, 5))  # CHANGED: Less padding
        
        # === COLUMN 3 (Right - Collab and Demo) ===
        col3_frame = ttk.Frame(grid_container)
        col3_frame.pack(side="right")
        
        # Column 3, Row 1: Collab
        collab_frame = ttk.Frame(col3_frame)
        collab_frame.pack(pady=(0, 8))
        ttk.Label(collab_frame, text="Collab:", font=("Segoe UI", 9, "bold")).pack(anchor="w")
        collab_radio_frame = ttk.Frame(collab_frame)
        collab_radio_frame.pack(pady=(2, 0))
        
        collab_options = [("Any", "All"), ("Yes", "Yes"), ("No", "No")]
        for display, value in collab_options:
            ttk.Radiobutton(collab_radio_frame, text=display, variable=self.collaboration_filter,
                           value=value, command=self._apply_filters).pack(side="left", padx=(0, 5))  # CHANGED: Less padding
        
        # Column 3, Row 2: Demo
        demo_frame = ttk.Frame(col3_frame)
        demo_frame.pack()
        ttk.Label(demo_frame, text="Demo:", font=("Segoe UI", 9, "bold")).pack(anchor="w")
        demo_radio_frame = ttk.Frame(demo_frame)
        demo_radio_frame.pack(pady=(2, 0))
        
        demo_options = [("Any", "All"), ("Yes", "Yes"), ("No", "No")]
        for display, value in demo_options:
            ttk.Radiobutton(demo_radio_frame, text=display, variable=self.demo_filter,
                           value=value, command=self._apply_filters).pack(side="left", padx=(0, 5))  # CHANGED: Less padding
        
        # === CLEAR BUTTON (Below the grid) - CHANGED: Right aligned with Refresh button ===
        clear_button_frame = ttk.Frame(filter_frame)
        clear_button_frame.pack(fill="x", pady=(15, 0))
        
        # Button container for right alignment
        button_container = ttk.Frame(clear_button_frame)
        button_container.pack(side="right")
        
        # Refresh List button
        ttk.Button(button_container, text="Refresh List", 
                  command=self._refresh_data_and_table).pack(side="left", padx=(0, 10))
        
        # Clear All Filters button
        ttk.Button(button_container, text="Clear All Filters", 
                  command=self._clear_filters).pack(side="left")
    
    def _create_table(self):
        """Create the main data table"""
        # Table frame with scrollbars
        table_frame = ttk.Frame(self.frame)
        table_frame.pack(fill="both", expand=True)
        
        # UPDATED: Focus on essential columns only
        columns = ("completed", "title", "type", "difficulty", "rating", "completed_date", "notes")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
        
        # Configure columns
        self.tree.heading("completed", text="✓")
        self.tree.heading("title", text="Title")
        self.tree.heading("type", text="Type")
        self.tree.heading("difficulty", text="Difficulty")
        self.tree.heading("rating", text="Rating")
        self.tree.heading("completed_date", text="Completed Date")
        self.tree.heading("notes", text="Notes")
        
        # Set column widths
        self.tree.column("completed", width=45, minwidth=35, anchor="center")
        self.tree.column("title", width=220, minwidth=170)
        self.tree.column("type", width=90, minwidth=70, anchor="center")
        self.tree.column("difficulty", width=100, minwidth=80, anchor="center")
        self.tree.column("rating", width=90, minwidth=70, anchor="center")
        self.tree.column("completed_date", width=110, minwidth=90, anchor="center")
        self.tree.column("notes", width=170, minwidth=120)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack table and scrollbars (set horizontal scrollbar to auto-display)
        self.tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid_remove()  # Initially hide the horizontal scrollbar
        
        # Make a binding to show/hide scrollbar when needed
        self.tree.bind("<Configure>", lambda e: self._toggle_h_scrollbar(h_scrollbar))
        
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)
        
        # Bind events
        self.tree.bind("<Button-1>", self._on_item_click)
        self.tree.bind("<Double-1>", self._on_item_double_click)
        self.tree.bind("<Motion>", self._on_mouse_motion)  # ADDED: Mouse motion for cursor changes
        
        # Status label
        self.status_label = ttk.Label(self.frame, text="", font=("Segoe UI", 9))
        self.status_label.pack(pady=(5, 0))

    def _on_mouse_motion(self, event):
        """Change cursor when hovering over clickable columns"""
        item = self.tree.identify("item", event.x, event.y)
        column = self.tree.identify("column", event.x, event.y)
        
        if item and column in ["#1", "#6", "#7"]:  # Completed, Date, and Notes columns are clickable
            self.tree.config(cursor="hand2")
        else:
            self.tree.config(cursor="")

    def _refresh_table(self):
        """Refresh table data from data manager"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Get all hacks and apply filters
        all_hacks = self.data_manager.get_all_hacks()
        self.filtered_data = self._filter_hacks(all_hacks)
        
        print(f"DEBUG: _refresh_table - Found {len(self.filtered_data)} hacks")  # DEBUG
        
        # Populate table
        for hack in self.filtered_data:
            # Simple checkmark display
            completed_display = "✓" if hack.get("completed", False) else ""
            rating_display = self._get_rating_display(hack.get("personal_rating", 0))
            
            # Truncate notes for display
            notes_display = hack.get("notes", "")
            if len(notes_display) > 30:
                notes_display = notes_display[:30] + "..."
            
            # FIXED: Use the correct key "id" from data manager
            hack_id = hack.get("id")  # Data manager uses "id" key
            print(f"DEBUG: _refresh_table - Hack ID: '{hack_id}' (type: {type(hack_id)}) for '{hack['title']}'")  # DEBUG
            
            self.tree.insert("", "end", values=(
                completed_display,
                hack["title"],
                hack.get("hack_type", "Unknown").title(),
                hack.get("difficulty", "Unknown"),
                rating_display,
                hack.get("completed_date", ""),
                notes_display
            ), tags=(hack_id,))  # Use the actual hack ID as tag
        
        # Update status
        total_count = len(self.data_manager.get_all_hacks())
        filtered_count = len(self.filtered_data)
        completed_count = sum(1 for hack in self.filtered_data if hack.get("completed", False))
        
        status_text = f"Showing {filtered_count} of {total_count} hacks"
        if filtered_count > 0:
            status_text += f" • {completed_count} completed"
        
        if hasattr(self, 'status_label'):
            self.status_label.config(text=status_text)

    def _toggle_completed(self, hack_id):
        """Toggle completed status for a hack"""
        print(f"DEBUG: Looking for hack ID: {hack_id} (type: {type(hack_id)})")
        
        # FIXED: Convert hack_id to string to match data structure
        hack_id_str = str(hack_id)
        
        # Find the hack in our filtered data
        hack_data = None
        for hack in self.filtered_data:
            current_id = hack.get("id")
            print(f"DEBUG: Comparing '{hack_id_str}' with '{current_id}' (types: {type(hack_id_str)} vs {type(current_id)})")
            
            if current_id == hack_id_str:  # Compare as strings
                hack_data = hack
                print(f"DEBUG: Found match for hack: {hack['title']}")
                break

        if not hack_data:
            print(f"ERROR: Could not find hack with ID: {hack_id}")
            print(f"DEBUG: Available hack IDs: {[hack.get('id') for hack in self.filtered_data[:5]]}")
            return
        
        # Toggle the completed status
        new_completed = not hack_data.get("completed", False)
        print(f"DEBUG: Toggling completed from {hack_data.get('completed', False)} to {new_completed}")
        
        # FIXED: Use string hack_id for data manager
        if self.data_manager.update_hack(hack_id_str, "completed", new_completed):
            # Update local data
            hack_data["completed"] = new_completed
            
            if new_completed:
                # COMPLETED: Auto-set completion date if completed and no date set
                if not hack_data.get("completed_date"):
                    from datetime import datetime
                    today = datetime.now().strftime("%Y-%m-%d")
                    hack_data["completed_date"] = today
                    self.data_manager.update_hack(hack_id_str, "completed_date", today)
                    print(f"DEBUG: Auto-set completion date to {today}")
            else:
                # NOT COMPLETED: Clear the completion date for consistency
                hack_data["completed_date"] = ""
                self.data_manager.update_hack(hack_id_str, "completed_date", "")
                print(f"DEBUG: Cleared completion date")
            
            # Refresh the table to show changes
            self._refresh_table()
            
            print(f"SUCCESS: Hack '{hack_data['title']}' marked as {'completed' if new_completed else 'not completed'}")
        else:
            print(f"ERROR: Failed to update completion status for hack {hack_id_str}")

    def _refresh_filter_dropdowns(self):
        """Refresh the values in filter dropdowns to include new data"""
        # Get fresh data for dropdowns
        types = ["All"] + self.data_manager.get_unique_types()
        difficulties = ["All"] + self.data_manager.get_unique_difficulties()
        
        # Update Type dropdown if it exists
        if hasattr(self, 'type_combo') and self.type_combo:
            current_type = self.type_filter.get()
            self.type_combo['values'] = types
            if current_type not in types:
                self.type_filter.set("All")
        
        # Update Difficulty dropdown if it exists
        if hasattr(self, 'diff_combo') and self.diff_combo:
            current_diff = self.difficulty_filter.get()
            self.diff_combo['values'] = difficulties
            if current_diff not in difficulties:
                self.difficulty_filter.set("All")

    def _on_item_click(self, event):
        """Handle single clicks on table items"""
        # First check if we need to save any active edit
        needs_refresh = False
        if hasattr(self, 'date_entry') and self.date_entry:
            # Save the current edit before starting a new one
            self._save_date_edit()
            needs_refresh = True  # We'll need to refresh after saving
    
        # Also check for active notes edit
        if hasattr(self, 'notes_entry') and self.notes_entry:
            # Save the current edit before starting a new one
            self._save_notes_edit()
            needs_refresh = True  # We'll need to refresh after saving

        # Now identify what was clicked
        item = self.tree.identify("item", event.x, event.y)
        column = self.tree.identify("column", event.x, event.y)
        
        if not item or not column:
            return
        
        # If we saved an edit, refresh the table first to ensure we have fresh data
        if needs_refresh:
            self._refresh_table()
            # Re-identify the clicked item after refresh (it might have changed position)
            item = self.tree.identify("item", event.x, event.y)
            if not item:
                return
        
        # Handle completed checkbox toggle
        if column == "#1":  # First column is completed
            tags = self.tree.item(item)["tags"]
            if tags:
                hack_id = tags[0]
                self._toggle_completed(hack_id)

        # Handle completed date click
        elif column == "#6":  # Completed date column
            tags = self.tree.item(item)["tags"]
            if tags:
                hack_id = tags[0]
                self._edit_date_cell(hack_id, item, event)
    
        # Handle notes click
        elif column == "#7":  # Notes column
            tags = self.tree.item(item)["tags"]
            if tags:
                hack_id = tags[0]
                self._edit_notes_cell(hack_id, item, event)

    def _edit_date_cell(self, hack_id, item, event):
        """Allow direct editing of date cell"""
        # Clean up any existing date entry
        if hasattr(self, 'date_entry') and self.date_entry:
            self._cleanup_date_edit()

        hack_id_str = str(hack_id)

        # Find the hack data
        hack_data = None
        for hack in self.filtered_data:
            if hack.get("id") == hack_id_str:
                hack_data = hack
                break

        if not hack_data:
            return

        # Get the bounding box of the date cell
        bbox = self.tree.bbox(item, "#6")
        if not bbox:
            return

        # Get current date value
        current_date = hack_data.get("completed_date", "")

        # Create inline entry widget
        x, y, width, height = bbox

        # Store references for saving/canceling
        self.editing_hack_id = hack_id_str
        self.editing_item = item
        self.original_date = current_date

        # Create entry widget positioned exactly over the cell
        self.date_entry = ttk.Entry(self.tree, font=("Segoe UI", 10))
        self.date_entry.place(x=x, y=y, width=width, height=height)
        self.date_entry.insert(0, current_date)
        
        # Register a window-level binding that saves when clicking elsewhere
        self.binding_id = self.tree.winfo_toplevel().bind("<Button-1>", self._check_date_click, add="+")

        # Bind events to the entry widget
        self.date_entry.bind("<Return>", lambda e: self._save_date_edit())
        self.date_entry.bind("<Escape>", lambda e: self._cancel_date_edit())
        
        # FIXED: Use after method with stronger focus management
        # This helps ensure the widget truly gets focus
        self.tree.after(50, lambda: self._ensure_entry_focus())

    def _ensure_entry_focus(self):
        """Ensure the entry widget has proper focus and selection"""
        if hasattr(self, 'date_entry') and self.date_entry:
            try:
                # Grab all focus to this widget
                self.date_entry.focus_force()
                
                # Ensure the application window has focus
                self.tree.winfo_toplevel().focus_force()
                
                # Then set focus back to our entry and select all text
                self.date_entry.focus_force()
                self.date_entry.select_range(0, tk.END)
                
                # Set insertion cursor at end just in case
                self.date_entry.icursor(tk.END)
                
                # Process all pending events to ensure focus is applied
                self.tree.update_idletasks()
            except tk.TclError:
                # Widget may have been destroyed
                pass

    def _check_date_click(self, event):
        """Check if click is outside the date entry and save if needed"""
        if not hasattr(self, 'date_entry') or not self.date_entry:
            return

        # Get entry widget position
        try:
            x = self.date_entry.winfo_rootx()
            y = self.date_entry.winfo_rooty()
            w = self.date_entry.winfo_width()
            h = self.date_entry.winfo_height()
            
            # If click is outside the entry, save the edit
            if event.x_root < x or event.x_root > x+w or event.y_root < y or event.y_root > y+h:
                self._save_date_edit()
        except tk.TclError:
            # Widget may have been destroyed
            pass

    def _cancel_date_edit(self, event=None):
        """Cancel date editing without saving"""
        if hasattr(self, 'binding_id') and self.binding_id:
            try:
                self.tree.winfo_toplevel().unbind("<Button-1>", self.binding_id)
                self.binding_id = None
            except:
                pass
        self._cleanup_date_edit()

    def _save_date_edit(self, event=None):
        """Save the edited date after validation"""
        if not hasattr(self, 'date_entry') or not self.date_entry:
            return
        
        # Remove global binding first to prevent recursive calls
        if hasattr(self, 'binding_id') and self.binding_id:
            try:
                self.tree.winfo_toplevel().unbind("<Button-1>", self.binding_id)
                self.binding_id = None
            except:
                pass
    
        try:
            new_date = self.date_entry.get().strip()
        except tk.TclError:
            self._cleanup_date_edit()
            return
        
        # Validate and normalize the date if not empty
        normalized_date = ""
        if new_date:
            normalized_date = self._normalize_date(new_date)
            if not normalized_date:
                # Show error but clear the invalid date
                messagebox.showerror("Invalid Date", 
                         "Invalid date format detected. The date field has been cleared.\n\n"
                         "Valid format is YYYY-MM-DD (e.g., 2025-01-15)")
                new_date = ""  # Clear the invalid date
            else:
                new_date = normalized_date

        # Find the hack data
        hack_data = None
        for hack in self.filtered_data:
            if hack.get("id") == self.editing_hack_id:
                hack_data = hack
                break

        if hack_data:
            if self.data_manager.update_hack(self.editing_hack_id, "completed_date", new_date):
                hack_data["completed_date"] = new_date
                
                if new_date:
                    hack_data["completed"] = True
                    self.data_manager.update_hack(self.editing_hack_id, "completed", True)
                else:
                    hack_data["completed"] = False
                    self.data_manager.update_hack(self.editing_hack_id, "completed", False)
                
                print(f"SUCCESS: Date updated for '{hack_data['title']}' to {new_date or 'cleared'}")
            else:
                print(f"ERROR: Failed to update date for hack {self.editing_hack_id}")
        
        self._cleanup_date_edit()
        self._refresh_table()

    def _normalize_date(self, date_string):
        """Convert any valid date format to YYYY-MM-DD format"""
        if not date_string:
            return ""
        
        date_formats = [
            "%Y-%m-%d", "%Y/%m/%d", "%m/%d/%Y", "%d/%m/%Y", "%m-%d-%Y", "%d-%m-%Y",
            "%m.%d.%Y", "%d.%m.%Y", "%Y.%m.%d", "%d %m %Y", "%m %d %Y", "%Y %m %d",
            "%B %d, %Y", "%d %B %Y", "%b %d, %Y", "%d %b %Y", "%Y%m%d", "%m%d%Y", "%d%m%Y"
        ]
        
        for date_format in date_formats:
            try:
                parsed_date = datetime.strptime(date_string, date_format)
                return parsed_date.strftime("%Y-%m-%d")
            except ValueError:
                continue
        
        return None

    def _cleanup_date_edit(self):
        """Clean up date editing widgets and variables"""
        # Remove window-level binding if it exists
        if hasattr(self, 'binding_id') and self.binding_id:
            try:
                self.tree.winfo_toplevel().unbind("<Button-1>", self.binding_id)
                self.binding_id = None
            except:
                pass
            
        # Destroy the entry widget if it exists
        if hasattr(self, 'date_entry') and self.date_entry:
            try:
                self.date_entry.destroy()
            except tk.TclError:
                pass
            self.date_entry = None
        
        # Remove all related attributes
        for attr in ['editing_hack_id', 'editing_item', 'original_date', '_validating_date']:
            if hasattr(self, attr):
                delattr(self, attr)

    def _edit_notes_cell(self, hack_id, item, event):
        """Allow direct editing of notes cell"""
        # Clean up any existing notes entry
        if hasattr(self, 'notes_entry') and self.notes_entry:
            self._cleanup_notes_edit()

        hack_id_str = str(hack_id)

        # Find the hack data
        hack_data = None
        for hack in self.filtered_data:
            if hack.get("id") == hack_id_str:
                hack_data = hack
                break

        if not hack_data:
            return

        # Get the bounding box of the notes cell
        bbox = self.tree.bbox(item, "#7")
        if not bbox:
            return

        # Get current notes value
        current_notes = hack_data.get("notes", "")

        # Create inline entry widget
        x, y, width, height = bbox

        # Store references for saving/canceling
        self.editing_notes_hack_id = hack_id_str
        self.editing_notes_item = item
        self.original_notes = current_notes

        # Create entry widget positioned exactly over the cell
        self.notes_entry = ttk.Entry(self.tree, font=("Segoe UI", 10))
        self.notes_entry.place(x=x, y=y, width=width, height=height)
        self.notes_entry.insert(0, current_notes)
        
        # Register a window-level binding that saves when clicking elsewhere
        self.notes_binding_id = self.tree.winfo_toplevel().bind("<Button-1>", self._check_notes_click, add="+" )

        # Bind events to the entry widget
        self.notes_entry.bind("<Return>", lambda e: self._save_notes_edit())
        self.notes_entry.bind("<Escape>", lambda e: self._cancel_notes_edit())
        
        # Use after method with stronger focus management
        self.tree.after(50, lambda: self._ensure_notes_entry_focus())

    def _ensure_notes_entry_focus(self):
        """Ensure the notes entry widget has proper focus and selection"""
        if hasattr(self, 'notes_entry') and self.notes_entry:
            try:
                # Grab all focus to this widget
                self.notes_entry.focus_force()
                
                # Ensure the application window has focus
                self.tree.winfo_toplevel().focus_force()
                
                # Then set focus back to our entry and select all text
                self.notes_entry.focus_force()
                self.notes_entry.select_range(0, tk.END)
                
                # Set insertion cursor at end just in case
                self.notes_entry.icursor(tk.END)
                
                # Process all pending events to ensure focus is applied
                self.tree.update_idletasks()
            except tk.TclError:
                # Widget may have been destroyed
                pass

    def _check_notes_click(self, event):
        """Check if click is outside the notes entry and save if needed"""
        if not hasattr(self, 'notes_entry') or not self.notes_entry:
            return

        # Get entry widget position
        try:
            x = self.notes_entry.winfo_rootx()
            y = self.notes_entry.winfo_rooty()
            w = self.notes_entry.winfo_width()
            h = self.notes_entry.winfo_height()
            
            # If click is outside the entry, save the edit
            if event.x_root < x or event.x_root > x+w or event.y_root < y or event.y_root > y+h:
                self._save_notes_edit()
        except tk.TclError:
            # Widget may have been destroyed
            pass

    def _cancel_notes_edit(self, event=None):
        """Cancel notes editing without saving"""
        if hasattr(self, 'notes_binding_id') and self.notes_binding_id:
            try:
                self.tree.winfo_toplevel().unbind("<Button-1>", self.notes_binding_id)
                self.notes_binding_id = None
            except:
                pass
        self._cleanup_notes_edit()

    def _save_notes_edit(self, event=None):
        """Save the edited notes"""
        if not hasattr(self, 'notes_entry') or not self.notes_entry:
            return
        
        # Remove global binding first to prevent recursive calls
        if hasattr(self, 'notes_binding_id') and self.notes_binding_id:
            try:
                self.tree.winfo_toplevel().unbind("<Button-1>", self.notes_binding_id)
                self.notes_binding_id = None
            except:
                pass
        
        try:
            new_notes = self.notes_entry.get().strip()
            
            # Limit notes to 280 characters
            if len(new_notes) > 280:
                new_notes = new_notes[:280]
        except tk.TclError:
            self._cleanup_notes_edit()
            return

        # Find the hack data
        hack_data = None
        for hack in self.filtered_data:
            if hack.get("id") == self.editing_notes_hack_id:
                hack_data = hack
                break

        if hack_data:
            if self.data_manager.update_hack(self.editing_notes_hack_id, "notes", new_notes):
                hack_data["notes"] = new_notes
                print(f"SUCCESS: Notes updated for '{hack_data['title']}'")
            else:
                print(f"ERROR: Failed to update notes for hack {self.editing_notes_hack_id}")
        
        self._cleanup_notes_edit()
        self._refresh_table()

    def _cleanup_notes_edit(self):
        """Clean up notes editing widgets and variables"""
        # Remove window-level binding if it exists
        if hasattr(self, 'notes_binding_id') and self.notes_binding_id:
            try:
                self.tree.winfo_toplevel().unbind("<Button-1>", self.notes_binding_id)
                self.notes_binding_id = None
            except:
                pass
        
        # Destroy the entry widget if it exists
        if hasattr(self, 'notes_entry') and self.notes_entry:
            try:
                self.notes_entry.destroy()
            except tk.TclError:
                pass
            self.notes_entry = None
    
    def _apply_filters(self):
        """Apply all filters and refresh the table"""
        self._refresh_table()

    def _clear_filters(self):
        """Reset all filters to default values"""
        self.name_filter.set("")
        self.type_filter.set("All")
        self.difficulty_filter.set("All")
        self.completed_filter.set("All")
        self.rating_filter.set("All")
        self.hall_of_fame_filter.set("All")
        self.sa1_filter.set("All") 
        self.collaboration_filter.set("All")
        self.demo_filter.set("All")
        self._apply_filters()

    def _filter_hacks(self, hacks):
        """Apply all active filters to the list of hacks"""
        filtered_hacks = []
        
        for hack in hacks:
            # Name filter (case insensitive substring match)
            name_filter_text = self.name_filter.get().strip().lower()
            if name_filter_text and name_filter_text not in hack.get("title", "").lower():
                continue
                
            # Type filter
            type_filter_value = self.type_filter.get()
            if type_filter_value != "All" and hack.get("hack_type", "").title() != type_filter_value:
                continue
                
            # Difficulty filter
            difficulty_filter_value = self.difficulty_filter.get()
            if difficulty_filter_value != "All" and hack.get("difficulty") != difficulty_filter_value:
                continue
                
            # Completed filter
            completed_filter_value = self.completed_filter.get()
            if completed_filter_value == "Yes" and not hack.get("completed", False):
                continue
            elif completed_filter_value == "No" and hack.get("completed", False):
                continue
                
            # Rating filter
            rating_filter_value = self.rating_filter.get()
            if rating_filter_value != "All":
                # Convert star display to numeric rating
                stars_count = rating_filter_value.count("★")
                if hack.get("personal_rating", 0) != stars_count:
                    continue
                
            # Hall of Fame filter
            hof_filter_value = self.hall_of_fame_filter.get()
            if hof_filter_value == "Yes" and not hack.get("hall_of_fame", False):
                continue
            elif hof_filter_value == "No" and hack.get("hall_of_fame", False):
                continue
                
            # SA-1 filter - FIXED: Use correct field name "sa1_compatibility"
            sa1_filter_value = self.sa1_filter.get()
            if sa1_filter_value == "Yes" and not hack.get("sa1_compatibility", False):
                continue
            elif sa1_filter_value == "No" and hack.get("sa1_compatibility", False):
                continue
                
            # Collaboration filter - FIXED: Use correct field name
            collab_filter_value = self.collaboration_filter.get()
            if collab_filter_value == "Yes" and not hack.get("collaboration", False):
                continue
            elif collab_filter_value == "No" and hack.get("collaboration", False):
                continue
                
            # Demo filter
            demo_filter_value = self.demo_filter.get()
            if demo_filter_value == "Yes" and not hack.get("demo", False):
                continue
            elif demo_filter_value == "No" and hack.get("demo", False):
                continue
                
            # Hack passed all filters, add to results
            filtered_hacks.append(hack)
            
        return filtered_hacks

    def _get_rating_display(self, rating):
        """Convert numeric rating (0-5) to star display"""
        if rating == 0:
            return "☆☆☆☆☆"  # Unrated
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
            return "☆☆☆☆☆"  # Invalid rating

    def _on_item_double_click(self, event):
        """Handle double click on a table item - open hack details"""
        item = self.tree.identify("item", event.x, event.y)
        if not item:
            return
            
        # Get hack ID from item tags
        tags = self.tree.item(item)["tags"]
        if not tags:
            return
            
        hack_id = tags[0]
        
        # Find the hack data
        hack_data = None
        for hack in self.filtered_data:
            if str(hack.get("id")) == str(hack_id):
                hack_data = hack
                break
                
        if hack_data:
            self._show_hack_details(hack_data)

    def _show_hack_details(self, hack_data):
        """Show detailed information for a hack"""
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
        if hack_data.get('sa1', False):
            details += "Uses SA-1 chip: Yes\n"
        if hack_data.get('collab', False):
            details += "Collaboration project: Yes\n"
        if hack_data.get('demo', False):
            details += "Demo version: Yes\n"
        
        # Notes
        if hack_data.get('notes'):
            details += f"\nNotes:\n{hack_data.get('notes')}"
        
        # Display in a dialog
        messagebox.showinfo(title, details)

    def _toggle_h_scrollbar(self, scrollbar):
        """Show or hide horizontal scrollbar based on content width"""
        tree_width = self.tree.winfo_width()
        content_width = sum(self.tree.column(col)["width"] for col in self.tree["columns"])
        
        if content_width > tree_width:
            scrollbar.grid(row=1, column=0, sticky="ew")
        else:
            scrollbar.grid_remove()

