import tkinter as tk
from tkinter import ttk, messagebox
import threading
import sys
import os

# Add path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from utils import TYPE_KEYMAP
from ui_constants import get_page_padding, get_section_padding

class SettingsPage:
    """Settings page implementation"""
    
    def __init__(self, parent, run_pipeline_func, setup_section, filter_section, 
                 difficulty_section, logger):
        self.parent = parent
        self.setup_section = setup_section
        self.logger = logger
        self.font = ("Segoe UI", 9)
        self.frame = None
        self.log_level_combo = None
    
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
        """Create the settings page"""
        self.frame = ttk.Frame(self.parent, padding=get_page_padding())
        
        # Configure styles
        style = ttk.Style()
        for widget in ("TCheckbutton", "TRadiobutton", "TButton", "TCombobox"):
            style.configure(f"Custom.{widget}", font=self.font)

        # Setup section - now takes full width
        _, section_padding_y = get_section_padding()
        self.setup_section.parent = self.frame
        setup_frame = self.setup_section.create(self.font)
        setup_frame.pack(fill="x", pady=section_padding_y)
        
        # Log section with level dropdown and clear button - positioned below Setup
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
        
        # Log text area - now takes remaining space to bottom of app
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
