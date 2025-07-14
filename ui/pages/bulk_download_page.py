import tkinter as tk
from tkinter import ttk, messagebox
import threading
import sys
import os

# Add path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from utils import TYPE_KEYMAP
from ui_constants import get_page_padding, get_section_padding

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
        
        # Cancellation support
        self.is_cancelled = False
        self.current_thread = None
    
    def update_theme_colors(self):
        """Update cancel button colors when theme changes"""
        # No longer needed - button keeps its original style
        pass

    def _configure_cancel_style(self):
        """Configure the complete cancel button style independent of theme changes"""
        try:
            from colors import get_colors
            colors = get_colors()
            
            # Create completely independent cancel button style
            style = ttk.Style()
            
            # First, clear any existing Cancel.TButton configuration
            try:
                style.configure("Cancel.TButton")  # Reset to defaults
            except:
                pass
            
            # Get the current TButton configuration to see what might be interfering
            try:
                button_config = style.configure("TButton")
                print(f"DEBUG: Current TButton config: {button_config}")
            except:
                pass
            
            # Force complete reconfiguration to override any interference
            # Configure Cancel.TButton to be completely independent of TButton
            style.configure("Cancel.TButton", 
                           font=("Segoe UI", 10, "bold"),  # Explicit font - larger than default
                           padding=(20, 10),               # Explicit padding
                           background=colors["cancel_bg"],
                           foreground=colors["cancel_fg"],
                           borderwidth=1,
                           relief="flat",
                           width=None,      # Let text determine width
                           height=None)     # Let font+padding determine height
            
            # Also configure the style mapping to prevent inheritance issues
            style.map("Cancel.TButton",
                     background=[('active', colors["cancel_hover"]),
                                ('pressed', colors["cancel_pressed"]),
                                ('disabled', colors["cancel_bg"]),
                                ('focus', colors["cancel_bg"]),
                                ('!focus', colors["cancel_bg"]),
                                ('selected', colors["cancel_bg"]),
                                ('!selected', colors["cancel_bg"]),
                                ('readonly', colors["cancel_bg"]),
                                ('alternate', colors["cancel_bg"]),
                                ('invalid', colors["cancel_bg"]),
                                ('', colors["cancel_bg"])],
                     foreground=[('active', colors["cancel_fg"]),
                                ('pressed', colors["cancel_fg"]),
                                ('disabled', colors["cancel_fg"]),
                                ('focus', colors["cancel_fg"]),
                                ('!focus', colors["cancel_fg"]),
                                ('selected', colors["cancel_fg"]),
                                ('!selected', colors["cancel_fg"]),
                                ('readonly', colors["cancel_fg"]),
                                ('alternate', colors["cancel_fg"]),
                                ('invalid', colors["cancel_fg"]),
                                ('', colors["cancel_fg"])],
                     # Override font in map as well to prevent inheritance
                     font=[('', ("Segoe UI", 10, "bold"))],
                     focuscolor=[('', ''), ('focus', ''), ('!focus', '')],
                     bordercolor=[('', colors["cancel_bg"]), ('focus', colors["cancel_bg"])],
                     lightcolor=[('', colors["cancel_bg"])],
                     darkcolor=[('', colors["cancel_bg"])])
            
            # Ensure the button is using our style and force refresh
            if self.download_button:
                self.download_button.configure(style="Cancel.TButton")
                # Force widget to recalculate its size
                self.download_button.update_idletasks()
                
                # DEBUG: Check what style the button is actually using
                actual_style = self.download_button.cget('style')
                print(f"DEBUG: Button is using style: {actual_style}")
                
        except Exception as e:
            print(f"Error configuring cancel button style: {e}")

    def create(self):
        """Create the bulk download page"""
        self.frame = ttk.Frame(self.parent, padding=get_page_padding())
        
        # Configure styles
        style = ttk.Style()
        for widget in ("TCheckbutton", "TRadiobutton", "TButton", "TCombobox"):
            style.configure(f"Custom.{widget}", font=self.font)

        style.configure("Large.Accent.TButton", 
                      font=("Segoe UI", 10, "bold"),
                      padding=(20, 10))

        # Difficulty selection
        _, section_padding_y = get_section_padding()
        self.difficulty_section.parent = self.frame
        difficulty_frame = self.difficulty_section.create(self.font)
        difficulty_frame.pack(fill="x", pady=0) #section_padding_y)

        # Setup & filters section
        row_frame = ttk.Frame(self.frame)
        row_frame.pack(fill="both", expand=True, pady=section_padding_y)

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
            command=self._on_button_click,
            style="Large.Accent.TButton"
        )
        self.download_button.pack(pady=(10, 15))
        
        # Log section with level dropdown and clear button
        log_header_frame = ttk.Frame(self.frame)
        log_header_frame.pack(fill="x", pady=(20, 5))
        
        # Log level dropdown (left side) - UPDATED ORDER AND REMOVED WARNING
        ttk.Label(log_header_frame, text="Log Level:", font=self.font).pack(side="left")
        
        self.log_level_combo = ttk.Combobox(
            log_header_frame,
            values=["Information", "Debug", "Error"],  # REORDERED AND REMOVED WARNING
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

        # Convert Yes/No to API flag, ignore "Any" - FIXED: Don't wrap in array
        for key, var_value in [
            ("demo", filter_values["demo"]), 
            ("hof", filter_values["hof"]),
            ("sa1", filter_values["sa1"]), 
            ("collab", filter_values["collab"])
        ]:
            # Only add filter if it's not "Any" (which means no filter)
            if var_value in ["Yes", "No"]:
                flag = {"Yes": "1", "No": "0"}[var_value]
                payload[key] = flag  # FIXED: Remove the array wrapping

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
        
        # Reset cancellation flag and set button to cancel mode
        self.is_cancelled = False
        
        # Simply change the text - keep the same blue style for consistency
        self.download_button.configure(text="Cancel")
        
        def pipeline_worker():
            try:
                # Call original pipeline
                self.run_pipeline_func(
                    filter_payload=payload,
                    base_rom_path=paths["base_rom_path"],
                    output_dir=paths["output_dir"],
                    log=self.logger.log
                )
                if not self.is_cancelled:
                    self.logger.log("✅ Done!", level="Information")
            except Exception as e:
                if not self.is_cancelled:
                    self.logger.log(f"❌ Error: {e}", level="Error")
            finally:
                # Re-enable button when done and restore original colors
                self.current_thread = None
                root = self.parent.winfo_toplevel()
                if root:
                    def restore_button():
                        # Restore original button text
                        self.download_button.configure(text="Download & Patch")
                    
                    root.after(0, restore_button)
        
        # Start pipeline in separate thread
        thread = threading.Thread(target=pipeline_worker, daemon=True)
        thread.start()
        self.current_thread = thread
    
    def _on_button_click(self):
        """Handle button click - either start download or cancel operation"""
        if self.current_thread and self.current_thread.is_alive():
            # Cancel operation
            self._cancel_operation()
        else:
            # Start operation
            self._run_pipeline_threaded()
    
    def _cancel_operation(self):
        """Cancel the current operation"""
        self.is_cancelled = True
        
        # Cancel the pipeline operation
        from api_pipeline import cancel_pipeline
        cancel_pipeline()
        
        self.logger.log("🛑 Cancelling operation...", level="warning")
        
        # Reset button immediately
        self.download_button.configure(text="Download & Patch")
        
        # Note: Cancellation confirmation message is logged by api_pipeline.py

    def get_download_button(self):
        """Return the download button reference"""
        return self.download_button

    def on_download_click(self):
        """Handle download button click"""
        
        # Get current filter settings
        current_filters = {
            "hack_type": self.hack_type_var.get(),
            "difficulty": self.difficulty_var.get(),
            "hall_of_fame": self.hall_of_fame_var.get(),
            "sa1": self.sa1_var.get(),
            "collaboration": self.collaboration_var.get(), 
            "demo": self.demo_var.get()
        }
        
        # Pass filters to the download pipeline
        self.run_pipeline_func(filters=current_filters)
    
    def _run_pipeline_with_cancellation(self, filter_payload, base_rom_path, output_dir, log=None):
        """Run pipeline with cancellation support"""
        # Import required modules
        from api_pipeline import fetch_hack_list, load_processed, save_processed
        from utils import DIFFICULTY_KEYMAP, title_case, safe_filename
        from patch_handler import extract_patches_from_zip, apply_patch
        import tempfile
        import shutil
        import requests
        import os
        
        processed = load_processed()
        all_hacks = []
        if log: log("🔎 Starting download...")

        # Check if we need to do post-collection filtering
        difficulties = filter_payload.get("difficulties", [])
        has_no_difficulty = "no difficulty" in difficulties
        regular_difficulties = [d for d in difficulties if d != "no difficulty"]
        needs_post_filtering = has_no_difficulty and not regular_difficulties
        
        # Add warning for "No Difficulty" selections
        if has_no_difficulty:
            if log:
                log("[WRN] 'No Difficulty' selected - downloading ALL hacks then filtering locally due to SMWC API limitations", level="warning")

        # PHASE 1: Fetch all moderated hacks (u=0)
        page = 1
        while True:
            if self.is_cancelled:
                return
                
            page_result = fetch_hack_list(filter_payload, page=page, waiting_mode=False, log=log)
            
            hacks = page_result["data"]
            last_page = page_result.get("last_page", page)
            
            if not hacks:
                if log: log("📄 No more moderated pages available", level="information")
                break
            
            all_hacks.extend(hacks)
            
            if log: 
                log(f"📄 Moderated page {page} returned {len(hacks)} entries", level="information")
            
            # Stop if we've reached the last page
            if page >= last_page:
                if log: log(f"📄 Reached last moderated page ({last_page})", level="information")
                break
            
            page += 1

        # PHASE 2: Fetch waiting hacks if enabled (u=1)
        if filter_payload.get("waiting", False):
            page = 1
            while True:
                if self.is_cancelled:
                    return
                    
                page_result = fetch_hack_list(filter_payload, page=page, waiting_mode=True, log=log)
                
                hacks = page_result["data"]
                last_page = page_result.get("last_page", page)
                
                if not hacks:
                    if log: log("📄 No more waiting pages available", level="information")
                    break
                
                all_hacks.extend(hacks)
                
                if log: 
                    log(f"📄 Waiting page {page} returned {len(hacks)} entries", level="information")
                
                if page >= last_page:
                    if log: log(f"📄 Reached last waiting page ({last_page})", level="information")
                    break
                
                page += 1

        if self.is_cancelled:
            return

        # Continue with the rest of the pipeline logic...
        # (This is a simplified version - you'd need to adapt the full pipeline with cancellation checks)
        
        if log:
            log(f"📦 Found {len(all_hacks)} total hacks.")
            log("🧪 Starting patching...")

        base_rom_ext = os.path.splitext(base_rom_path)[1]
        raw_type = filter_payload["type"][0]
        normalized_type = raw_type.lower().replace("-", "_")

        for i, hack in enumerate(all_hacks):
            if self.is_cancelled:
                return
                
            # Process each hack (simplified version)
            hack_id = str(hack["id"])
            raw_title = hack["name"]
            title_clean = title_case(safe_filename(raw_title))
            
            if log:
                log(f"Processing {i+1}/{len(all_hacks)}: {title_clean}")
            
            # Add cancellation checks during processing
            # This is where you'd call the original pipeline logic
            # but with periodic cancellation checks