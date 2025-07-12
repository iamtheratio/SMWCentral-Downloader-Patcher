import tkinter as tk
from tkinter import ttk

class TableFilters:
    """Manages table filtering logic"""
    
    def __init__(self, apply_callback):
        self.apply_callback = apply_callback
        
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
                  command=self.clear_filters).pack(side="left")
                  
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