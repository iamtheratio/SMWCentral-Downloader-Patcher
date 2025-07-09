import tkinter as tk
from tkinter import ttk, filedialog

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
        self.delay_display = ttk.Label(
            self.frame, textvariable=self.delay_label_var,
            font=font, foreground="#0078d4"
        )
        self.delay_display.grid(row=4, column=1, sticky="e", padx=(10, 0), pady=(0, 5))
        
        # Slider frame
        slider_frame = ttk.Frame(self.frame)
        slider_frame.grid(row=5, column=0, columnspan=2, sticky="ew", padx=5, pady=(0, 10))  # Changed from 5 to 10
        
        # Slider with labels
        ttk.Label(slider_frame, text="0s", font=(font[0], font[1]-1)).pack(side="left")
        
        self.delay_slider = ttk.Scale(
            slider_frame,
            from_=0.0,
            to=3.0,  # Changed from 5.0 to 3.0
            orient="horizontal",
            variable=self.api_delay_var,
            command=self._on_delay_changed
        )
        self.delay_slider.pack(side="left", fill="x", expand=True, padx=(5, 5))
        
        ttk.Label(slider_frame, text="3s", font=(font[0], font[1]-1)).pack(side="right")  # Changed from "5s" to "3s"
        
        # Slider description
        ttk.Label(
            self.frame, 
            text="Controls delay between API requests. Increase if experiencing rate limiting errors.",
            font=(font[0], font[1]-1, "italic"),
            foreground="#888888"
        ).grid(row=6, column=0, columnspan=2, sticky="w", padx=5, pady=(0, 20))
        
        # Required fields note
        ttk.Label(
            self.frame, 
            text="* All fields are required", 
            font=(font[0], font[1]-1, "italic"),
            foreground="#888888"
        ).grid(row=7, column=0, columnspan=2, sticky="w", padx=5, pady=(0, 0))

        # Configure column weights
        self.frame.columnconfigure(0, weight=1)
        self.frame.columnconfigure(1, weight=0)
        
        return self.frame
    
    def _browse_rom(self):
        filename = filedialog.askopenfilename(
            title="Select Base ROM",
            filetypes=[
                ("Super Nintendo ROMs", "*.smc *.sfc"),
                ("All files", "*.*")
            ]
        )
        if filename:
            self.base_rom_path_var.set(filename)
            self.config.set("base_rom_path", filename)
    
    def _select_output_dir(self):
        path = filedialog.askdirectory()
        if path:
            self.output_dir_var.set(path)
            self.config.set("output_dir", path)
    
    def _on_delay_changed(self, value):
        """Handle delay slider changes"""
        delay_value = float(value)
        self.api_delay_var.set(delay_value)
        self.delay_label_var.set(f"{delay_value:.1f}s")
        
        # Save to config
        self.config.set("api_delay", delay_value)
    
    def get_paths(self):
        """Return current path values"""
        return {
            "base_rom_path": self.base_rom_path_var.get(),
            "output_dir": self.output_dir_var.get()
        }
    
    def get_api_delay(self):
        """Return current API delay value"""
        return self.api_delay_var.get()


class FilterSection:
    """Filter section for hack type and options"""
    
    def __init__(self, parent):
        self.parent = parent
        self.frame = None
        self.type_var = tk.StringVar(value="Kaizo")
        self.hof_var = tk.StringVar(value="Any")
        self.sa1_var = tk.StringVar(value="Any")
        self.collab_var = tk.StringVar(value="Any")
        self.demo_var = tk.StringVar(value="Any")
    
    def create(self, font, hack_types):
        """Create the filter section"""
        self.frame = ttk.LabelFrame(self.parent, text="Hack Filters", padding=15)
        
        # Hack type dropdown
        ttk.Label(self.frame, text="Hack Type:", font=font).grid(row=0, column=0, sticky="w", pady=(0,8))
        ttk.Combobox(
            self.frame, textvariable=self.type_var, values=hack_types,
            state="readonly", style="Custom.TCombobox"
        ).grid(row=0, column=1, columnspan=3, sticky="ew", pady=(7,15))  # Just add 3px top padding

        # Radio button rows
        self._add_radio_row("Hall of Fame", self.hof_var, 1, font)
        self._add_radio_row("SA-1", self.sa1_var, 2, font)
        self._add_radio_row("Collab", self.collab_var, 3, font)
        self._add_radio_row("Demo", self.demo_var, 4, font)
        
        return self.frame
    
    def _add_radio_row(self, label, var, row, font):
        """Helper to create a radio button row"""
        ttk.Label(self.frame, text=f"{label}:", font=font)\
            .grid(row=row, column=0, sticky="w", pady=8)
        for i, val in enumerate(["Any", "Yes", "No"]):
            ttk.Radiobutton(
                self.frame, text=val, variable=var, value=val,
                style="Custom.TRadiobutton"
            ).grid(row=row, column=i+1, padx=8, pady=8, sticky="w")
    
    def get_filter_values(self):
        """Return current filter values"""
        return {
            "type": self.type_var.get(),
            "hof": self.hof_var.get(),
            "sa1": self.sa1_var.get(),
            "collab": self.collab_var.get(),
            "demo": self.demo_var.get()
        }


class DifficultySection:
    """Difficulty selection section"""
    
    def __init__(self, parent, difficulty_list):
        self.parent = parent
        self.frame = None
        self.difficulty_list = difficulty_list
        self.difficulty_vars = {d: tk.BooleanVar() for d in difficulty_list}
        self.toggle_all_state = tk.BooleanVar(value=False)
        self.toggle_button = None
    
    def create(self, font):
        """Create the difficulty selection section"""
        self.frame = ttk.LabelFrame(self.parent, text="Difficulty Selection", padding=15)
        
        # Checkboxes for each difficulty in a horizontal layout
        for i, d in enumerate(self.difficulty_list):
            ttk.Checkbutton(
                self.frame, text=d.title(), variable=self.difficulty_vars[d],
                style="Custom.TCheckbutton"
            ).grid(row=0, column=i, padx=10)
        
        # Toggle button
        self.toggle_button = ttk.Button(
            self.frame, text="Select All", command=self._toggle_difficulties,
            style="Custom.TButton"
        )
        self.toggle_button.grid(row=1, column=0, pady=10, sticky="w")
        
        return self.frame
    
    def _toggle_difficulties(self):
        """Toggle all difficulty checkboxes"""
        new_state = not self.toggle_all_state.get()
        for var in self.difficulty_vars.values():
            var.set(new_state)
        self.toggle_all_state.set(new_state)
        self.toggle_button.config(text="Deselect All" if new_state else "Select All")
    
    def get_selected_difficulties(self):
        """Return list of selected difficulties"""
        return [d for d in self.difficulty_list if self.difficulty_vars[d].get()]