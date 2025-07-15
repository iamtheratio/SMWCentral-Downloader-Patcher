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
        
        # Multi-Type Download Options Section
        multi_type_frame = ttk.LabelFrame(self.frame, text="Multi-Type Download Options", padding=get_section_padding())
        multi_type_frame.pack(fill="x", pady=(20, 5))
        
        # Multi-type enabled checkbox
        self.multi_type_enabled_var = tk.BooleanVar()
        self.multi_type_enabled_checkbox = ttk.Checkbutton(
            multi_type_frame,
            text="Enable multi-type downloads (for hacks with multiple types like 'Kaizo, Tool-Assisted')",
            variable=self.multi_type_enabled_var,
            font=self.font
        )
        self.multi_type_enabled_checkbox.pack(anchor="w", pady=(0, 10))
        
        # Download mode selection
        mode_frame = ttk.Frame(multi_type_frame)
        mode_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Label(mode_frame, text="Download Mode:", font=self.font).pack(anchor="w")
        
        self.download_mode_var = tk.StringVar()
        mode_options = [
            ("primary_only", "Primary type only (saves to first type folder only)"),
            ("copy_all", "Copy to all type folders (creates multiple copies)"),
            ("symlink_all", "Symlink to all type folders (saves space, requires admin rights)")
        ]
        
        for value, description in mode_options:
            ttk.Radiobutton(
                mode_frame,
                text=description,
                variable=self.download_mode_var,
                value=value,
                font=self.font
            ).pack(anchor="w", padx=(20, 0), pady=2)
        
        # Duplicate method (only shown when copy_all is selected)
        self.duplicate_frame = ttk.Frame(multi_type_frame)
        self.duplicate_frame.pack(fill="x", pady=(0, 5))
        
        ttk.Label(self.duplicate_frame, text="File Management:", font=self.font).pack(anchor="w")
        
        self.duplicate_method_var = tk.StringVar()
        duplicate_options = [
            ("copy", "Create separate copies (uses more disk space)"),
            ("hardlink", "Create hard links (saves space, same file)")
        ]
        
        for value, description in duplicate_options:
            ttk.Radiobutton(
                self.duplicate_frame,
                text=description,
                variable=self.duplicate_method_var,
                value=value,
                font=self.font
            ).pack(anchor="w", padx=(20, 0), pady=2)
        
        # Bind mode change to show/hide duplicate options
        self.download_mode_var.trace("w", self._on_download_mode_changed)
        
        # Load current settings
        self._load_multi_type_settings()
        
        # Bind changes to save settings
        self.multi_type_enabled_var.trace("w", self._save_multi_type_settings)
        self.download_mode_var.trace("w", self._save_multi_type_settings)
        self.duplicate_method_var.trace("w", self._save_multi_type_settings)
        
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
    
    def _on_download_mode_changed(self, *args):
        """Show/hide duplicate method options based on download mode"""
        mode = self.download_mode_var.get()
        if mode == "copy_all":
            # Show duplicate method options
            for widget in self.duplicate_frame.winfo_children():
                widget.pack_configure()
        else:
            # Hide duplicate method options
            for widget in self.duplicate_frame.winfo_children():
                if isinstance(widget, ttk.Radiobutton):
                    widget.pack_forget()
    
    def _load_multi_type_settings(self):
        """Load multi-type settings from config"""
        try:
            from config_manager import ConfigManager
            config = ConfigManager()
            
            # Load settings with defaults
            enabled = config.get("multi_type_enabled", True)
            mode = config.get("multi_type_download_mode", "primary_only")
            method = config.get("multi_type_duplicate_method", "copy")
            
            self.multi_type_enabled_var.set(enabled)
            self.download_mode_var.set(mode)
            self.duplicate_method_var.set(method)
            
            # Update UI visibility
            self._on_download_mode_changed()
            
        except Exception as e:
            print(f"Error loading multi-type settings: {e}")
            # Set defaults
            self.multi_type_enabled_var.set(True)
            self.download_mode_var.set("primary_only")
            self.duplicate_method_var.set("copy")
    
    def _save_multi_type_settings(self, *args):
        """Save multi-type settings to config"""
        try:
            from config_manager import ConfigManager
            config = ConfigManager()
            
            enabled = self.multi_type_enabled_var.get()
            mode = self.download_mode_var.get()
            method = self.duplicate_method_var.get()
            
            config.set("multi_type_enabled", enabled)
            config.set("multi_type_download_mode", mode)  
            config.set("multi_type_duplicate_method", method)
            
        except Exception as e:
            print(f"Error saving multi-type settings: {e}")
