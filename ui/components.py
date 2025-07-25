import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from colors import get_colors
import sys
import os

# Add path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from ui_constants import get_labelframe_padding

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
        self.frame = ttk.LabelFrame(self.parent, text="Setup", padding=get_labelframe_padding())
        
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
            text="Controls delay between API requests, increase if experiencing rate limits.",
            font=(font[0], font[1]-1, "italic"),
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
        # Round to nearest 0.1 increment
        delay_val = round(float(value), 1)
        self.delay_label_var.set(f"{delay_val:.1f}s")
        self.config.set("api_delay", delay_val)
        # Update the slider variable to match the rounded value
        self.api_delay_var.set(delay_val)
    
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
        
        # Variables - Changed defaults
        self.type_var = tk.StringVar(value="Kaizo")  # DEFAULT TO KAIZO
        self.demo_var = tk.StringVar(value="Any")    # CHANGED TO ANY
        self.hof_var = tk.StringVar(value="Any")     # CHANGED TO ANY
        self.sa1_var = tk.StringVar(value="Any")     # CHANGED TO ANY
        self.collab_var = tk.StringVar(value="Any")  # CHANGED TO ANY
        self.waiting_var = tk.BooleanVar(value=False)
    
    def create(self, font, hack_types):
        """Create the filter section"""
        self.frame = ttk.LabelFrame(self.parent, text="Filters", padding=get_labelframe_padding())
        
        # Hack Type section - DROPDOWN WITH KAIZO DEFAULT
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
        
        # Filter options - REORDERED AND CHANGED TO "Any"
        self._add_radio_row("Hall of Fame:", self.hof_var, 1, font)
        self._add_radio_row("SA-1:", self.sa1_var, 2, font)
        self._add_radio_row("Collab:", self.collab_var, 3, font)
        self._add_radio_row("Demo:", self.demo_var, 4, font)
        
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
        
        # CHANGED OPTIONS TO Any/Yes/No
        for i, option in enumerate(["Any", "Yes", "No"]):
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
        self.select_all_button = None  # Store reference to the button
        
        # Initialize difficulty variables
        for diff in difficulty_list:
            self.difficulty_vars[diff] = tk.BooleanVar()
    
    def create(self, font):
        """Create the difficulty section - SINGLE ROW FORMAT"""
        self.frame = ttk.LabelFrame(self.parent, text="Difficulty Selection", padding=get_labelframe_padding())
        
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
                command=self._update_button_text,  # Update button text when checkbox clicked
                style="Custom.TCheckbutton"
            ).pack(side="left", padx=(0, 15))
        
        # Select All button on the right side, aligned with the No Difficulty checkbox
        self.select_all_button = ttk.Button(
            diff_frame,
            text="Select All",
            command=self._toggle_difficulties,
            style="Custom.TButton"
        )
        self.select_all_button.pack(side="right", padx=(15, 0))
        
        return self.frame
    
    def _toggle_difficulties(self):
        """Toggle all difficulties on or off based on button text"""
        if self.select_all_button.cget("text") == "Select All":
            # Select all difficulties
            for var in self.difficulty_vars.values():
                var.set(True)
        else:
            # Deselect all difficulties
            for var in self.difficulty_vars.values():
                var.set(False)
        
        # Update button text
        self._update_button_text()
    
    def _update_button_text(self):
        """Update the Select All button text based on current state"""
        if self.select_all_button:
            any_checked = any(var.get() for var in self.difficulty_vars.values())
            
            if any_checked:
                self.select_all_button.configure(text="Deselect All")
            else:
                self.select_all_button.configure(text="Select All")
    
    def get_selected_difficulties(self):
        """Get list of selected difficulties"""
        selected = []
        for diff, var in self.difficulty_vars.items():
            if var.get():
                selected.append(diff)
        return selected
