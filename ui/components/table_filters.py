import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

class TableFilters:
    """Manages table filtering logic"""
    
    def __init__(self, apply_callback):
        self.apply_callback = apply_callback
        self.data_manager = None  # Will be set when create_filter_ui is called
        
        # Filter variables
        self.name_filter = tk.StringVar()
        self.type_filter = tk.StringVar(value="All")
        self.difficulty_filter = tk.StringVar(value="All")
        self.completed_filter = tk.StringVar(value="All")
        self.rating_filter = tk.StringVar(value="All")
        self.hall_of_fame_filter = tk.StringVar(value="All")
        self.sa1_filter = tk.StringVar(value="All")
        self.collaboration_filter = tk.StringVar(value="All")
        self.demo_filter = tk.StringVar(value="All")
        
    def create_filter_ui(self, parent, data_manager):
        """Create filter UI elements"""
        self.data_manager = data_manager  # Store reference for Add Hack functionality
        filter_frame = ttk.LabelFrame(parent, text="Filters", padding=15)
        
        # Create main grid container
        grid_container = ttk.Frame(filter_frame)
        grid_container.pack(fill="x")
        
        # Column 1 - Name and dropdowns
        col1_frame = ttk.Frame(grid_container)
        col1_frame.pack(side="left", fill="x", padx=(0, 15))
        
        # Name filter
        self._create_name_filter(col1_frame)
        
        # Dropdown filters
        self._create_dropdown_filters(col1_frame, data_manager)
        
        # Column 2 - HoF and SA-1
        col2_frame = ttk.Frame(grid_container)
        col2_frame.pack(side="left", padx=(0, 15))
        
        self._create_radio_filters_col2(col2_frame)
        
        # Column 3 - Collab and Demo
        col3_frame = ttk.Frame(grid_container)
        col3_frame.pack(side="right")
        
        self._create_radio_filters_col3(col3_frame)
        
        # Clear button
        self._create_clear_button(filter_frame)
        
        return filter_frame
        
    def _create_name_filter(self, parent):
        """Create name filter"""
        name_frame = ttk.Frame(parent)
        name_frame.pack(fill="x", pady=(0, 8))
        ttk.Label(name_frame, text="Name:", font=("Segoe UI", 9, "bold")).pack(anchor="w")
        name_entry = ttk.Entry(name_frame, textvariable=self.name_filter, width=90)
        name_entry.pack(fill="x", pady=(2, 0))
        name_entry.bind("<KeyRelease>", lambda e: self.apply_callback())
        
    def _create_dropdown_filters(self, parent, data_manager):
        """Create dropdown filter controls"""
        dropdowns_frame = ttk.Frame(parent)
        dropdowns_frame.pack(fill="x")
        
        # Type filter
        type_frame = ttk.Frame(dropdowns_frame)
        type_frame.pack(side="left", padx=(0, 12))
        ttk.Label(type_frame, text="Type:", font=("Segoe UI", 9, "bold")).pack(anchor="w")
        types = ["All"] + data_manager.get_unique_types()
        self.type_combo = ttk.Combobox(type_frame, textvariable=self.type_filter, 
                                     values=types, state="readonly", width=14)
        self.type_combo.pack(pady=(2, 0))
        self.type_combo.bind("<<ComboboxSelected>>", lambda e: self.apply_callback())
        
        # Difficulty filter
        diff_frame = ttk.Frame(dropdowns_frame)
        diff_frame.pack(side="left", padx=(0, 12))
        ttk.Label(diff_frame, text="Difficulty:", font=("Segoe UI", 9, "bold")).pack(anchor="w")
        difficulties = ["All"] + data_manager.get_unique_difficulties()
        self.diff_combo = ttk.Combobox(diff_frame, textvariable=self.difficulty_filter, 
                                     values=difficulties, state="readonly", width=14)
        self.diff_combo.pack(pady=(2, 0))
        self.diff_combo.bind("<<ComboboxSelected>>", lambda e: self.apply_callback())
        
        # More dropdown filters...
        self._create_remaining_dropdowns(dropdowns_frame)
        
    def _create_remaining_dropdowns(self, parent):
        """Create completed and rating dropdowns"""
        # Completed filter
        completed_frame = ttk.Frame(parent)
        completed_frame.pack(side="left", padx=(0, 12))
        ttk.Label(completed_frame, text="Completed:", font=("Segoe UI", 9, "bold")).pack(anchor="w")
        completed_combo = ttk.Combobox(completed_frame, textvariable=self.completed_filter,
                                     values=["All", "Yes", "No"], state="readonly", width=14)
        completed_combo.pack(pady=(2, 0))
        completed_combo.bind("<<ComboboxSelected>>", lambda e: self.apply_callback())
        
        # Rating filter
        rating_frame = ttk.Frame(parent)
        rating_frame.pack(side="left")
        ttk.Label(rating_frame, text="Rating:", font=("Segoe UI", 9, "bold")).pack(anchor="w")
        rating_combo = ttk.Combobox(rating_frame, textvariable=self.rating_filter,
                                   values=["All", "★★★★★", "★★★★☆", "★★★☆☆", "★★☆☆☆", "★☆☆☆☆", "☆☆☆☆☆"],
                                   state="readonly", width=14)
        rating_combo.pack(pady=(2, 0))
        rating_combo.bind("<<ComboboxSelected>>", lambda e: self.apply_callback())
        
    def _create_radio_filters_col2(self, parent):
        """Create HoF and SA-1 radio filters"""
        # HoF filter
        hof_frame = ttk.Frame(parent)
        hof_frame.pack(pady=(0, 8))
        ttk.Label(hof_frame, text="HoF:", font=("Segoe UI", 9, "bold")).pack(anchor="w")
        hof_radio_frame = ttk.Frame(hof_frame)
        hof_radio_frame.pack(pady=(2, 0))
        
        for display, value in [("Any", "All"), ("Yes", "Yes"), ("No", "No")]:
            ttk.Radiobutton(hof_radio_frame, text=display, variable=self.hall_of_fame_filter,
                           value=value, command=self.apply_callback).pack(side="left", padx=(0, 5))
        
        # SA-1 filter
        sa1_frame = ttk.Frame(parent)
        sa1_frame.pack()
        ttk.Label(sa1_frame, text="SA-1:", font=("Segoe UI", 9, "bold")).pack(anchor="w")
        sa1_radio_frame = ttk.Frame(sa1_frame)
        sa1_radio_frame.pack(pady=(2, 0))
        
        for display, value in [("Any", "All"), ("Yes", "Yes"), ("No", "No")]:
            ttk.Radiobutton(sa1_radio_frame, text=display, variable=self.sa1_filter,
                           value=value, command=self.apply_callback).pack(side="left", padx=(0, 5))
                           
    def _create_radio_filters_col3(self, parent):
        """Create Collab and Demo radio filters"""
        # Collab filter
        collab_frame = ttk.Frame(parent)
        collab_frame.pack(pady=(0, 8))
        ttk.Label(collab_frame, text="Collab:", font=("Segoe UI", 9, "bold")).pack(anchor="w")
        collab_radio_frame = ttk.Frame(collab_frame)
        collab_radio_frame.pack(pady=(2, 0))
        
        for display, value in [("Any", "All"), ("Yes", "Yes"), ("No", "No")]:
            ttk.Radiobutton(collab_radio_frame, text=display, variable=self.collaboration_filter,
                           value=value, command=self.apply_callback).pack(side="left", padx=(0, 5))
        
        # Demo filter
        demo_frame = ttk.Frame(parent)
        demo_frame.pack()
        ttk.Label(demo_frame, text="Demo:", font=("Segoe UI", 9, "bold")).pack(anchor="w")
        demo_radio_frame = ttk.Frame(demo_frame)
        demo_radio_frame.pack(pady=(2, 0))
        
        for display, value in [("Any", "All"), ("Yes", "Yes"), ("No", "No")]:
            ttk.Radiobutton(demo_radio_frame, text=display, variable=self.demo_filter,
                           value=value, command=self.apply_callback).pack(side="left", padx=(0, 5))
                           
    def _create_clear_button(self, parent):
        """Create clear filters button"""
        clear_button_frame = ttk.Frame(parent)
        clear_button_frame.pack(fill="x", pady=(15, 0))
        
        button_container = ttk.Frame(clear_button_frame)
        button_container.pack(side="right")
        
        ttk.Button(button_container, text="Refresh List", 
                  command=lambda: None).pack(side="left", padx=(0, 10))  # Will be connected later
        
        ttk.Button(button_container, text="Clear All Filters", 
                  command=self.clear_filters).pack(side="left", padx=(0, 10))
        
        ttk.Button(button_container, text="Add Hack", 
                  command=self.show_add_hack_dialog).pack(side="left")
                  
    def clear_filters(self):
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
        self.apply_callback()
        
    def refresh_dropdown_values(self, data_manager):
        """Refresh dropdown values when data changes"""
        if hasattr(self, 'type_combo'):
            types = ["All"] + data_manager.get_unique_types()
            current_type = self.type_filter.get()
            self.type_combo['values'] = types
            if current_type not in types:
                self.type_filter.set("All")
        
        if hasattr(self, 'diff_combo'):
            difficulties = ["All"] + data_manager.get_unique_difficulties()
            current_diff = self.difficulty_filter.get()
            self.diff_combo['values'] = difficulties
            if current_diff not in difficulties:
                self.difficulty_filter.set("All")
                
    def apply_filters(self, hacks):
        """Apply all active filters to the list of hacks"""
        filtered_hacks = []
        
        for hack in hacks:
            if self._hack_passes_filters(hack):
                filtered_hacks.append(hack)
                
        return filtered_hacks
        
    def _hack_passes_filters(self, hack):
        """Check if a hack passes all current filters"""
        # Name filter
        name_filter_text = self.name_filter.get().strip().lower()
        if name_filter_text and name_filter_text not in hack.get("title", "").lower():
            return False
            
        # Type filter
        type_filter_value = self.type_filter.get()
        if type_filter_value != "All" and hack.get("hack_type", "").title() != type_filter_value:
            return False
            
        # Difficulty filter
        difficulty_filter_value = self.difficulty_filter.get()
        if difficulty_filter_value != "All" and hack.get("difficulty") != difficulty_filter_value:
            return False
            
        # More filter checks...
        return self._check_remaining_filters(hack)
        
    def _check_remaining_filters(self, hack):
        """Check remaining filters"""
        # Completed filter
        completed_filter_value = self.completed_filter.get()
        if completed_filter_value == "Yes" and not hack.get("completed", False):
            return False
        elif completed_filter_value == "No" and hack.get("completed", False):
            return False
            
        # Rating filter
        rating_filter_value = self.rating_filter.get()
        if rating_filter_value != "All":
            stars_count = rating_filter_value.count("★")
            if hack.get("personal_rating", 0) != stars_count:
                return False
                
        # Boolean filters
        filters_to_check = [
            ("hall_of_fame", self.hall_of_fame_filter.get(), "hall_of_fame"),
            ("sa1_compatibility", self.sa1_filter.get(), "sa1_compatibility"),
            ("collaboration", self.collaboration_filter.get(), "collaboration"),
            ("demo", self.demo_filter.get(), "demo")
        ]
        
        for field_name, filter_value, hack_field in filters_to_check:
            if filter_value == "Yes" and not hack.get(hack_field, False):
                return False
            elif filter_value == "No" and hack.get(hack_field, False):
                return False
                
        return True
    
    def show_add_hack_dialog(self):
        """Show dialog to add a new hack manually"""
        if not self.data_manager:
            messagebox.showerror("Error", "Data manager not available")
            return
            
        dialog = AddHackDialog(None, self.data_manager, self.apply_callback)
        dialog.show()


class AddHackDialog:
    """Dialog for adding a hack manually"""
    
    def __init__(self, parent, data_manager, refresh_callback):
        self.data_manager = data_manager
        self.refresh_callback = refresh_callback
        self.dialog = None
        
    def show(self):
        """Show the add hack dialog"""
        self.dialog = tk.Toplevel()
        self.dialog.title("Add Hack")
        self.dialog.geometry("750x650")  # Made wider to fit Demo radio buttons
        self.dialog.resizable(False, False)
        self.dialog.grab_set()  # Make dialog modal
        
        # Center the dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (750 // 2)  # Updated for new width
        y = (self.dialog.winfo_screenheight() // 2) - (650 // 2)
        self.dialog.geometry(f"750x650+{x}+{y}")  # Updated for new width
        
        self._create_form()
        
    def _create_form(self):
        """Create the form layout"""
        main_frame = ttk.Frame(self.dialog, padding=20)
        main_frame.pack(fill="both", expand=True)
        
        # Hack Information Section
        info_frame = ttk.LabelFrame(main_frame, text="Hack Information", padding=15)
        info_frame.pack(fill="x", pady=(0, 15))
        
        # Configure grid layout - 4 columns with equal weight
        info_frame.grid_columnconfigure(0, weight=1)
        info_frame.grid_columnconfigure(1, weight=1) 
        info_frame.grid_columnconfigure(2, weight=1)
        info_frame.grid_columnconfigure(3, weight=1)
        
        # Row 0: Title (spans full width)
        title_frame = ttk.Frame(info_frame)
        title_frame.grid(row=0, column=0, columnspan=4, sticky="ew", padx=0, pady=(0, 15))
        ttk.Label(title_frame, text="Title:", font=("Segoe UI", 10, "bold")).pack(anchor="w")
        self.title_var = tk.StringVar()
        ttk.Entry(title_frame, textvariable=self.title_var, font=("Segoe UI", 10)).pack(fill="x", pady=(5, 0))
        
        # Row 1: Type, Difficulty, Exits, Authors
        # Type (column 0)
        type_frame = ttk.Frame(info_frame)
        type_frame.grid(row=1, column=0, sticky="ew", padx=(0, 5), pady=(0, 15))
        ttk.Label(type_frame, text="Type:", font=("Segoe UI", 10, "bold")).pack(anchor="w")
        self.type_var = tk.StringVar()
        type_combo = ttk.Combobox(type_frame, textvariable=self.type_var, state="readonly",
                                 font=("Segoe UI", 10))
        type_combo['values'] = ["Kaizo", "Pit", "Puzzle", "Standard", "Tool-Assisted"]  # Alphabetical
        type_combo.set("Kaizo")  # Default to Kaizo
        type_combo.pack(fill="x", pady=(5, 0))
        
        # Difficulty (column 1)
        diff_frame = ttk.Frame(info_frame)
        diff_frame.grid(row=1, column=1, sticky="ew", padx=5, pady=(0, 15))
        ttk.Label(diff_frame, text="Difficulty:", font=("Segoe UI", 10, "bold")).pack(anchor="w")
        self.difficulty_var = tk.StringVar()
        difficulty_combo = ttk.Combobox(diff_frame, textvariable=self.difficulty_var, state="readonly", 
                                       font=("Segoe UI", 10))
        difficulty_combo['values'] = ["Newcomer", "Casual", "Skilled", "Advanced", "Expert", "Master", "Grandmaster"]
        difficulty_combo.set("Newcomer")  # Default to Newcomer
        difficulty_combo.pack(fill="x", pady=(5, 0))
        
        # Exits (column 2)
        exits_frame = ttk.Frame(info_frame)
        exits_frame.grid(row=1, column=2, sticky="ew", padx=5, pady=(0, 15))
        ttk.Label(exits_frame, text="Exits:", font=("Segoe UI", 10, "bold")).pack(anchor="w")
        self.exits_var = tk.StringVar(value="0")
        ttk.Entry(exits_frame, textvariable=self.exits_var, font=("Segoe UI", 10)).pack(fill="x", pady=(5, 0))
        
        # Authors (column 3)
        authors_frame = ttk.Frame(info_frame)
        authors_frame.grid(row=1, column=3, sticky="ew", padx=(5, 0), pady=(0, 15))
        ttk.Label(authors_frame, text="Authors:", font=("Segoe UI", 10, "bold")).pack(anchor="w")
        self.authors_var = tk.StringVar()
        ttk.Entry(authors_frame, textvariable=self.authors_var, font=("Segoe UI", 10)).pack(fill="x", pady=(5, 0))
        
        # Row 2: Hall of Fame, SA-1, Collaboration, Demo (all 4 boolean fields)
        # Hall of Fame (column 0)
        hof_frame = ttk.Frame(info_frame)
        hof_frame.grid(row=2, column=0, sticky="ew", padx=(0, 5), pady=(0, 15))
        ttk.Label(hof_frame, text="Hall of Fame:", font=("Segoe UI", 10, "bold")).pack(anchor="w")
        self.hof_var = tk.StringVar(value="No")
        hof_radio_frame = ttk.Frame(hof_frame)
        hof_radio_frame.pack(anchor="w", pady=(5, 0))
        ttk.Radiobutton(hof_radio_frame, text="Yes", variable=self.hof_var, value="Yes").pack(side="left", padx=(0, 10))
        ttk.Radiobutton(hof_radio_frame, text="No", variable=self.hof_var, value="No").pack(side="left")
        
        # SA-1 (column 1)
        sa1_frame = ttk.Frame(info_frame)
        sa1_frame.grid(row=2, column=1, sticky="ew", padx=5, pady=(0, 15))
        ttk.Label(sa1_frame, text="SA-1:", font=("Segoe UI", 10, "bold")).pack(anchor="w")
        self.sa1_var = tk.StringVar(value="No")
        sa1_radio_frame = ttk.Frame(sa1_frame)
        sa1_radio_frame.pack(anchor="w", pady=(5, 0))
        ttk.Radiobutton(sa1_radio_frame, text="Yes", variable=self.sa1_var, value="Yes").pack(side="left", padx=(0, 10))
        ttk.Radiobutton(sa1_radio_frame, text="No", variable=self.sa1_var, value="No").pack(side="left")
        
        # Collaboration (column 2)
        collab_frame = ttk.Frame(info_frame)
        collab_frame.grid(row=2, column=2, sticky="ew", padx=5, pady=(0, 15))
        ttk.Label(collab_frame, text="Collaboration:", font=("Segoe UI", 10, "bold")).pack(anchor="w")
        self.collab_var = tk.StringVar(value="No")
        collab_radio_frame = ttk.Frame(collab_frame)
        collab_radio_frame.pack(anchor="w", pady=(5, 0))
        ttk.Radiobutton(collab_radio_frame, text="Yes", variable=self.collab_var, value="Yes").pack(side="left", padx=(0, 10))
        ttk.Radiobutton(collab_radio_frame, text="No", variable=self.collab_var, value="No").pack(side="left")
        
        # Demo (column 3)
        demo_frame = ttk.Frame(info_frame)
        demo_frame.grid(row=2, column=3, sticky="ew", padx=(5, 0), pady=(0, 15))
        ttk.Label(demo_frame, text="Demo:", font=("Segoe UI", 10, "bold")).pack(anchor="w")
        self.demo_var = tk.StringVar(value="No")
        demo_radio_frame = ttk.Frame(demo_frame)
        demo_radio_frame.pack(anchor="w", pady=(5, 0))
        ttk.Radiobutton(demo_radio_frame, text="Yes", variable=self.demo_var, value="Yes").pack(side="left", padx=(0, 10))
        ttk.Radiobutton(demo_radio_frame, text="No", variable=self.demo_var, value="No").pack(side="left")
        
        # Personal Stats Section
        stats_frame = ttk.LabelFrame(main_frame, text="Personal Stats", padding=15)
        stats_frame.pack(fill="x", pady=(0, 15))
        
        # First stats row: Completed, Completed Date, Rating, Time to Beat
        stats_row1 = ttk.Frame(stats_frame)
        stats_row1.pack(fill="x", pady=(0, 15))
        
        # Completed (left)
        completed_frame = ttk.Frame(stats_row1)
        completed_frame.pack(side="left", padx=(0, 20))
        ttk.Label(completed_frame, text="Completed:", font=("Segoe UI", 10, "bold")).pack(anchor="w")
        self.completed_var = tk.StringVar(value="No")
        self.completed_var.trace_add("write", self._on_completed_change)  # Auto-set date
        completed_radio_frame = ttk.Frame(completed_frame)
        completed_radio_frame.pack(anchor="w", pady=(5, 0))
        ttk.Radiobutton(completed_radio_frame, text="Yes", variable=self.completed_var, value="Yes").pack(side="left", padx=(0, 10))
        ttk.Radiobutton(completed_radio_frame, text="No", variable=self.completed_var, value="No").pack(side="left")
        
        # Completed Date
        date_frame = ttk.Frame(stats_row1)
        date_frame.pack(side="left", padx=(0, 20))
        ttk.Label(date_frame, text="Completed Date:", font=("Segoe UI", 10, "bold")).pack(anchor="w")
        self.completed_date_var = tk.StringVar()
        self.completed_date_var.trace_add("write", self._on_completed_date_change)  # Auto-set completed
        date_entry = ttk.Entry(date_frame, textvariable=self.completed_date_var, font=("Segoe UI", 10), width=12)
        date_entry.pack(pady=(5, 0))
        date_entry.bind("<FocusOut>", self._on_date_focus_out)
        
        # Rating with interactive stars
        rating_frame = ttk.Frame(stats_row1)
        rating_frame.pack(side="left", padx=(0, 20))
        ttk.Label(rating_frame, text="Rating:", font=("Segoe UI", 10, "bold")).pack(anchor="w")
        self.rating_var = tk.IntVar(value=0)
        
        # Create star rating frame
        star_frame = ttk.Frame(rating_frame)
        star_frame.pack(pady=(5, 0))
        
        # Create clickable star labels
        self.star_labels = []
        for i in range(5):
            star_label = ttk.Label(star_frame, text="☆", font=("Segoe UI", 14))
            star_label.pack(side="left", padx=1)
            star_label.bind("<Button-1>", lambda e, star=i+1: self._set_rating(star))
            star_label.bind("<Enter>", lambda e, star=i+1: self._hover_rating(star))
            star_label.bind("<Leave>", lambda e: self._hover_rating(0))
            self.star_labels.append(star_label)
        
        # Time to Beat
        time_frame = ttk.Frame(stats_row1)
        time_frame.pack(side="left")
        ttk.Label(time_frame, text="Time to Beat:", font=("Segoe UI", 10, "bold")).pack(anchor="w")
        self.time_to_beat_var = tk.StringVar(value="")  # Empty by default like history page
        time_entry = ttk.Entry(time_frame, textvariable=self.time_to_beat_var, font=("Segoe UI", 10), width=12)
        time_entry.pack(pady=(5, 0))
        time_entry.bind("<FocusOut>", self._on_time_focus_out)  # Format time on focus out
        
        # Add tooltip for time format help
        def show_time_help(event):
            tooltip_text = ("Time formats:\n"
                          "• HH:MM:SS (1:30:45)\n"
                          "• MM:SS (90:30)\n"
                          "• 2h 30m 15s\n"
                          "• 90m or 90 minutes\n"
                          "• 90 (assumes minutes)\n"
                          "• 14d 10h 2m 1s")
            # Simple tooltip - just bind to show help in status
            
        time_entry.bind("<FocusIn>", show_time_help)
        
        # Notes (full width)
        notes_frame = ttk.Frame(stats_frame)
        notes_frame.pack(fill="x")
        ttk.Label(notes_frame, text="Notes:", font=("Segoe UI", 10, "bold")).pack(anchor="w")
        self.notes_var = tk.StringVar()
        ttk.Entry(notes_frame, textvariable=self.notes_var, font=("Segoe UI", 10)).pack(fill="x", pady=(5, 0))
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x", pady=(20, 0))
        
        ttk.Button(button_frame, text="Cancel", command=self.dialog.destroy).pack(side="right", padx=(10, 0))
        ttk.Button(button_frame, text="Save Hack", command=self._save_hack).pack(side="right")
    
    def _set_rating(self, rating):
        """Set the rating and update star display"""
        current_rating = self.rating_var.get()
        
        # If clicking beyond the current rating, set to that rating
        # If clicking on or before the current rating, clear it (set to 0)
        if rating > current_rating:
            self.rating_var.set(rating)
        else:
            self.rating_var.set(0)  # Clear rating
            
        self._update_star_display(self.rating_var.get())
    
    def _hover_rating(self, rating):
        """Update star display on hover"""
        if rating == 0:
            # Show actual rating on mouse leave
            self._update_star_display(self.rating_var.get())
        else:
            # Show hover preview
            self._update_star_display(rating, hover=True)
    
    def _update_star_display(self, rating, hover=False):
        """Update the visual star display"""
        for i, label in enumerate(self.star_labels):
            if i < rating:
                label.config(text="★", foreground="gold" if hover else "")
            else:
                label.config(text="☆", foreground="")
    
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
        """Parse user time input and convert to seconds (same as history page)"""
        if not time_str or time_str.strip() == "":
            return 0
        
        time_str = time_str.strip()
        
        import re
        
        # Pattern for flexible shortened formats with days
        pattern_flexible = re.match(r'(?:(\d+)d\s*)?(?:(\d+)h?\s*)?(?:(\d+)m?\s*)?(?:(\d+)s?\s*)?$', time_str.lower())
        if pattern_flexible and any(pattern_flexible.groups()):
            days = int(pattern_flexible.group(1) or 0)
            hours = int(pattern_flexible.group(2) or 0)
            minutes = int(pattern_flexible.group(3) or 0) 
            seconds = int(pattern_flexible.group(4) or 0)
            
            # If there's a 'd' in the input, treat it as the day format
            if 'd' in time_str.lower():
                return days * 86400 + hours * 3600 + minutes * 60 + seconds
            
            # If no 'd', check for standard letter suffixes
            if re.search(r'[hms]', time_str.lower()):
                return hours * 3600 + minutes * 60 + seconds
        
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
                return None, "Time cannot be negative"
            if seconds > 999 * 3600:  # 999 hours max
                return None, "Time cannot exceed 999 hours"
            return seconds, None
        except ValueError:
            return None, ("Invalid time format. Valid formats:\n"
                         "• HH:MM:SS (1:30:45)\n"
                         "• MM:SS (90:30)\n"
                         "• 2h 30m 15s\n"
                         "• 90m or 90 minutes\n"
                         "• 90 (assumes minutes)\n"
                         "• 14d 10h 2m 1s")
    
    def _on_completed_change(self, *args):
        """Handle completed radio button changes - auto-set date like history page"""
        if self.completed_var.get() == "Yes" and not self.completed_date_var.get().strip():
            # Auto-set to today's date when marking completed
            from datetime import datetime
            today = datetime.now().strftime("%Y-%m-%d")
            self.completed_date_var.set(today)
        elif self.completed_var.get() == "No":
            # Clear date when marking as not completed
            self.completed_date_var.set("")
    
    def _on_completed_date_change(self, *args):
        """Handle completed date changes - auto-set completed status like history page"""
        date_text = self.completed_date_var.get().strip()
        if date_text and self.completed_var.get() == "No":
            # Auto-set completed to Yes when date is added
            self.completed_var.set("Yes")
        elif not date_text and self.completed_var.get() == "Yes":
            # Auto-set completed to No when date is removed
            self.completed_var.set("No")
    
    def _on_date_focus_out(self, event):
        """Handle date field focus out - validate and normalize date"""
        date_text = self.completed_date_var.get().strip()
        if date_text:
            # Try to parse and normalize the date
            from datetime import datetime
            date_formats = [
                "%Y-%m-%d", "%Y/%m/%d", "%m/%d/%Y", "%d/%m/%Y", "%m-%d-%Y", "%d-%m-%Y",
                "%m.%d.%Y", "%d.%m.%Y", "%Y.%m.%d", "%d %m %Y", "%m %d %Y", "%Y %m %d",
                "%B %d, %Y", "%d %B %Y", "%b %d, %Y", "%d %b %Y", "%Y%m%d", "%m%d%Y", "%d%m%Y"
            ]
            
            for date_format in date_formats:
                try:
                    parsed_date = datetime.strptime(date_text, date_format)
                    normalized_date = parsed_date.strftime("%Y-%m-%d")
                    self.completed_date_var.set(normalized_date)
                    return  # Success
                except ValueError:
                    continue
    
    def _on_time_focus_out(self, event):
        """Handle time field focus out - format display like history page"""
        time_text = self.time_to_beat_var.get().strip()
        if time_text:
            try:
                # Parse the time input
                time_seconds = self._parse_time_input(time_text)
                # Format it back to a readable format
                formatted_time = self._format_time_display(time_seconds)
                self.time_to_beat_var.set(formatted_time)
            except ValueError:
                # Leave invalid input as-is for user to fix
                pass
    
    def _validate_form_data(self):
        """Validate all form data before saving"""
        errors = []
        
        # Validate title (required)
        title = self.title_var.get().strip()
        if not title:
            errors.append("Title is required")
        
        # Validate exits (must be numeric)
        exits_str = self.exits_var.get().strip()
        if exits_str:
            try:
                exits = int(exits_str)
                if exits < 0:
                    errors.append("Exits must be a non-negative number")
            except ValueError:
                errors.append("Exits must be a valid number")
        
        # Validate completed date if provided
        completed_date = self.completed_date_var.get().strip()
        if completed_date:
            # Use the same validation as history page
            from datetime import datetime
            date_formats = [
                "%Y-%m-%d", "%Y/%m/%d", "%m/%d/%Y", "%d/%m/%Y", "%m-%d-%Y", "%d-%m-%Y",
                "%m.%d.%Y", "%d.%m.%Y", "%Y.%m.%d", "%d %m %Y", "%m %d %Y", "%Y %m %d",
                "%B %d, %Y", "%d %B %Y", "%b %d, %Y", "%d %b %Y", "%Y%m%d", "%m%d%Y", "%d%m%Y"
            ]
            
            date_valid = False
            for date_format in date_formats:
                try:
                    parsed_date = datetime.strptime(completed_date, date_format)
                    # Normalize to YYYY-MM-DD format
                    self.completed_date_var.set(parsed_date.strftime("%Y-%m-%d"))
                    date_valid = True
                    break
                except ValueError:
                    continue
                    
            if not date_valid:
                errors.append("Completed date must be in valid format (e.g., 2025-01-15)")
        
        # Validate time to beat (using same logic as history page)
        time_str = self.time_to_beat_var.get().strip()
        if time_str:
            # First try to parse as formatted display (e.g. "1h 30m 15s")
            try:
                time_seconds = self._parse_time_input(time_str)
                if time_seconds < 0:
                    errors.append("Time to beat cannot be negative")
                elif time_seconds > 999 * 3600:  # 999 hours max
                    errors.append("Time to beat cannot exceed 999 hours")
            except ValueError:
                errors.append("Time to beat format is invalid. Use formats like: 1h 30m, 90:30, or 90m")
        
        return errors
        
    def _save_hack(self):
        """Save the hack data after validation"""
        # Validate form data first
        validation_errors = self._validate_form_data()
        if validation_errors:
            error_message = "Please fix the following errors:\n\n" + "\n".join(f"• {error}" for error in validation_errors)
            messagebox.showerror("Validation Error", error_message)
            return
            
        # Get next user ID
        user_id = self._get_next_user_id()
        
        # Parse authors
        authors_text = self.authors_var.get().strip()
        authors = [author.strip() for author in authors_text.split(",")] if authors_text else []
        
        # Convert capitalized values to lowercase for storage consistency
        difficulty_storage = self.difficulty_var.get().lower()
        type_storage = self.type_var.get().lower().replace("-", "")  # Remove hyphens for consistency
        
        # Parse time to beat using the same logic as history page
        time_str = self.time_to_beat_var.get().strip()
        time_seconds = 0
        if time_str:
            try:
                time_seconds = self._parse_time_input(time_str)
            except ValueError:
                time_seconds = 0  # Fall back to 0 if parsing fails (should be caught by validation)
        
        # Create hack data
        hack_data = {
            "title": self.title_var.get().strip(),
            "current_difficulty": difficulty_storage,
            "folder_name": difficulty_storage,
            "hack_type": type_storage,
            "hack_types": [type_storage],
            "hall_of_fame": self.hof_var.get() == "Yes",
            "sa1_compatibility": self.sa1_var.get() == "Yes",
            "collaboration": self.collab_var.get() == "Yes",
            "demo": self.demo_var.get() == "Yes",
            "authors": authors,
            "exits": int(self.exits_var.get()) if self.exits_var.get().strip() else 0,
            "completed": self.completed_var.get() == "Yes",
            "completed_date": self.completed_date_var.get().strip(),
            "personal_rating": self.rating_var.get(),  # Now using IntVar directly
            "time_to_beat": time_seconds,  # Store as seconds like history page
            "notes": self.notes_var.get().strip(),
            "obsolete": False,
            "file_path": "",  # No file path for user-added hacks
            "additional_paths": []
        }
        
        # Add to data manager
        success = self.data_manager.add_user_hack(user_id, hack_data)
        
        if success:
            messagebox.showinfo("Success", f"Hack '{hack_data['title']}' added successfully with ID {user_id}")
            self.refresh_callback()  # Refresh the table
            self.dialog.destroy()
        else:
            messagebox.showerror("Error", "Failed to add hack")
    
    def _get_next_user_id(self):
        """Get the next available user ID"""
        existing_user_ids = []
        for hack_id in self.data_manager.data.keys():
            if hack_id.startswith("usr_"):
                try:
                    num = int(hack_id[4:])  # Remove "usr_" prefix
                    existing_user_ids.append(num)
                except ValueError:
                    continue
        
        # Find next available ID
        next_id = 0
        while next_id in existing_user_ids:
            next_id += 1
            
        return f"usr_{next_id}"
