import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import os
import subprocess
import platform
from datetime import datetime
import sv_ttk

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
        if self.edit_widget:
            self._cancel_edit()
    
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
        # REMOVED: Font configuration (now handled in main.py apply_font_settings)
    
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
        
        # Set column widths - ADJUSTED: Slightly wider to accommodate larger font
        self.tree.column("completed", width=45, minwidth=35, anchor="center")  # INCREASED: +5px
        self.tree.column("title", width=220, minwidth=170)  # INCREASED: +20px
        self.tree.column("type", width=90, minwidth=70, anchor="center")  # INCREASED: +10px
        self.tree.column("difficulty", width=100, minwidth=80, anchor="center")  # INCREASED: +10px
        self.tree.column("rating", width=90, minwidth=70, anchor="center")  # INCREASED: +10px
        self.tree.column("completed_date", width=110, minwidth=90, anchor="center")  # INCREASED: +10px
        self.tree.column("notes", width=170, minwidth=120)  # INCREASED: +20px
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack table and scrollbars
        self.tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)
        
        # Bind events
        self.tree.bind("<Button-1>", self._on_item_click)
        self.tree.bind("<Double-1>", self._on_item_double_click)
        
        # Status label
        self.status_label = ttk.Label(self.frame, text="", font=("Segoe UI", 9))
        self.status_label.pack(pady=(5, 0))
    
    def _refresh_table(self):
        """Refresh table data from data manager"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Get all hacks and apply filters
        all_hacks = self.data_manager.get_all_hacks()
        self.filtered_data = self._filter_hacks(all_hacks)
        
        # Populate table
        for hack in self.filtered_data:
            completed_display = "✓" if hack["completed"] else ""
            rating_display = self._get_rating_display(hack["personal_rating"])
            
            # Truncate notes for display
            notes_display = hack["notes"][:30] + "..." if len(hack["notes"]) > 30 else hack["notes"]
            
            self.tree.insert("", "end", values=(
                completed_display,
                hack["title"],
                hack.get("hack_type", "Unknown").title(),
                hack["difficulty"],
                rating_display,
                hack["completed_date"],
                notes_display
            ), tags=(hack["id"],))
        
        # Update status
        total_count = len(all_hacks)
        filtered_count = len(self.filtered_data)
        completed_count = sum(1 for hack in self.filtered_data if hack["completed"])
        
        status_text = f"Showing {filtered_count} of {total_count} hacks"
        if filtered_count > 0:
            status_text += f" • {completed_count} completed"
        
        self.status_label.config(text=status_text)
    
    def _filter_hacks(self, hacks):
        """Apply current filters to hack list"""
        filtered = hacks.copy()
        
        # Name filter
        name_text = self.name_filter.get().lower()
        if name_text:
            filtered = [h for h in filtered if name_text in h["title"].lower()]
        
        # Type filter
        if self.type_filter.get() != "All":
            filtered = [h for h in filtered if h.get("hack_type", "Unknown").title() == self.type_filter.get()]
        
        # Difficulty filter
        if self.difficulty_filter.get() != "All":
            filtered = [h for h in filtered if h["difficulty"] == self.difficulty_filter.get()]
        
        # Completed filter
        completed_val = self.completed_filter.get()
        if completed_val == "Yes":
            filtered = [h for h in filtered if h["completed"]]
        elif completed_val == "No":
            filtered = [h for h in filtered if not h["completed"]]
        
        # Rating filter
        rating_val = self.rating_filter.get()
        if rating_val != "All":
            rating_num = rating_val.count("★")
            filtered = [h for h in filtered if h["personal_rating"] == rating_num]
        
        # ADDED: New attribute filters
        # Hall of Fame filter
        hof_val = self.hall_of_fame_filter.get()
        if hof_val == "Yes":
            filtered = [h for h in filtered if h.get("hall_of_fame", False)]
        elif hof_val == "No":
            filtered = [h for h in filtered if not h.get("hall_of_fame", False)]
        
        # SA-1 filter
        sa1_val = self.sa1_filter.get()
        if sa1_val == "Yes":
            filtered = [h for h in filtered if h.get("sa1_compatibility", False)]
        elif sa1_val == "No":
            filtered = [h for h in filtered if not h.get("sa1_compatibility", False)]
        
        # Collaboration filter
        collab_val = self.collaboration_filter.get()
        if collab_val == "Yes":
            filtered = [h for h in filtered if h.get("collaboration", False)]
        elif collab_val == "No":
            filtered = [h for h in filtered if not h.get("collaboration", False)]
        
        # Demo filter
        demo_val = self.demo_filter.get()
        if demo_val == "Yes":
            filtered = [h for h in filtered if h.get("demo", False)]
        elif demo_val == "No":
            filtered = [h for h in filtered if not h.get("demo", False)]
        
        return filtered
    
    def _apply_filters(self):
        """Apply current filters and refresh table"""
        self._refresh_table()
    
    def _clear_filters(self):
        """Clear all filters"""
        self.name_filter.set("")
        self.type_filter.set("All")
        self.difficulty_filter.set("All")
        self.completed_filter.set("All")
        self.rating_filter.set("All")  # CHANGED: Back to "All" for dropdown
        # Clear new filters
        self.hall_of_fame_filter.set("All")
        self.sa1_filter.set("All")
        self.collaboration_filter.set("All")
        self.demo_filter.set("All")
        self._apply_filters()
    
    def _get_rating_display(self, rating):
        """Convert numeric rating to star display"""
        if rating == 0:
            return "☆☆☆☆☆"
        return "★" * rating + "☆" * (5 - rating)
    
    def _on_item_click(self, event):
        """Handle single clicks on table items"""
        item = self.tree.identify("item", event.x, event.y)
        column = self.tree.identify("column", event.x, event.y)
        
        if not item:
            return
        
        hack_id = self.tree.item(item)["tags"][0]
        hack_data = next((h for h in self.filtered_data if h["id"] == hack_id), None)
        
        if not hack_data:
            return
        
        # Handle completed checkbox toggle
        if column == "#1":  # Completed column
            self._toggle_completed(hack_id, hack_data)
        
        # Handle rating click with simple input
        elif column == "#5":  # Rating column (moved due to new columns)
            self._edit_rating_simple(hack_id, hack_data)
        
        # Handle date click with date picker
        elif column == "#6":  # Completed date column (moved due to new columns)
            self._edit_date_with_picker(hack_id, hack_data, event)
    
    def _on_item_double_click(self, event):
        """Handle double clicks for notes editing"""
        item = self.tree.identify("item", event.x, event.y)
        column = self.tree.identify("column", event.x, event.y)
        
        if not item:
            return
        
        hack_id = self.tree.item(item)["tags"][0]
        hack_data = next((h for h in self.filtered_data if h["id"] == hack_id), None)
        
        if not hack_data:
            return
        
        # Handle notes editing on double-click
        if column == "#7":  # Notes column (moved due to new columns)
            self._edit_notes_inline(item, hack_id, hack_data, event)
    
    def _toggle_completed(self, hack_id, hack_data):
        """Toggle completed status"""
        new_completed = not hack_data["completed"]
        if self.data_manager.update_hack(hack_id, "completed", new_completed):
            hack_data["completed"] = new_completed
            # Auto-set completion date if not set
            if new_completed and not hack_data["completed_date"]:
                today = datetime.now().strftime("%Y-%m-%d")
                hack_data["completed_date"] = today
                self.data_manager.update_hack(hack_id, "completed_date", today)
            self._refresh_table()
    
    def _edit_rating_simple(self, hack_id, hack_data):
        """Simple rating edit with buttons"""
        current_rating = hack_data["personal_rating"]
        
        # Create a simple popup with star buttons
        popup = tk.Toplevel(self.frame)
        popup.title("Rate Hack")
        popup.geometry("300x150")
        popup.resizable(False, False)
        popup.grab_set()
        
        # Center the popup
        popup.update_idletasks()
        x = (popup.winfo_screenwidth() // 2) - (300 // 2)
        y = (popup.winfo_screenheight() // 2) - (150 // 2)
        popup.geometry(f"300x150+{x}+{y}")
        
        ttk.Label(popup, text=f"Rate: {hack_data['title'][:30]}...", 
                 font=("Segoe UI", 10, "bold")).pack(pady=10)
        
        button_frame = ttk.Frame(popup)
        button_frame.pack(pady=10)
        
        def set_rating(rating):
            if self.data_manager.update_hack(hack_id, "personal_rating", rating):
                hack_data["personal_rating"] = rating
                self._refresh_table()
            popup.destroy()
        
        # Create rating buttons
        for i in range(6):  # 0-5 stars
            if i == 0:
                text = "No Rating"
            else:
                text = "★" * i + "☆" * (5-i)
            
            style = "Accent.TButton" if i == current_rating else "TButton"
            btn = ttk.Button(button_frame, text=text, style=style,
                           command=lambda r=i: set_rating(r))
            btn.pack(pady=2, fill="x")
        
        # Cancel button
        ttk.Button(popup, text="Cancel", command=popup.destroy).pack(pady=5)
    
    def _edit_date_with_picker(self, hack_id, hack_data, event):
        """Edit date with a date picker popup"""
        current_date = hack_data["completed_date"]
        
        # Create popup for date picker
        popup = tk.Toplevel(self.frame)
        popup.title("Select Completed Date")
        popup.geometry("250x200")
        popup.resizable(False, False)
        popup.grab_set()
        
        # Center the popup
        popup.update_idletasks()
        x = event.x_root - 125
        y = event.y_root - 100
        popup.geometry(f"250x200+{x}+{y}")
        
        ttk.Label(popup, text=f"Completed date for:\n{hack_data['title'][:30]}...", 
                 font=("Segoe UI", 9)).pack(pady=10)
        
        # Date picker (using tkcalendar if available, otherwise simple entry)
        try:
            from tkcalendar import DateEntry
            if current_date:
                try:
                    initial_date = datetime.strptime(current_date, "%Y-%m-%d").date()
                except:
                    initial_date = datetime.now().date()
            else:
                initial_date = datetime.now().date()
            
            date_picker = DateEntry(popup, date_pattern='yyyy-mm-dd', 
                                  selectmode='day', year=initial_date.year,
                                  month=initial_date.month, day=initial_date.day)
            date_picker.pack(pady=10)
            
            def save_date():
                selected_date = date_picker.get()
                if self.data_manager.update_hack(hack_id, "completed_date", selected_date):
                    hack_data["completed_date"] = selected_date
                    self._refresh_table()
                popup.destroy()
            
        except ImportError:
            # Fallback to simple entry if tkcalendar not available
            ttk.Label(popup, text="Format: YYYY-MM-DD").pack()
            date_var = tk.StringVar(value=current_date or datetime.now().strftime("%Y-%m-%d"))
            date_entry = ttk.Entry(popup, textvariable=date_var, width=15)
            date_entry.pack(pady=10)
            
            def save_date():
                new_date = date_var.get().strip()
                if new_date:
                    try:
                        datetime.strptime(new_date, "%Y-%m-%d")
                    except ValueError:
                        messagebox.showerror("Invalid Date", "Please use YYYY-MM-DD format")
                        return
                
                if self.data_manager.update_hack(hack_id, "completed_date", new_date):
                    hack_data["completed_date"] = new_date
                    self._refresh_table()
                popup.destroy()
        
        # Buttons
        button_frame = ttk.Frame(popup)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="Save", command=save_date).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Clear", 
                  command=lambda: self._clear_date(hack_id, hack_data, popup)).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Cancel", command=popup.destroy).pack(side="left", padx=5)
    
    def _clear_date(self, hack_id, hack_data, popup):
        """Clear the completed date"""
        if self.data_manager.update_hack(hack_id, "completed_date", ""):
            hack_data["completed_date"] = ""
            self._refresh_table()
        popup.destroy()
    
    def _edit_notes_inline(self, item, hack_id, hack_data, event):
        """Edit notes with inline text widget"""
        if self.edit_widget:
            self._save_current_edit()
        
        # Get the bounding box of the notes cell
        bbox = self.tree.bbox(item, "#7")  # FIXED: Notes is column #7, not #11
        if not bbox:
            return
        
        self.edit_item = item
        self.edit_column = "#7"  # FIXED: Update to correct column
        
        # Create text widget over the cell
        current_notes = hack_data["notes"]
        
        self.edit_widget = tk.Text(self.tree, height=1, width=30, wrap="none")
        self.edit_widget.insert("1.0", current_notes)
        self.edit_widget.place(x=bbox[0], y=bbox[1], width=bbox[2], height=bbox[3])
        self.edit_widget.focus_set()
        self.edit_widget.select_range("1.0", "end")
        
        # Bind save/cancel events
        self.edit_widget.bind("<Return>", lambda e: self._save_notes_edit(hack_id, hack_data))
        self.edit_widget.bind("<Escape>", lambda e: self._cancel_edit())
        self.edit_widget.bind("<FocusOut>", lambda e: self._save_notes_edit(hack_id, hack_data))
    
    def _save_notes_edit(self, hack_id, hack_data):
        """Save the notes edit"""
        if not self.edit_widget:
            return
        
        new_notes = self.edit_widget.get("1.0", "end-1c")
        
        # Limit to 200 characters
        if len(new_notes) > 200:
            new_notes = new_notes[:200]
            messagebox.showwarning("Too Long", "Notes limited to 200 characters. Text was truncated.")
        
        if self.data_manager.update_hack(hack_id, "notes", new_notes):
            hack_data["notes"] = new_notes
            self._refresh_table()
        
        self._cancel_edit()
    
    def _save_current_edit(self):
        """Save any current edit in progress"""
        if self.edit_widget and self.edit_item:
            # This would need hack_id and hack_data, so we'll just cancel for now
            self._cancel_edit()
    
    def _cancel_edit(self):
        """Cancel current edit"""
        if self.edit_widget:
            self.edit_widget.destroy()
            self.edit_widget = None
        self.edit_item = None
        self.edit_column = None
    
    def _refresh_filter_dropdowns(self):
        """Refresh the values in filter dropdowns to include new data"""
        # Get fresh data for dropdowns
        types = ["All"] + self.data_manager.get_unique_types()
        difficulties = ["All"] + self.data_manager.get_unique_difficulties()
        
        # Update Type dropdown if it exists
        if hasattr(self, 'type_combo') and self.type_combo:
            current_type = self.type_filter.get()
            self.type_combo['values'] = types
            # Preserve current selection if it's still valid, otherwise reset to "All"
            if current_type not in types:
                self.type_filter.set("All")
        
        # Update Difficulty dropdown if it exists
        if hasattr(self, 'diff_combo') and self.diff_combo:
            current_diff = self.difficulty_filter.get()
            self.diff_combo['values'] = difficulties
            # Preserve current selection if it's still valid, otherwise reset to "All"
            if current_diff not in difficulties:
                self.difficulty_filter.set("All")