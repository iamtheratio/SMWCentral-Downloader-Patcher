import tkinter as tk
from tkinter import ttk, messagebox
import threading
from utils import TYPE_KEYMAP
import sv_ttk
from colors import get_colors

class MainLayout:
    """Main UI layout manager"""
    
    # Add this class variable for underline spacing
    UNDERLINE_SPACING = 20
    
    def __init__(self, root, run_pipeline_func, toggle_theme_callback, 
                 setup_section, filter_section, difficulty_section, logger, version=None):
        self.root = root
        self.run_pipeline_func = run_pipeline_func
        self.toggle_theme_callback = toggle_theme_callback
        self.setup_section = setup_section
        self.filter_section = filter_section
        self.difficulty_section = difficulty_section
        self.logger = logger
        self.version = version
        self.download_button = None
        self.font = ("Segoe UI", 9)
        
        # Page management
        self.current_page = "Bulk Download"
        self.pages = {}
        self.nav_bar = None
        self.content_frame = None
    
    def _create_navigation_bar(self):
        """Create navigation bar with tabs"""
        # Create spacer to push navigation down - increase height to 80px
        spacer = ttk.Frame(self.root, height=60)
        spacer.pack(side="top", fill="x")
        
        # Create navigation bar using a Canvas for complete background control
        accent_color = "#66c2ff"  # Light blue color for navigation bar
        
        nav_height = 60  # Increase from 40 to 50 pixels
        
        # Create a canvas for the navigation bar with blue background
        self.nav_bar = tk.Canvas(
            self.root,
            height=nav_height,
            bg=accent_color,  # Use blue background
            highlightthickness=0,  # No border
        )
        self.nav_bar.pack(fill="x", side="top", pady=0)
        
        # Add tab buttons as text directly on the canvas
        tabs = ["Bulk Download", "Hack History"]
        tab_width = 130
        
        # Store references for click handling
        self.tab_refs = []
        
        for i, tab in enumerate(tabs):
            x_pos = 10 + (i * tab_width)
            
            # Create text item on canvas
            tab_id = self.nav_bar.create_text(
                x_pos + 10,  # Add padding
                nav_height // 2 - 3,  # Subtract 3px to move text up
                text=tab,
                font=("Segoe UI", 11, "bold" if tab == self.current_page else "normal"),
                fill="black",
                anchor="w"
            )
            
            # Get text dimensions to center underline
            text_bbox = self.nav_bar.bbox(tab_id)
            text_width = text_bbox[2] - text_bbox[0]
            text_left = text_bbox[0]
            
            # Create underline rectangle (only for active tab)
            # Center the line under the text with a margin above the bottom
            if tab == self.current_page:
                # Ensure we always create an underline for the current page
                underline_id = self.nav_bar.create_line(
                    text_left, nav_height - self.UNDERLINE_SPACING,  # Use the class variable
                    text_left + text_width, nav_height - self.UNDERLINE_SPACING,  # Use the class variable
                    width=3,
                    fill="black"
                )
            else:
                underline_id = None
            
            # Store references for later - store text bbox info for underline positioning
            self.tab_refs.append({
                "name": tab,
                "text_id": tab_id,
                "underline_id": underline_id,
                "x": x_pos,
                "width": tab_width,
                "text_left": text_left,
                "text_width": text_width
            })
            
            # Calculate bbox for click detection
            x1 = x_pos
            y1 = 0
            x2 = x_pos + tab_width
            y2 = nav_height
            
            # Bind canvas area click to show page
            self.nav_bar.tag_bind(tab_id, "<Button-1>", lambda e, t=tab: self.show_page(t))
            
            # Make cursor change on hover by binding to canvas area
            self.nav_bar.tag_bind(tab_id, "<Enter>", lambda e: self.nav_bar.config(cursor="hand2"))
            self.nav_bar.tag_bind(tab_id, "<Leave>", lambda e: self.nav_bar.config(cursor=""))

    def show_page(self, page_name):
        """Switch between pages"""
        # Update the current page
        self.current_page = page_name
        
        # Hide all pages first
        for name, frame in self.pages.items():
            frame.pack_forget()
        
        # Show the selected page
        if page_name in self.pages:
            self.pages[page_name].pack(fill="both", expand=True)
        
        # Update tabs on the canvas
        for tab_ref in self.tab_refs:
            # Update text style (bold for active)
            self.nav_bar.itemconfig(
                tab_ref["text_id"],
                font=("Segoe UI", 11, "bold" if tab_ref["name"] == page_name else "normal")
            )
            
            # Handle underline
            if tab_ref["name"] == page_name:
                # Get updated text dimensions after font change (bold makes text wider)
                text_bbox = self.nav_bar.bbox(tab_ref["text_id"])
                text_width = text_bbox[2] - text_bbox[0]
                text_left = text_bbox[0]
                
                # Create underline if not exists
                if not tab_ref["underline_id"]:
                    tab_ref["underline_id"] = self.nav_bar.create_line(
                        text_left, self.nav_bar.winfo_height() - self.UNDERLINE_SPACING,  # Use the class variable
                        text_left + text_width, self.nav_bar.winfo_height() - self.UNDERLINE_SPACING,  # Use the class variable
                        width=3,
                        fill="black"
                    )
                else:
                    # Update position if it exists
                    self.nav_bar.coords(
                        tab_ref["underline_id"],
                        text_left, self.nav_bar.winfo_height() - self.UNDERLINE_SPACING,  # Use the class variable
                        text_left + text_width, self.nav_bar.winfo_height() - self.UNDERLINE_SPACING  # Use the class variable
                    )
            else:
                # Remove underline if exists
                if tab_ref["underline_id"]:
                    self.nav_bar.delete(tab_ref["underline_id"])
                    tab_ref["underline_id"] = None

    def _create_bulk_download_page(self):
        """Create the bulk download page (existing UI)"""
        # Main frame for this page
        bulk_page = ttk.Frame(self.content_frame, padding=25)
        self.pages["Bulk Download"] = bulk_page
        
        # Configure styles
        style = ttk.Style()
        for widget in ("TCheckbutton", "TRadiobutton", "TButton", "TCombobox"):
            style.configure(f"Custom.{widget}", font=self.font)

        style.configure("Large.Accent.TButton", 
                      font=("Segoe UI", 10, "bold"),
                      padding=(20, 10))

        # Difficulty selection
        self.difficulty_section.parent = bulk_page
        difficulty_frame = self.difficulty_section.create(self.font)
        difficulty_frame.pack(fill="x", pady=10)

        # Setup & filters section
        row_frame = ttk.Frame(bulk_page)
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
            bulk_page, 
            text="Download & Patch", 
            command=self._run_pipeline_threaded,
            style="Large.Accent.TButton"
        )
        self.download_button.pack(pady=(10, 15))
        
        # Log section with level dropdown and clear button
        log_header_frame = ttk.Frame(bulk_page)
        log_header_frame.pack(fill="x", pady=(20, 5))
        
        # Log level dropdown (left side)
        ttk.Label(log_header_frame, text="Log Level:", font=self.font).pack(side="left")
        
        log_level_combo = ttk.Combobox(
            log_header_frame,
            values=["Debug", "Information", "Warning", "Error"],
            state="readonly",
            font=self.font,
            width=12
        )
        log_level_combo.set("Information")
        log_level_combo.pack(side="left", padx=(10, 0))
        
        # Clear button (right side)
        ttk.Button(
            log_header_frame,
            text="Clear",
            command=self.logger.clear_log
        ).pack(side="right")
        
        # Log text area (full width below)
        log_text = self.logger.setup(bulk_page)
        log_text.pack(fill="both", expand=True, pady=(2, 5))
        
        # Store reference for theme toggling
        self.root.log_text = log_text
    
    def _create_hack_history_page(self):
        """Create a blank page for hack history"""
        # Main frame for this page
        history_page = ttk.Frame(self.content_frame, padding=25)
        self.pages["Hack History"] = history_page
        
        # Add placeholder content
        ttk.Label(
            history_page,
            text="Hack History Page",
            font=("Segoe UI", 14)
        ).pack(pady=50)
        
        ttk.Label(
            history_page,
            text="This page will be implemented in a future update.",
            font=("Segoe UI", 10)
        ).pack()

    def _create_theme_toggle(self):
        """Create theme toggle switch"""
        # Position the theme toggle to be visible in the top-right corner
        theme_frame = ttk.Frame(self.root)
        theme_frame.place(relx=1.0, rely=0.0, anchor="ne", x=-10, y=10)
        
        # Add theme switch
        theme_switch = ttk.Checkbutton(
            theme_frame,
            style="Switch.TCheckbutton",
            command=lambda: self.toggle_theme_callback(self.root)
        )
        theme_switch.pack(side="left")
        theme_switch.state(['selected'] if sv_ttk.get_theme() == "dark" else [])
        
        # Add moon icon
        moon_label = ttk.Label(
            theme_frame, 
            text="🌙",
            font=("Segoe UI Emoji", 12),
        )
        moon_label.pack(side="left", padx=(2, 5))
        
        # Store references for later access
        self.root.theme_switch = theme_switch
        self.root.moon_label = moon_label
        
        # Make sure the theme toggle is on top of everything
        theme_frame.lift()

    def create(self):
        """Create the main UI layout"""
        # Create theme toggle frame for top right first
        self._create_theme_toggle()
        
        # Create navigation bar at the top (with 50px spacer)
        self._create_navigation_bar()
        
        # Content frame - will hold all pages
        self.content_frame = ttk.Frame(self.root)
        self.content_frame.pack(fill="both", expand=True)
        
        # Create pages
        self._create_bulk_download_page()
        self._create_hack_history_page()
        
        # Show default page (this will ensure underline is correctly displayed)
        self.show_page("Bulk Download")
        
        # Add version label in bottom right with 20px padding
        if self.version:
            version_label = ttk.Label(self.root, text=self.version, 
                                    font=("Segoe UI", 8, "italic"))
            # Use place geometry manager for absolute positioning - right aligned with padding
            version_label.place(relx=1.0, rely=1.0, anchor="se", x=-26, y=-10)
            
            # Set initial color based on theme
            colors = get_colors()
            version_label.configure(foreground=colors["version_label"])
            
            # Store reference for theme updates
            self.root.version_label = version_label
    
        # Make sure theme toggle remains on top
        self.root.update_idletasks()
        if hasattr(self.root, 'theme_switch'):
            self.root.theme_switch.master.lift()
    
        # Force a refresh of the navigation tabs to ensure underline is properly displayed
        self.root.after(100, lambda: self.show_page(self.current_page))
    
        return self.content_frame
    
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
            values=["Information", "Debug", "Verbose", "Error"],
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
            "difficulties": selected_difficulties,
            "waiting": filter_values["waiting"]  # Add waiting parameter
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
        
        # Check if any paths are empty - REMOVED flips_path check
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
        
        # ADDED: Check if no difficulties selected
        if not payload.get("difficulties"):
            messagebox.showerror(
                "Selection Required", 
                "Please select at least one difficulty level to continue."
            )
            return
        
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
                self.root.after(0, lambda: self.download_button.configure(
                    state="normal", 
                    text="Download & Patch"
                ))
        
        # Start pipeline in separate thread
        thread = threading.Thread(target=pipeline_worker, daemon=True)
        thread.start()