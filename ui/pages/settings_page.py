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
        for widget in ("TCheckbutton", "TRadiobutton", "TButton", "TCombobox", "TLabel"):
            style.configure(f"Custom.{widget}", font=self.font)

        # Top row: Setup section on left, Multi-type options on right - EQUAL WIDTHS
        top_row_frame = ttk.Frame(self.frame)
        top_row_frame.pack(fill="x", pady=(0, 20))
        
        # Setup section (left side) - equal width, no extra wrapper
        setup_frame = ttk.Frame(top_row_frame)
        setup_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        self.setup_section.parent = setup_frame
        setup_content = self.setup_section.create(self.font)
        setup_content.pack(fill="both", expand=True)
        
        # Multi-Type Download Options Section (right side) - equal width
        multi_type_frame = ttk.LabelFrame(top_row_frame, text="Multi-Type Download Options", padding=(15, 10, 15, 15))
        multi_type_frame.pack(side="right", fill="both", expand=True, padx=(10, 0))
        
        # Multi-type enabled checkbox
        self.multi_type_enabled_var = tk.BooleanVar()
        self.multi_type_enabled_checkbox = ttk.Checkbutton(
            multi_type_frame,
            text="Enable multi-type downloads\n(for hacks with types like 'Kaizo, Tool-Assisted')",
            variable=self.multi_type_enabled_var,
            style="Custom.TCheckbutton"
        )
        self.multi_type_enabled_checkbox.pack(anchor="w", pady=(0, 12))
        
        # Download mode selection
        mode_frame = ttk.Frame(multi_type_frame)
        mode_frame.pack(fill="x", pady=(0, 12))
        
        ttk.Label(mode_frame, text="Download Mode:", style="Custom.TLabel").pack(anchor="w", pady=(0, 4))
        
        self.download_mode_var = tk.StringVar()
        mode_options = [
            ("primary_only", "Primary type only"),
            ("copy_all", "Copy to all type folders")
        ]
        
        for value, description in mode_options:
            ttk.Radiobutton(
                mode_frame,
                text=description,
                variable=self.download_mode_var,
                value=value,
                style="Custom.TRadiobutton"
            ).pack(anchor="w", padx=(15, 0), pady=2)
        
        # Load current settings FIRST
        self._load_multi_type_settings()
        
        # Bind changes to save settings (cross-version tkinter compatibility)
        try:
            # Python 3.6+
            self.multi_type_enabled_var.trace_add("write", self._save_multi_type_settings)
            self.download_mode_var.trace_add("write", self._save_multi_type_settings)
        except AttributeError:
            # Older Python versions
            self.multi_type_enabled_var.trace("w", self._save_multi_type_settings)
            self.download_mode_var.trace("w", self._save_multi_type_settings)
        
        # Update section
        update_frame = ttk.Frame(multi_type_frame)
        update_frame.pack(fill="x", pady=(12, 0))
        
        # Separator line
        separator = ttk.Separator(update_frame, orient="horizontal")
        separator.pack(fill="x", pady=(0, 12))
        
        # Update section label
        ttk.Label(update_frame, text="Application Updates:", style="Custom.TLabel", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(0, 8))
        
        # Check for updates button
        self.check_updates_button = ttk.Button(
            update_frame,
            text="Check for Updates",
            command=self._check_for_updates,
            style="Custom.TButton"
        )
        self.check_updates_button.pack(anchor="w", pady=(0, 4))
        
        # Auto-check updates setting
        self.auto_check_updates_var = tk.BooleanVar()
        self.auto_check_updates_checkbox = ttk.Checkbutton(
            update_frame,
            text="Check for updates automatically on startup",
            variable=self.auto_check_updates_var,
            style="Custom.TCheckbutton",
            command=self._save_auto_check_setting
        )
        self.auto_check_updates_checkbox.pack(anchor="w", pady=(4, 0))
        
        # Load auto-check setting
        self._load_auto_check_setting()

        # QUSB2SNES Sync Section - further reduced spacing from top sections
        qusb2snes_frame = ttk.Frame(self.frame)
        qusb2snes_frame.pack(fill="x", pady=(5, 20))
        
        try:
            from qusb2snes_ui import QUSB2SNESSection
            
            # Use the shared config from setup_section instead of creating a new one
            # This ensures all sections see the same data and saves don't overwrite
            shared_config = self.setup_section.config
            self.qusb2snes_section = QUSB2SNESSection(qusb2snes_frame, shared_config, self.logger)
            qusb2snes_content = self.qusb2snes_section.create(None)
            qusb2snes_content.pack(fill="x")
            
        except ImportError as e:
            # If QUSB2SNES components aren't available, show placeholder
            placeholder_frame = ttk.LabelFrame(qusb2snes_frame, text="QUSB2SNES Sync", padding=(15, 10))
            placeholder_frame.pack(fill="x")
            ttk.Label(
                placeholder_frame,
                text="QUSB2SNES sync feature not available (missing dependencies)",
                font=self.font
            ).pack()

        # Log section with level dropdown and clear button
        log_header_frame = ttk.Frame(self.frame)
        log_header_frame.pack(fill="x", pady=(0, 5))
        
        # Log level dropdown (left side)
        ttk.Label(log_header_frame, text="Log Level:", style="Custom.TLabel").pack(side="left")
        
        self.log_level_combo = ttk.Combobox(
            log_header_frame,
            values=["Information", "Debug", "Error"],
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
        
        # Log text area - takes remaining space to bottom
        log_text = self.logger.setup(self.frame)
        log_text.pack(fill="both", expand=True, pady=(2, 5))
        
        # Store reference for theme toggling
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
            # Show the entire duplicate frame
            self.duplicate_frame.pack(fill="x", pady=(8, 0))
        else:
            # Hide the entire duplicate frame
            self.duplicate_frame.pack_forget()
    
    def _load_multi_type_settings(self):
        """Load multi-type settings from config"""
        try:
            # Use shared config instead of creating new instance
            config = self.setup_section.config
            
            # Load settings with defaults
            enabled = config.get("multi_type_enabled", True)
            mode = config.get("multi_type_download_mode", "primary_only")
            
            self.multi_type_enabled_var.set(enabled)
            self.download_mode_var.set(mode)
            
        except Exception as e:
            print(f"Error loading multi-type settings: {e}")
            # Set defaults
            self.multi_type_enabled_var.set(True)
            self.download_mode_var.set("primary_only")
    
    def _save_multi_type_settings(self, *args):
        """Save multi-type settings to config"""
        try:
            # Use shared config instead of creating new instance
            config = self.setup_section.config
            
            enabled = self.multi_type_enabled_var.get()
            mode = self.download_mode_var.get()
            
            config.set("multi_type_enabled", enabled)
            config.set("multi_type_download_mode", mode)  
            config.save()  # Critical: Save changes to disk!
            
        except Exception as e:
            print(f"Error saving multi-type settings: {e}")
    
    def _check_for_updates(self):
        """Check for updates manually"""
        try:
            # Import here to avoid circular imports
            from updater import Updater, UpdateDialog
            from main import VERSION
            
            # Disable button during check
            self.check_updates_button.config(state="disabled", text="Checking...")
            self.frame.update()
            
            def check_updates():
                try:
                    updater = Updater(VERSION.lstrip('v'))
                    update_info = updater.check_for_updates(silent=True)  # Use silent=True to avoid duplicate dialogs
                    
                    # Schedule UI updates on the main thread
                    def update_ui():
                        try:
                            # Re-enable button
                            self.check_updates_button.config(state="normal", text="Check for Updates")
                            
                            if update_info:
                                # Add current version to update info
                                update_info['current_version'] = VERSION.lstrip('v')
                                
                                # Show update dialog
                                root = self.parent.winfo_toplevel()
                                dialog = UpdateDialog(root, update_info)
                                dialog.show()
                            else:
                                # No update available
                                messagebox.showinfo("No Updates", "You are already using the latest version!")
                        except Exception as e:
                            print(f"UI update error: {e}")
                    
                    # Schedule UI update on main thread
                    root = self.parent.winfo_toplevel()
                    root.after(0, update_ui)
                        
                except Exception as e:
                    # Schedule error handling on main thread
                    def handle_error():
                        self.check_updates_button.config(state="normal", text="Check for Updates")
                        messagebox.showerror("Update Check Failed", f"Failed to check for updates: {str(e)}")
                        print(f"Update check error: {e}")  # Debug print
                    
                    root = self.parent.winfo_toplevel()
                    root.after(0, handle_error)
            
            # Run check in background thread
            import threading
            thread = threading.Thread(target=check_updates, daemon=True)
            thread.start()
            
        except Exception as e:
            self.check_updates_button.config(state="normal", text="Check for Updates")
            messagebox.showerror("Update Check Failed", f"Failed to check for updates: {str(e)}")
            print(f"Outer update check error: {e}")  # Debug print
    
    def _save_auto_check_setting(self):
        """Save auto-check updates setting"""
        try:
            # Use shared config instead of creating new instance
            config = self.setup_section.config
            
            auto_check = self.auto_check_updates_var.get()
            config.set("auto_check_updates", auto_check)
            config.save()  # Critical: Save changes to disk!
            
        except Exception as e:
            print(f"Error saving auto-check setting: {e}")
    
    def _load_auto_check_setting(self):
        """Load auto-check updates setting"""
        try:
            # Use shared config instead of creating new instance
            config = self.setup_section.config
            
            auto_check = config.get("auto_check_updates", False)
            self.auto_check_updates_var.set(auto_check)
            
        except Exception as e:
            print(f"Error loading auto-check setting: {e}")
            self.auto_check_updates_var.set(True)  # Default to True
