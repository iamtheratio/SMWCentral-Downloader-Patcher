import tkinter as tk
from tkinter import ttk, messagebox
import threading
from datetime import datetime, timedelta
import sys
import os

# Add path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from utils import TYPE_DISPLAY_LOOKUP, DIFFICULTY_LOOKUP, format_types_display
from ui_constants import get_labelframe_padding
from ui.components import DifficultySection
import sv_ttk

class DownloadFilters:
    """Filter section for download page"""
    
    def __init__(self, parent, callback_search, callback_clear, callback_time_period_update, callback_cancel=None):
        self.parent = parent
        self.callback_search = callback_search
        self.callback_clear = callback_clear
        self.callback_time_period_update = callback_time_period_update
        self.callback_cancel = callback_cancel
        
        # Filter variables
        self.name_var = tk.StringVar()
        self.type_var = tk.StringVar()
        self.authors_var = tk.StringVar()
        self.tags_var = tk.StringVar()
        self.description_var = tk.StringVar()
        self.time_period_var = tk.StringVar(value="All Time")
        self.hof_var = tk.StringVar(value="Any")
        self.sa1_var = tk.StringVar(value="Any")
        self.collab_var = tk.StringVar(value="Any")
        self.demo_var = tk.StringVar(value="Any")
        self.include_waiting_var = tk.BooleanVar(value=False)
        
        # UI components and state
        self.search_button = None
        self.time_combo = None
        self.is_searching = False
        
        # Create the filters
        self._create_filters()
        
    def _create_filters(self):
        """Create the organized filters section"""
        filter_frame = ttk.LabelFrame(self.parent, text="Filters", padding=get_labelframe_padding())
        filter_frame.pack(fill="x", pady=(0, 10))
        
        # First row: Name, Collab, Hall of Fame
        self._create_row1(filter_frame)
        
        # Second row: Type, Tags, Authors, Time Period, Demo, SA-1
        self._create_row2(filter_frame)
        
        # Third row: Description, Include Waiting, Search buttons
        self._create_row3(filter_frame)
        
        # Time period can now work independently with API-based date sorting
        # No need for complex state tracking
        
    def _create_row1(self, parent):
        """Create first row: Name, Collab, Hall of Fame"""
        row1_frame = ttk.Frame(parent)
        row1_frame.pack(fill="x", pady=(0, 10))
        
        # Name field (takes more space)
        name_frame = ttk.Frame(row1_frame)
        name_frame.pack(side="left", fill="x", expand=True)
        ttk.Label(name_frame, text="Name:").pack(anchor="w")
        ttk.Entry(name_frame, textvariable=self.name_var, width=40).pack(fill="x", pady=(2, 0))
        
        # Collab radio buttons
        collab_frame = ttk.Frame(row1_frame)
        collab_frame.pack(side="right", padx=(20, 10))
        ttk.Label(collab_frame, text="Collab:", font=("Segoe UI", 9, "bold")).pack(anchor="w")
        collab_radio_frame = ttk.Frame(collab_frame)
        collab_radio_frame.pack(anchor="w")
        for option in ["Any", "Yes", "No"]:
            ttk.Radiobutton(collab_radio_frame, text=option, variable=self.collab_var, value=option).pack(side="left", padx=(0, 5))
        
        # Hall of Fame radio buttons
        hof_frame = ttk.Frame(row1_frame)
        hof_frame.pack(side="right", padx=(10, 0))
        ttk.Label(hof_frame, text="Hall of Fame:", font=("Segoe UI", 9, "bold")).pack(anchor="w")
        hof_radio_frame = ttk.Frame(hof_frame)
        hof_radio_frame.pack(anchor="w")
        for option in ["Any", "Yes", "No"]:
            ttk.Radiobutton(hof_radio_frame, text=option, variable=self.hof_var, value=option).pack(side="left", padx=(0, 5))
    
    def _create_row2(self, parent):
        """Create second row: Type, Tags, Authors, Time Period, Demo, SA-1"""
        row2_frame = ttk.Frame(parent)
        row2_frame.pack(fill="x", pady=(0, 10))
        
        # Type dropdown
        type_frame = ttk.Frame(row2_frame)
        type_frame.pack(side="left")
        ttk.Label(type_frame, text="Type:").pack(anchor="w")
        type_combo = ttk.Combobox(
            type_frame, 
            textvariable=self.type_var,
            values=["Any"] + sorted(TYPE_DISPLAY_LOOKUP.values()),
            state="readonly",
            width=12
        )
        type_combo.pack(pady=(2, 0))
        type_combo.set("Any")
        
        # Tags field
        tags_frame = ttk.Frame(row2_frame)
        tags_frame.pack(side="left", padx=(15, 0))
        ttk.Label(tags_frame, text="Tag(s):").pack(anchor="w")
        ttk.Entry(tags_frame, textvariable=self.tags_var, width=15).pack(pady=(2, 0))
        
        # Authors field
        authors_frame = ttk.Frame(row2_frame)
        authors_frame.pack(side="left", padx=(15, 0))
        ttk.Label(authors_frame, text="Author(s):").pack(anchor="w")
        ttk.Entry(authors_frame, textvariable=self.authors_var, width=15).pack(pady=(2, 0))
        
        # Time Period dropdown
        time_frame = ttk.Frame(row2_frame)
        time_frame.pack(side="left", padx=(15, 0))
        ttk.Label(time_frame, text="Time Period:").pack(anchor="w")
        self.time_combo = ttk.Combobox(
            time_frame,
            textvariable=self.time_period_var,
            values=["All Time", "Last Week", "Last Month", "3 Months", "6 Months", "1 Year"],
            state="readonly",
            width=12
        )
        self.time_combo.pack(pady=(2, 0))
        self.time_combo.set("All Time")
        
        # Demo radio buttons
        demo_frame = ttk.Frame(row2_frame)
        demo_frame.pack(side="right", padx=(20, 10))
        ttk.Label(demo_frame, text="Demo:", font=("Segoe UI", 9, "bold")).pack(anchor="w")
        demo_radio_frame = ttk.Frame(demo_frame)
        demo_radio_frame.pack(anchor="w")
        for option in ["Any", "Yes", "No"]:
            ttk.Radiobutton(demo_radio_frame, text=option, variable=self.demo_var, value=option).pack(side="left", padx=(0, 5))
        
        # SA-1 radio buttons
        sa1_frame = ttk.Frame(row2_frame)
        sa1_frame.pack(side="right", padx=(10, 0))
        ttk.Label(sa1_frame, text="SA-1:", font=("Segoe UI", 9, "bold")).pack(anchor="w")
        sa1_radio_frame = ttk.Frame(sa1_frame)
        sa1_radio_frame.pack(anchor="w")
        for option in ["Any", "Yes", "No"]:
            ttk.Radiobutton(sa1_radio_frame, text=option, variable=self.sa1_var, value=option).pack(side="left", padx=(0, 5))
    
    def _create_row3(self, parent):
        """Create third row: Description, Include Waiting, Search buttons"""
        row3_frame = ttk.Frame(parent)
        row3_frame.pack(fill="x", pady=(0, 0))
        
        # Description field (smaller width)
        description_frame = ttk.Frame(row3_frame)
        description_frame.pack(side="left")
        ttk.Label(description_frame, text="Description:").pack(anchor="w")
        ttk.Entry(description_frame, textvariable=self.description_var, width=95).pack(pady=(2, 0))
        
        # Include Waiting checkbox
        waiting_frame = ttk.Frame(row3_frame)
        waiting_frame.pack(side="left", padx=(15, 0))
        ttk.Label(waiting_frame, text="").pack(anchor="w")  # Empty label for alignment
        ttk.Checkbutton(
            waiting_frame,
            text="Include Waiting",
            variable=self.include_waiting_var
        ).pack(pady=(2, 0))
        
        # Search buttons
        button_frame = ttk.Frame(row3_frame)
        button_frame.pack(side="right")
        ttk.Label(button_frame, text="").pack(anchor="w")  # Empty label for alignment
        
        button_container = ttk.Frame(button_frame)
        button_container.pack(pady=(2, 0))
        
        self.search_button = ttk.Button(
            button_container, 
            text="Search Hacks", 
            command=self._handle_search_cancel,
            width=12  # Fixed width to prevent button jumping
        )
        self.search_button.pack(side="left")
        
        clear_button = ttk.Button(
            button_container,
            text="Clear Filters",
            command=self.callback_clear
        )
        clear_button.pack(side="left", padx=(10, 0))
    
    def _handle_search_cancel(self):
        """Handle search/cancel button clicks"""
        if self.is_searching:
            # Currently searching - cancel it
            if self.callback_cancel:
                self.callback_cancel()
        else:
            # Not searching - start search
            self.callback_search()
    
    def set_searching_state(self, is_searching):
        """Update the search button state"""
        self.is_searching = is_searching
        if is_searching:
            self.search_button.configure(text="Cancel", state="normal")
        else:
            self.search_button.configure(text="Search Hacks", state="normal")
    
    def clear_all(self):
        """Clear all filter inputs"""
        self.name_var.set("")
        self.type_var.set("Any")
        self.authors_var.set("")
        self.tags_var.set("")
        self.description_var.set("")
        self.time_period_var.set("All Time")
        self.hof_var.set("Any")
        self.sa1_var.set("Any")
        self.collab_var.set("Any")
        self.demo_var.set("Any")
        self.include_waiting_var.set(False)
    
    def build_search_config(self):
        """Build API search configuration from filter inputs"""
        config = {}
        
        # Text-based filters
        if self.name_var.get().strip():
            config["name"] = self.name_var.get().strip()
        
        if self.authors_var.get().strip():
            config["author"] = self.authors_var.get().strip()
        
        if self.tags_var.get().strip():
            config["tags"] = self.tags_var.get().strip()
        
        if self.description_var.get().strip():
            config["description"] = self.description_var.get().strip()
        
        # Type filter
        if self.type_var.get() != "Any":
            display_type = self.type_var.get()
            api_type = None
            for api_key, display_val in TYPE_DISPLAY_LOOKUP.items():
                if display_val == display_type:
                    api_type = api_key
                    break
            if api_type:
                config["type"] = [api_type]
        
        # Boolean filters
        if self.hof_var.get() != "Any":
            config["hof"] = "1" if self.hof_var.get() == "Yes" else "0"
        
        if self.sa1_var.get() != "Any":
            config["sa1"] = "1" if self.sa1_var.get() == "Yes" else "0"
        
        if self.collab_var.get() != "Any":
            config["collab"] = "1" if self.collab_var.get() == "Yes" else "0"
        
        if self.demo_var.get() != "Any":
            config["demo"] = "1" if self.demo_var.get() == "Yes" else "0"
        
        return config


class DownloadResults:
    """Results table component for single download page"""
    
    def __init__(self, parent, callback_selection_change):
        self.parent = parent
        self.callback_selection_change = callback_selection_change
        
        # Table state
        self.tree = None
        self.status_label = None
        self.search_results = []
        self.selected_hacks = []
        self.sort_column = "date"
        self.sort_reverse = True  # Default to descending (newest first)
        self.select_all_state = False  # Track select all checkbox state
        
        # Create the results section
        self._create_results()
        
    def _create_results(self):
        """Create the search results table with simple, responsive layout"""
        results_frame = ttk.LabelFrame(self.parent, text="Search Results", padding=get_labelframe_padding())
        results_frame.pack(fill="x", expand=False, pady=(0, 10))  # Changed: fill="x" instead of "both", expand=False
        
        # Create treeview for results with a simple, reasonable height
        columns = ("select", "title", "type", "difficulty", "rating", "exits", "authors", "date")
        # Use a simple fixed height that works well across different screen sizes
        self.tree = ttk.Treeview(results_frame, columns=columns, show="headings", height=8)
        
        # Configure headers and columns
        headers = ["✓", "Title", "Type(s)", "Difficulty", "Rating", "Exit(s)", "Author(s)", "Date"]
        widths = [40, 250, 90, 100, 70, 60, 150, 90]
        min_widths = [35, 200, 70, 80, 60, 50, 120, 80]
        anchors = ["center", "w", "center", "center", "center", "center", "w", "center"]
        
        for i, (col, header, width, min_width, anchor) in enumerate(zip(columns, headers, widths, min_widths, anchors)):
            if col == "select":
                # Make select header clickable for select all functionality
                self.tree.heading(col, text=header, command=lambda: self.toggle_select_all())
            else:
                # Add sorting to other columns
                self.tree.heading(col, text=header, command=lambda c=col: self._sort_by_column(c))
            self.tree.column(col, width=width, minwidth=min_width, anchor=anchor)
        
        # Scrollbars (horizontal only shown when needed)
        v_scrollbar = ttk.Scrollbar(results_frame, orient="vertical", command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(results_frame, orient="horizontal", command=self.tree.xview)
        
        # Configure scrollbars with auto-hide for horizontal
        def on_configure(event=None):
            # Get the tree's actual vs displayed width
            tree_width = self.tree.winfo_width()
            if tree_width > 1:  # Avoid division by zero
                # Check if content is wider than visible area
                try:
                    bbox = self.tree.bbox(self.tree.get_children()[0]) if self.tree.get_children() else None
                    if bbox:
                        # Show/hide horizontal scrollbar based on content width
                        total_width = sum([self.tree.column(col, "width") for col in self.tree["columns"]])
                        if total_width > tree_width:
                            h_scrollbar.grid(row=1, column=0, sticky="ew")
                        else:
                            h_scrollbar.grid_remove()
                    else:
                        h_scrollbar.grid_remove()
                except (IndexError, tk.TclError):
                    h_scrollbar.grid_remove()
        
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        self.tree.bind('<Configure>', on_configure)
        
        # Grid layout
        self.tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        # h_scrollbar will be shown/hidden dynamically by on_configure
        
        results_frame.grid_rowconfigure(0, weight=1)
        results_frame.grid_columnconfigure(0, weight=1)
        
        # Bind events
        self.tree.bind("<Button-1>", self._on_tree_click)
        self.tree.bind("<space>", self._on_tree_space)
        
        # Status label
        self.status_label = ttk.Label(results_frame, text="", font=("Segoe UI", 9))
        self.status_label.grid(row=2, column=0, columnspan=2, pady=(10, 0))
        
        # Configure tag styles for selection
        self.tree.tag_configure("selected", background="#404040" if sv_ttk.get_theme() == "dark" else "#E3F2FD")
        self.tree.tag_configure("unselected", background="")
    
    def _sort_by_column(self, column):
        """Sort the table by the specified column"""
        # Toggle sort direction if clicking the same column
        if self.sort_column == column:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_column = column
            self.sort_reverse = False
        
        # Update header to show sort direction
        self._update_sort_headers()
        
        # Sort the results
        self._sort_results()
    
    def _update_sort_headers(self):
        """Update column headers to show sort direction"""
        headers = {"title": "Title", "type": "Type", "difficulty": "Difficulty", 
                  "rating": "Rating", "exits": "Exit(s)", "authors": "Author(s)", "date": "Date"}
        
        for col, base_text in headers.items():
            if col == self.sort_column:
                arrow = " ▼" if self.sort_reverse else " ▲"
                self.tree.heading(col, text=base_text + arrow)
            else:
                self.tree.heading(col, text=base_text)
    
    def _sort_results(self):
        """Sort the current results and update the tree display"""
        if not self.search_results:
            return
        
        # Create a list of (hack, item_id) pairs for sorting
        items_data = []
        for item in self.tree.get_children():
            item_index = self.tree.index(item)
            if item_index < len(self.search_results):
                hack = self.search_results[item_index]
                items_data.append((hack, item, self.tree.item(item, "values")))
        
        # Sort based on the selected column
        if self.sort_column == "title":
            items_data.sort(key=lambda x: x[0].get("name", "").lower(), reverse=self.sort_reverse)
        elif self.sort_column == "type":
            items_data.sort(key=lambda x: x[2][2], reverse=self.sort_reverse)
        elif self.sort_column == "difficulty":
            items_data.sort(key=lambda x: x[2][3], reverse=self.sort_reverse)
        elif self.sort_column == "rating":
            items_data.sort(key=lambda x: float(x[2][4]) if x[2][4] != "N/A" else -1, reverse=self.sort_reverse)
        elif self.sort_column == "exits":
            items_data.sort(key=lambda x: int(x[2][5]) if x[2][5] != "N/A" else -1, reverse=self.sort_reverse)
        elif self.sort_column == "authors":
            items_data.sort(key=lambda x: x[2][6].lower(), reverse=self.sort_reverse)
        elif self.sort_column == "date":
            items_data.sort(key=lambda x: x[2][7], reverse=self.sort_reverse)
        
        # Reorder items in tree
        for index, (hack, item, values) in enumerate(items_data):
            self.tree.move(item, "", index)
        
        # Update search_results to match new order
        self.search_results = [item[0] for item in items_data]
    
    def _on_tree_click(self, event):
        """Handle tree item click for selection"""
        item = self.tree.identify_row(event.y)
        if item:
            column = self.tree.identify_column(event.x)
            if column == "#1":  # Select column
                self._toggle_selection(item)
    
    def _on_tree_space(self, event):
        """Handle spacebar to toggle selection"""
        selection = self.tree.selection()
        if selection:
            self._toggle_selection(selection[0])
    
    def _toggle_selection(self, item):
        """Toggle selection state of an item"""
        current_values = list(self.tree.item(item, "values"))
        
        if current_values[0] == "":
            # Select the item
            current_values[0] = "✓"
            self.tree.item(item, values=current_values, tags=("selected",))
            
            # Add to selected hacks
            item_index = self.tree.index(item)
            if item_index < len(self.search_results):
                self.selected_hacks.append(self.search_results[item_index])
        else:
            # Deselect the item
            current_values[0] = ""
            self.tree.item(item, values=current_values, tags=("unselected",))
            
            # Remove from selected hacks
            item_index = self.tree.index(item)
            if item_index < len(self.search_results):
                hack_to_remove = self.search_results[item_index]
                if hack_to_remove in self.selected_hacks:
                    self.selected_hacks.remove(hack_to_remove)
        
        # Notify parent of selection change
        self.callback_selection_change()
    
    def toggle_select_all(self):
        """Toggle selection state of all visible items"""
        if not self.tree or not self.tree.get_children():
            return
        
        # Determine new state based on current select_all_state
        self.select_all_state = not self.select_all_state
        
        # Update header text to reflect current state  
        header_text = "✓"  # Keep single checkmark always
        self.tree.heading("select", text=header_text)
        
        # Apply selection state to all visible items
        for item in self.tree.get_children():
            current_values = list(self.tree.item(item, "values"))
            item_index = self.tree.index(item)
            
            if self.select_all_state:
                # Select the item
                current_values[0] = "✓"
                self.tree.item(item, values=current_values, tags=("selected",))
                
                # Add to selected hacks if not already there
                if item_index < len(self.search_results):
                    hack = self.search_results[item_index]
                    if hack not in self.selected_hacks:
                        self.selected_hacks.append(hack)
            else:
                # Deselect the item
                current_values[0] = ""
                self.tree.item(item, values=current_values, tags=("unselected",))
                
                # Remove from selected hacks
                if item_index < len(self.search_results):
                    hack = self.search_results[item_index]
                    if hack in self.selected_hacks:
                        self.selected_hacks.remove(hack)
        
        # Notify parent of selection change
        self.callback_selection_change()

    def display_results(self, results, time_period_filter="All Time"):
        """Display search results in the table (time filtering now handled server-side)"""
        self.search_results = results
        
        # Reset select all state when displaying new results
        self.select_all_state = False
        self.tree.heading("select", text="✓")
        
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Add results to table
        for hack in results:
            self._add_hack_to_tree(hack)
        
        # Sort results by default column
        if self.search_results:
            self._update_sort_headers()  # Update headers to show sort direction
            self._sort_results()
        
        # Update status (time filtering already applied server-side)
        total_results = len(self.search_results)
        if time_period_filter != "All Time":
            status_text = f"✅ Found {total_results} hacks (filtered by {time_period_filter})"
        else:
            status_text = f"✅ Found {total_results} hacks"
        
        self.set_status(status_text)
    
    def _add_hack_to_tree(self, hack):
        """Add a single hack to the tree view"""
        # Format the data for display
        title = hack.get("name", "Unknown")
        
        # Get type from raw_fields or fallback to main object
        raw_fields = hack.get("raw_fields", {})
        hack_type_raw = raw_fields.get("type") or hack.get("type", "")
        
        # Use the new helper function to format multiple types
        if isinstance(hack_type_raw, list):
            hack_type = format_types_display(hack_type_raw)
        else:
            hack_type = TYPE_DISPLAY_LOOKUP.get(hack_type_raw, hack_type_raw.title() if hack_type_raw else "Unknown")
        
        # Get difficulty from raw_fields
        raw_diff = raw_fields.get("difficulty", "")
        if not raw_diff or raw_diff in [None, "N/A"]:
            raw_diff = ""
        difficulty = DIFFICULTY_LOOKUP.get(raw_diff, "No Difficulty")
        
        # Get rating
        rating = hack.get("rating", "N/A")
        if rating and rating != "N/A":
            try:
                rating = f"{float(rating):.1f}"
            except (ValueError, TypeError):
                rating = "N/A"
        
        # Get exits (length field)
        exits = raw_fields.get("length") or hack.get("length", "N/A")
        if exits and exits != "N/A":
            try:
                exits = str(int(exits))
            except (ValueError, TypeError):
                exits = "N/A"
        
        # Get authors - parse array and join with commas
        authors_data = hack.get("authors", [])
        if isinstance(authors_data, list) and authors_data:
            # Extract just the names from author objects
            author_names = []
            for author in authors_data:
                if isinstance(author, dict):
                    name = author.get("name", "")
                else:
                    name = str(author)
                if name:
                    author_names.append(name)
            authors = ", ".join(author_names) if author_names else "Unknown"
        else:
            authors = "Unknown"
        
        # Get date from epoch time
        date_epoch = hack.get("time")
        if date_epoch:
            try:
                date_obj = datetime.fromtimestamp(int(date_epoch))
                date = date_obj.strftime("%Y-%m-%d")
            except (ValueError, TypeError, OSError):
                date = "Unknown"
        else:
            date = "Unknown"
        
        # Truncate long fields for display
        if len(title) > 35:
            title = title[:32] + "..."
        if len(authors) > 20:
            authors = authors[:17] + "..."
        
        self.tree.insert("", "end", values=(
            "",  # Empty for unselected
            title,
            hack_type,
            difficulty,
            rating,
            exits,
            authors,
            date
        ), tags=("unselected",))
    
    def clear_results(self):
        """Clear search results"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.search_results = []
        self.selected_hacks = []
        # Reset select all state
        self.select_all_state = False
        if self.tree:
            self.tree.heading("select", text="✓")
    
    def clear_selection(self):
        """Clear all selections"""
        self.selected_hacks = []
        
        # Reset select all state
        self.select_all_state = False
        if self.tree:
            self.tree.heading("select", text="✓")
        
        for item in self.tree.get_children():
            current_values = list(self.tree.item(item, "values"))
            current_values[0] = ""
            self.tree.item(item, values=current_values, tags=("unselected",))
    
    def set_status(self, text):
        """Set the status label text"""
        if self.status_label:
            self.status_label.configure(text=text)
    
    def get_selected_count(self):
        """Get the number of selected hacks"""
        return len(self.selected_hacks)
    
    def get_selected_hacks(self):
        """Get the list of selected hacks"""
        return self.selected_hacks.copy()


class DownloadButton:
    """Download button component for single download page"""
    
    def __init__(self, parent, callback_download, callback_cancel=None):
        self.parent = parent
        self.callback_download = callback_download
        self.callback_cancel = callback_cancel
        self.download_button = None
        self.progress_label = None
        self.is_downloading = False
        
        # Create the download button
        self._create_button()
    
    def _create_button(self):
        """Create the download button"""
        download_frame = ttk.Frame(self.parent)
        download_frame.pack(fill="x", pady=(10, 0))
        
        # Download button
        self.download_button = ttk.Button(
            download_frame,
            text="Download & Patch",
            command=self._handle_download_cancel,
            style="Large.Accent.TButton",
            state="disabled"
        )
        self.download_button.pack()
        
        # Progress label (initially hidden)
        self.progress_label = ttk.Label(
            download_frame,
            text="",
            font=("Segoe UI", 9)
        )
        self.progress_label.pack(pady=(5, 0))
    
    def _handle_download_cancel(self):
        """Handle download/cancel button clicks"""
        if self.is_downloading:
            # Currently downloading - cancel it
            if self.callback_cancel:
                self.callback_cancel()
        else:
            # Not downloading - start download
            self.callback_download()
    
    def update_state(self, selected_count):
        """Update button state based on selected count"""
        if not self.is_downloading:
            if selected_count > 0:
                self.download_button.configure(state="normal")
                self.download_button.configure(text=f"Download & Patch ({selected_count})")
            else:
                self.download_button.configure(state="disabled")
                self.download_button.configure(text="Download & Patch")
    
    def set_downloading(self, is_downloading=True):
        """Set the button to downloading state"""
        self.is_downloading = is_downloading
        if is_downloading:
            self.download_button.configure(text="Cancel", state="normal")
            self.progress_label.configure(text="Starting download...")
        else:
            # Reset to normal state - let update_state handle the proper text
            self.download_button.configure(state="normal")
            self.progress_label.configure(text="")
            self.is_downloading = False
    
    def update_progress(self, current, total, hack_name=""):
        """Update progress display during download"""
        if self.is_downloading and self.progress_label:
            if hack_name:
                progress_text = f"Processing {current}/{total}: {hack_name}"
            else:
                progress_text = f"Processing {current}/{total} hacks..."
            self.progress_label.configure(text=progress_text)
    
    def get_button(self):
        """Get the button widget reference"""
        return self.download_button
