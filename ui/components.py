import tkinter as tk
from tkinter import ttk, filedialog
from colors import get_colors

class SetupSection:
    """Setup section with path controls"""
    
    def __init__(self, parent, config_manager):
        self.parent = parent
        self.config = config_manager
        self.frame = None
        
        # Path variables
        self.base_rom_path_var = tk.StringVar(value=self.config.get("base_rom_path", ""))
        self.output_dir_var = tk.StringVar(value=self.config.get("output_dir", ""))
        
        # API delay slider variable
        self.api_delay_var = tk.DoubleVar(value=self.config.get("api_delay", 0.8))
        self.delay_label_var = tk.StringVar(value=f"{self.api_delay_var.get():.1f}s")
    
    def create(self, font):
        """Create the setup section"""
        self.frame = ttk.LabelFrame(self.parent, text="Setup", padding=15)
        
        # Base ROM section
        ttk.Label(self.frame, text="Base ROM: *", font=font).grid(row=0, column=0, sticky="w", pady=(0, 5))
        ttk.Button(
            self.frame, text="Browse", command=self._browse_rom,
            style="Custom.TButton"
        ).grid(row=0, column=1, sticky="e", padx=(10, 0), pady=(0, 5))
        self.rom_label = ttk.Label(
            self.frame, textvariable=self.base_rom_path_var,
            foreground="gray", font=font
        )
        self.rom_label.grid(row=1, column=0, columnspan=2, sticky="ew", padx=5, pady=(0, 20))

        # Output Folder section
        ttk.Label(self.frame, text="Output Folder: *", font=font).grid(row=2, column=0, sticky="w", pady=(0, 5))
        ttk.Button(
            self.frame, text="Browse", command=self._select_output_dir,
            style="Custom.TButton"
        ).grid(row=2, column=1, sticky="e", padx=(10, 0), pady=(0, 5))
        self.output_label = ttk.Label(
            self.frame, textvariable=self.output_dir_var,
            foreground="gray", font=font
        )
        self.output_label.grid(row=3, column=0, columnspan=2, sticky="ew", padx=5, pady=(0, 20))
        
        # API Delay Slider section
        ttk.Label(self.frame, text="API Request Delay:", font=font).grid(row=4, column=0, sticky="w", pady=(0, 10))
        colors = get_colors()
        self.delay_display = ttk.Label(
            self.frame, textvariable=self.delay_label_var,
            font=font, foreground=colors["api_delay"]
        )
        self.delay_display.grid(row=4, column=1, sticky="e", padx=(10, 0), pady=(0, 5))
        
        # Slider frame
        slider_frame = ttk.Frame(self.frame)
        slider_frame.grid(row=5, column=0, columnspan=2, sticky="ew", padx=5, pady=(0, 10))
        
        # Slider with labels
        ttk.Label(slider_frame, text="0s", font=(font[0], font[1]-1)).pack(side="left")
        
        self.delay_slider = ttk.Scale(
            slider_frame,
            from_=0.0,
            to=3.0,
            orient="horizontal",
            variable=self.api_delay_var,
            command=self._on_delay_changed
        )
        self.delay_slider.pack(side="left", fill="x", expand=True, padx=(5, 5))
        
        ttk.Label(slider_frame, text="3s", font=(font[0], font[1]-1)).pack(side="right")
        
        # Slider description
        colors = get_colors()
        ttk.Label(
            self.frame,
            text="Higher values = slower but more reliable downloads",
            font=(font[0], font[1]-1),
            foreground=colors["description"]
        ).grid(row=6, column=0, columnspan=2, sticky="ew", padx=5, pady=(0, 5))
        
        # Configure column weights
        self.frame.columnconfigure(0, weight=1)
        
        return self.frame
    
    def _browse_rom(self):
        path = filedialog.askopenfilename(
            title="Select Base ROM",
            filetypes=[("ROM files", "*.smc *.sfc"), ("All files", "*.*")]
        )
        if path:
            self.base_rom_path_var.set(path)
            self.config.set("base_rom_path", path)
    
    def _select_output_dir(self):
        path = filedialog.askdirectory(title="Select Output Directory")
        if path:
            self.output_dir_var.set(path)
            self.config.set("output_dir", path)
    
    def _on_delay_changed(self, value):
        delay_val = float(value)
        self.delay_label_var.set(f"{delay_val:.1f}s")
        self.config.set("api_delay", delay_val)
    
    def get_paths(self):
        return {
            "base_rom_path": self.base_rom_path_var.get(),
            "output_dir": self.output_dir_var.get()
        }
    
    def get_api_delay(self):
        return self.api_delay_var.get()


class FilterSection:
    """Filter section for hack type and options"""
    
    def __init__(self, parent):
        self.parent = parent
        self.frame = None
        
        # Variables
        self.type_var = tk.StringVar(value="Standard")
        self.demo_var = tk.StringVar(value="Either")
        self.hof_var = tk.StringVar(value="Either")
        self.sa1_var = tk.StringVar(value="Either")
        self.collab_var = tk.StringVar(value="Either")
        self.waiting_var = tk.BooleanVar(value=False)
    
    def create(self, font, hack_types):
        """Create the filter section"""
        self.frame = ttk.LabelFrame(self.parent, text="Filters", padding=15)
        
        # Hack Type section - RESTORED TO DROPDOWN
        ttk.Label(self.frame, text="Hack Type:", font=font).grid(row=0, column=0, sticky="w", pady=(0, 10))
        
        self.type_combo = ttk.Combobox(
            self.frame,
            textvariable=self.type_var,
            values=hack_types,
            state="readonly",
            font=font,
            style="Custom.TCombobox"
        )
        self.type_combo.grid(row=0, column=1, sticky="ew", padx=(10, 0), pady=(0, 10))
        
        # Filter options
        self._add_radio_row("Demo:", self.demo_var, 1, font)
        self._add_radio_row("Hall of Fame:", self.hof_var, 2, font)
        self._add_radio_row("SA-1:", self.sa1_var, 3, font)
        self._add_radio_row("Collab:", self.collab_var, 4, font)
        
        # Include Waiting checkbox
        ttk.Checkbutton(
            self.frame,
            text="Include Waiting",
            variable=self.waiting_var,
            style="Custom.TCheckbutton"
        ).grid(row=5, column=0, columnspan=2, sticky="w", pady=(10, 0))
        
        # Configure column weights
        self.frame.columnconfigure(1, weight=1)
        
        return self.frame
    
    def _add_radio_row(self, label, var, row, font):
        ttk.Label(self.frame, text=label, font=font).grid(row=row, column=0, sticky="w", pady=2)
        
        radio_frame = ttk.Frame(self.frame)
        radio_frame.grid(row=row, column=1, sticky="w", padx=(10, 0), pady=2)
        
        for i, option in enumerate(["Either", "Yes", "No"]):
            ttk.Radiobutton(
                radio_frame, text=option, variable=var, value=option,
                style="Custom.TRadiobutton"
            ).pack(side="left", padx=(0, 15))
    
    def get_filter_values(self):
        return {
            "type": self.type_var.get(),
            "demo": self.demo_var.get(),
            "hof": self.hof_var.get(),
            "sa1": self.sa1_var.get(),
            "collab": self.collab_var.get(),
            "waiting": self.waiting_var.get()
        }


class DifficultySection:
    """Difficulty selection section"""
    
    def __init__(self, parent, difficulty_list):
        self.parent = parent
        self.frame = None
        self.difficulty_list = difficulty_list
        self.difficulty_vars = {}
        self.select_all_var = tk.BooleanVar()
        
        # Initialize difficulty variables
        for diff in difficulty_list:
            self.difficulty_vars[diff] = tk.BooleanVar()
    
    def create(self, font):
        """Create the difficulty section - SINGLE ROW FORMAT"""
        self.frame = ttk.LabelFrame(self.parent, text="Difficulty Selection", padding=15)
        
        # Difficulty checkboxes in single horizontal row
        diff_frame = ttk.Frame(self.frame)
        diff_frame.pack(fill="x", pady=(0, 10))
        
        for i, difficulty in enumerate(self.difficulty_list):
            display_name = difficulty.replace("_", " ").title()
            if difficulty == "no difficulty":
                display_name = "No Difficulty"
            
            ttk.Checkbutton(
                diff_frame,
                text=display_name,
                variable=self.difficulty_vars[difficulty],
                style="Custom.TCheckbutton"
            ).pack(side="left", padx=(0, 15))
        
        # Select All button underneath
        ttk.Button(
            self.frame,
            text="Select All",
            command=self._toggle_difficulties,
            style="Custom.TButton"
        ).pack(anchor="w")
        
        return self.frame
    
    def _toggle_difficulties(self):
        """Toggle all difficulties on or off"""
        # Check current state - if any are checked, uncheck all; otherwise check all
        any_checked = any(var.get() for var in self.difficulty_vars.values())
        new_state = not any_checked
        
        for var in self.difficulty_vars.values():
            var.set(new_state)
    
    def get_selected_difficulties(self):
        """Get list of selected difficulties"""
        selected = []
        for diff, var in self.difficulty_vars.items():
            if var.get():
                selected.append(diff)
        return selected