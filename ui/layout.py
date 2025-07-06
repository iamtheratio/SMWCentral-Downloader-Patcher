import tkinter as tk
from tkinter import ttk, messagebox
import threading
from utils import TYPE_KEYMAP
import sv_ttk

class MainLayout:
    """Main UI layout manager"""
    
    def __init__(self, root, run_pipeline_func, toggle_theme_callback, 
                 setup_section, filter_section, difficulty_section, logger):
        self.root = root
        self.run_pipeline_func = run_pipeline_func
        self.toggle_theme_callback = toggle_theme_callback
        self.setup_section = setup_section
        self.filter_section = filter_section
        self.difficulty_section = difficulty_section
        self.logger = logger
        self.download_button = None
        self.font = ("Segoe UI", 9)
    
    def create(self):
        """Create the main UI layout"""
        # Create theme toggle frame for top right
        self._create_theme_toggle()
        
        # Main frame
        main_frame = ttk.Frame(self.root, padding=25)
        main_frame.pack(fill="both", expand=True)

        # Title
        ttk.Label(
            main_frame,
            text="SMWCentral Downloader & Patcher",
            font=("Segoe UI", 20, "bold")
        ).pack(pady=(0, 20))

        # Configure styles
        style = ttk.Style()
        for widget in ("TCheckbutton", "TRadiobutton", "TButton", "TCombobox"):
            style.configure(f"Custom.{widget}", font=self.font)

        style.configure("Large.Accent.TButton", 
                      font=("Segoe UI", 10, "bold"),
                      padding=(20, 10))

        # Difficulty selection
        self.difficulty_section.parent = main_frame
        difficulty_frame = self.difficulty_section.create(self.font)
        difficulty_frame.pack(fill="x", pady=10)

        # Setup & filters section
        row_frame = ttk.Frame(main_frame)
        row_frame.pack(fill="both", expand=True, pady=10)

        # Configure grid for row_frame
        row_frame.rowconfigure(0, weight=1)
        for col in (0,1):
            row_frame.columnconfigure(col, weight=1)

        # Change the parent for these components to row_frame
        self.setup_section.parent = row_frame
        self.filter_section.parent = row_frame

        # Create the frames with the correct parent
        setup_frame = self.setup_section.create(self.font)
        setup_frame.grid(row=0, column=0, sticky="nsew", padx=(0,10))

        filter_frame = self.filter_section.create(self.font, ["Standard", "Kaizo", "Puzzle", "Tool-Assisted", "Pit"])
        filter_frame.grid(row=0, column=1, sticky="nsew", padx=(10,0))

        # Download & Patch button
        self.download_button = ttk.Button(
            main_frame, 
            text="Download & Patch", 
            command=self._run_pipeline_threaded,
            style="Large.Accent.TButton"
        )
        self.download_button.pack(pady=(10, 15))
        
        # Log level selector
        self._create_log_controls(main_frame)
        
        # Log text area
        log_text = self.logger.setup(main_frame)
        log_text.pack(fill="both", expand=True, pady=(2,0))
        
        # Store reference for theme toggling
        self.root.log_text = log_text
        
        return main_frame
    
    def _create_theme_toggle(self):
        """Create theme toggle switch"""
        theme_frame = ttk.Frame(self.root)
        theme_frame.pack(anchor="ne", padx=10, pady=5)
        
        # Add empty label for spacing
        ttk.Label(
            theme_frame, 
            text="", 
            width=1
        ).pack(side="left", padx=(0, 5))
        
        # Add theme switch
        theme_switch = ttk.Checkbutton(
            theme_frame,
            style="Switch.TCheckbutton",
            command=lambda: self.toggle_theme_callback(self.root)
        )
        theme_switch.pack(side="left")
        theme_switch.state(['selected'])  # Start checked for dark mode
        
        # Add moon icon
        ttk.Label(
            theme_frame, 
            text="🌙",
            font=("Segoe UI Emoji", 12),
        ).pack(side="left", padx=(2, 5))
    
    def _create_log_controls(self, parent):
        """Create log level controls"""
        log_frame = ttk.Frame(parent)
        log_frame.pack(fill="x", pady=(5,0))
        right = ttk.Frame(log_frame)
        right.pack(side="right")
        ttk.Label(right, text="Log Level:", font=self.font).pack(side="left", padx=(0,6))
        
        log_level_var = tk.StringVar(value="Information")
        
        def on_log_level_changed(*args):
            try:
                self.logger.set_log_level(log_level_var.get())
            except Exception as e:
                print(f"Error changing log level: {e}")
        
        log_level_var.trace_add("write", on_log_level_changed)
        
        log_level_combo = ttk.Combobox(
            right, textvariable=log_level_var, 
            values=["Information", "Debug", "Verbose"],
            width=12, state="readonly"
        )
        log_level_combo.pack(side="right")
        log_level_combo.current(0)
    
    def _generate_filter_payload(self):
        """Build API filter payload from UI selections"""
        filter_values = self.filter_section.get_filter_values()
        selected_type_label = filter_values["type"]
        selected_type = TYPE_KEYMAP.get(selected_type_label, "standard")
        selected_difficulties = self.difficulty_section.get_selected_difficulties()

        payload = {
            "type": [selected_type],
            "difficulties": selected_difficulties
        }

        # Convert Yes/No to API flag
        for key, var_value in [
            ("demo", filter_values["demo"]), 
            ("hof", filter_values["hof"]),
            ("sa1", filter_values["sa1"]), 
            ("collab", filter_values["collab"])
        ]:
            flag = {"Yes": "1", "No": "0"}.get(var_value)
            if flag:
                payload[key] = [flag]

        return payload
    
    def _run_pipeline_threaded(self):
        """Run the pipeline in a separate thread"""
        # Get filter payload
        payload = self._generate_filter_payload()
        
        # Check if no difficulties selected
        if not payload.get("difficulties") and payload.get("type")[0] != "all":
            if not messagebox.askyesno(
                "No Difficulties Selected", 
                "No difficulty filters selected. This will download ALL difficulties for the selected hack type. Continue?",
                icon="warning"
            ):
                return  # User canceled
        
        # Disable button and show running state
        self.download_button.configure(state="disabled", text="Running...")
        
        def pipeline_worker():
            try:
                paths = self.setup_section.get_paths()
                self.run_pipeline_func(
                    filter_payload=payload,
                    flips_path=paths["flips_path"],
                    base_rom_path=paths["base_rom_path"],
                    output_dir=paths["output_dir"],
                    log=self.logger.log
                )
                self.logger.log("✅ Done!", level="Information")
            except Exception as e:
                self.logger.log(f"❌ Error: {e}", level="Error")
            finally:
                # Re-enable button when done
                self.root.after(0, lambda: self.download_button.configure(
                    state="normal", 
                    text="Download & Patch"
                ))
        
        # Start pipeline in separate thread
        thread = threading.Thread(target=pipeline_worker, daemon=True)
        thread.start()