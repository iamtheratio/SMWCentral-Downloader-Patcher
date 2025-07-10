import tkinter as tk
from tkinter import ttk, messagebox
import threading
from utils import TYPE_KEYMAP

class BulkDownloadPage:
    """Bulk download page implementation"""
    
    def __init__(self, parent, run_pipeline_func, setup_section, filter_section, 
                 difficulty_section, logger):
        self.parent = parent
        self.run_pipeline_func = run_pipeline_func
        self.setup_section = setup_section
        self.filter_section = filter_section
        self.difficulty_section = difficulty_section
        self.logger = logger
        self.font = ("Segoe UI", 9)
        self.download_button = None
        self.frame = None
        self.log_level_combo = None
    
    def create(self):
        """Create the bulk download page"""
        self.frame = ttk.Frame(self.parent, padding=25)
        
        # Configure styles
        style = ttk.Style()
        for widget in ("TCheckbutton", "TRadiobutton", "TButton", "TCombobox"):
            style.configure(f"Custom.{widget}", font=self.font)

        style.configure("Large.Accent.TButton", 
                      font=("Segoe UI", 10, "bold"),
                      padding=(20, 10))

        # Difficulty selection
        self.difficulty_section.parent = self.frame
        difficulty_frame = self.difficulty_section.create(self.font)
        difficulty_frame.pack(fill="x", pady=10)

        # Setup & filters section
        row_frame = ttk.Frame(self.frame)
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
            self.frame, 
            text="Download & Patch", 
            command=self._run_pipeline_threaded,
            style="Large.Accent.TButton"
        )
        self.download_button.pack(pady=(10, 15))
        
        # Log section with level dropdown and clear button
        log_header_frame = ttk.Frame(self.frame)
        log_header_frame.pack(fill="x", pady=(20, 5))
        
        # Log level dropdown (left side)
        ttk.Label(log_header_frame, text="Log Level:", font=self.font).pack(side="left")
        
        self.log_level_combo = ttk.Combobox(
            log_header_frame,
            values=["Debug", "Information", "Warning", "Error"],
            state="readonly",
            font=self.font,
            width=12
        )
        self.log_level_combo.set("Information")
        self.log_level_combo.pack(side="left", padx=(10, 0))
        
        # Bind log level change
        self.log_level_combo.bind("<<ComboboxSelected>>", self._on_log_level_changed)
        
        # Clear button (right side)
        ttk.Button(
            log_header_frame,
            text="Clear",
            command=self.logger.clear_log
        ).pack(side="right")
        
        # Log text area (full width below)
        log_text = self.logger.setup(self.frame)
        log_text.pack(fill="both", expand=True, pady=(2, 5))
        
        # Store reference for theme toggling - CORRECTLY on root, not in config
        root = self.parent.winfo_toplevel()
        root.log_text = log_text
        
        return self.frame
    
    def _on_log_level_changed(self, event=None):
        """Handle log level change"""
        if self.log_level_combo:
            new_level = self.log_level_combo.get()
            self.logger.set_log_level(new_level)
    
    def _generate_filter_payload(self):
        """Build API filter payload from UI selections"""
        filter_values = self.filter_section.get_filter_values()
        selected_type_label = filter_values["type"]
        selected_type = TYPE_KEYMAP.get(selected_type_label, "standard")
        selected_difficulties = self.difficulty_section.get_selected_difficulties()

        payload = {
            "type": [selected_type],
            "difficulties": selected_difficulties,
            "waiting": filter_values["waiting"]
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
        # Validate required paths first
        paths = self.setup_section.get_paths()
        
        # Check if any paths are empty
        missing_paths = []
        if not paths["base_rom_path"]:
            missing_paths.append("Base ROM Path")
        if not paths["output_dir"]:
            missing_paths.append("Output Directory")
        
        # If any paths are missing, show error and return
        if missing_paths:
            bullet_list = "• " + "\n• ".join(missing_paths)
            messagebox.showerror(
                "Missing Required Paths",
                f"The following required paths are not set:\n\n{bullet_list}\n\nPlease set all required paths in the Setup section before continuing."
            )
            return
        
        # Get filter payload
        payload = self._generate_filter_payload()
        
        # Check if no difficulties selected
        if not payload.get("difficulties"):
            messagebox.showerror(
                "Selection Required", 
                "Please select at least one difficulty level to continue."
            )
            return
        
        # Disable button and show running state
        self.download_button.configure(state="disabled", text="Running...")
        
        def pipeline_worker():
            try:
                self.run_pipeline_func(
                    filter_payload=payload,
                    base_rom_path=paths["base_rom_path"],
                    output_dir=paths["output_dir"],
                    log=self.logger.log
                )
                self.logger.log("✅ Done!", level="Information")
            except Exception as e:
                self.logger.log(f"❌ Error: {e}", level="Error")
            finally:
                # Re-enable button when done
                root = self.parent.winfo_toplevel()
                if root:
                    root.after(0, lambda: self.download_button.configure(
                        state="normal", 
                        text="Download & Patch"
                    ))
        
        # Start pipeline in separate thread
        thread = threading.Thread(target=pipeline_worker, daemon=True)
        thread.start()
    
    def get_download_button(self):
        """Return the download button reference"""
        return self.download_button