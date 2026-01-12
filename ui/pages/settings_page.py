import tkinter as tk
from tkinter import ttk, messagebox
import threading
import subprocess
import sys
import os
import platform

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
        
        # Callback for emulator settings changes
        self.emulator_settings_callback = None
    
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

        # Second row: Emulator and Difficulty Migration side by side
        second_row_frame = ttk.Frame(self.frame)
        second_row_frame.pack(fill="x", pady=(5, 20))
        
        # Emulator Configuration Section (left side)
        emulator_frame = ttk.LabelFrame(second_row_frame, text="Emulator Configuration", padding=(15, 10, 15, 15))
        emulator_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        # Emulator path
        emulator_path_frame = ttk.Frame(emulator_frame)
        emulator_path_frame.pack(fill="x", pady=(0, 8))
        
        ttk.Label(emulator_path_frame, text="Emulator Path:", style="Custom.TLabel").pack(side="left", padx=(0, 10))
        
        self.emulator_path_entry = ttk.Entry(emulator_path_frame, width=50)
        self.emulator_path_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        ttk.Button(
            emulator_path_frame,
            text="Browse",
            command=self._browse_emulator,
            style="Custom.TButton"
        ).pack(side="left")
        
        # Emulator arguments checkbox
        self.emulator_args_enabled_var = tk.BooleanVar()
        self.emulator_args_checkbox = ttk.Checkbutton(
            emulator_frame,
            text="Use Custom Command Line Arguments",
            variable=self.emulator_args_enabled_var,
            style="Custom.TCheckbutton",
            command=self._on_emulator_args_toggle
        )
        self.emulator_args_checkbox.pack(anchor="w", pady=(0, 8))
        
        # Emulator arguments
        emulator_args_frame = ttk.Frame(emulator_frame)
        emulator_args_frame.pack(fill="x", pady=(0, 8))
        
        ttk.Label(emulator_args_frame, text="Command Line Arguments:", style="Custom.TLabel").pack(side="left", padx=(0, 10))
        
        self.emulator_args_entry = ttk.Entry(emulator_args_frame, width=50)
        self.emulator_args_entry.pack(side="left", fill="x", expand=True)
        
        # Help text
        help_text = ttk.Label(
            emulator_frame,
            text="Use %1 as a placeholder for the ROM file path, or leave it out to append the ROM at the end.\n"
                 "Examples:\n"
                     "  • RetroArch (Windows): -L cores/snes9x_libretro.dll \"%1\"\n"
                     "  • RetroArch (macOS): -L \"~/Library/Application Support/RetroArch/cores/snes9x_libretro.dylib\" \"%1\"\n"
                 "  • Snes9x: --fullscreen (ROM will be added automatically)",
            style="Custom.TLabel",
            font=("Segoe UI", 8),
            foreground="gray"
        )
        help_text.pack(anchor="w", pady=(0, 8))
        
        # Load emulator settings
        self._load_emulator_settings()
        
        # Bind changes to save settings
        self.emulator_path_entry.bind("<FocusOut>", self._save_emulator_settings)
        self.emulator_args_entry.bind("<FocusOut>", self._save_emulator_settings)
        self.emulator_args_entry.bind("<Return>", self._save_emulator_settings)

        # Data Migration Section (right side)
        migration_frame = ttk.LabelFrame(second_row_frame, text="Data Migration", padding=(15, 10))
        migration_frame.pack(side="right", fill="both", expand=True, padx=(10, 0))
        
        ttk.Label(
            migration_frame,
            text="Manage your collection data. Fetch missing details (like release dates) from SMWCentral, "
                 "and update outdated difficulty categories to match the latest site standards.",
            style="Custom.TLabel",
            wraplength=428
        ).pack(anchor="w", pady=(0, 10))
        
        # Status label
        self.migration_status_label = ttk.Label(
            migration_frame,
            text="Select an action below",
            style="Custom.TLabel"
        )
        self.migration_status_label.pack(anchor="w", pady=(0, 10))
        
        # Buttons
        migration_buttons = ttk.Frame(migration_frame)
        migration_buttons.pack(fill="x")
        
        self.check_migration_button = ttk.Button(
            migration_buttons,
            text="Check Difficulties",
            command=self._check_difficulty_migration,
            style="Custom.TButton"
        )
        self.check_migration_button.pack(side="left", padx=(0, 10))
        
        self.apply_migration_button = ttk.Button(
            migration_buttons,
            text="Apply Fixes",
            command=self._apply_difficulty_migration,
            style="Accent.TButton",
            state="disabled"
        )
        self.apply_migration_button.pack(side="left", padx=(0, 10))
        
        # NEW: Fetch Metadata Button
        self.fetch_metadata_button = ttk.Button(
            migration_buttons,
            text="Fetch Metadata",
            command=self._fetch_missing_metadata,
            style="Custom.TButton"
        )
        self.fetch_metadata_button.pack(side="left")

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
    
    def _check_difficulty_migration(self):
        """Check if difficulty migrations are needed"""
        self.check_migration_button.config(state="disabled", text="Checking...")
        self.frame.update_idletasks()
        
        try:
            from difficulty_migration import DifficultyMigrator
            from config_manager import ConfigManager
            
            config = ConfigManager()
            output_dir = config.get("output_dir", "")
            
            if not output_dir or not os.path.exists(output_dir):
                self.migration_status_label.config(
                    text="⚠️ Please configure your output directory in Setup section first",
                    foreground="orange"
                )
                self.apply_migration_button.config(state="disabled")
                self.check_migration_button.config(state="normal", text="Check for Migrations")
                return
            
            # Check for missing difficulty_id fields first
            migrator = DifficultyMigrator(output_dir)
            backfill_check = migrator.backfill_difficulty_ids(dry_run=True)
            backfill_count = backfill_check.get("backfilled_count", 0)
            
            # Auto-detect renames
            detected = migrator.detect_renames_from_data()
            
            if not detected and backfill_count == 0:
                self.migration_status_label.config(
                    text="✅ Everything is up to date! Your hacks are using the latest difficulty categories.",
                    foreground="green"
                )
                self.apply_migration_button.config(state="disabled")
                self.check_migration_button.config(state="normal", text="Check for Migrations")
                return
            
            # Build status message
            status_parts = []
            
            # Add backfill info if needed
            if backfill_count > 0:
                status_parts.append(f"{backfill_count:,} hacks need difficulty_id backfill")
            
            # Add rename info if needed
            if detected:
                rename_count = len(detected)
                total_hacks = sum(count for _, count in detected.values())
                
                if rename_count == 1:
                    old_name, (new_name, count) = list(detected.items())[0]
                    status_parts.append(f"'{old_name}' → '{new_name}' ({count:,} hacks)")
                else:
                    renames = [f"'{old}' → '{new}'" for old, (new, _) in detected.items()]
                    status_parts.append(f"{rename_count} difficulty renames ({total_hacks:,} hacks)")
            
            status_text = "⚠️ " + " | ".join(status_parts)
            
            self.migration_status_label.config(text=status_text, foreground="orange")
            self.apply_migration_button.config(state="normal")
            self.check_migration_button.config(state="normal", text="Check for Migrations")
                
        except Exception as e:
            self.migration_status_label.config(
                text=f"❌ Error checking for updates: {str(e)}",
                foreground="red"
            )
            self.apply_migration_button.config(state="disabled")
            self.check_migration_button.config(state="normal", text="Check for Migrations")
            if self.logger:
                self.logger.log(f"Error checking difficulty migrations: {str(e)}", "Error")
        
        self.frame.update_idletasks()
    
    def _apply_difficulty_migration(self):
        """Apply difficulty migrations"""
        try:
            from difficulty_migration import DifficultyMigrator
            from config_manager import ConfigManager
            from tkinter import messagebox
            
            config = ConfigManager()
            output_dir = config.get("output_dir", "")
            
            if not output_dir or not os.path.exists(output_dir):
                messagebox.showerror("Migration Error", "Output directory not configured or doesn't exist")
                return
            
            # Check for backfill needs and auto-detect renames
            migrator = DifficultyMigrator(output_dir)
            backfill_check = migrator.backfill_difficulty_ids(dry_run=True)
            detected = migrator.detect_renames_from_data()
            
            backfill_count = backfill_check.get("backfilled_count", 0)
            
            if not detected and backfill_count == 0:
                messagebox.showinfo(
                    "No Migrations Needed", 
                    "Everything is up to date! Your hacks are already using the latest difficulty categories from SMWCentral."
                )
                return
            
            # Build confirmation message
            confirm_parts = []
            
            if backfill_count > 0:
                confirm_parts.append(f"Add missing difficulty_id field to {backfill_count:,} hacks")
            
            if detected:
                total_hacks = sum(count for _, count in detected.values())
                renames = [f"  • '{old}' will become '{new}' ({count:,} hacks)" for old, (new, count) in detected.items()]
                confirm_parts.append(f"Update difficulty names for {total_hacks:,} hacks:\n" + "\n".join(renames))
            
            confirm_msg = "The following updates will be applied:\n\n" + "\n\n".join(confirm_parts)
            confirm_msg += f"\n\nThis will:\n• Backfill missing difficulty_id fields (for old hacks)\n• Rename your difficulty folders to match SMWCentral\n• Update all hack records in your database\n• Create a backup before making any changes\n\nDo you want to proceed?"
            
            if not messagebox.askyesno("Confirm Migration", confirm_msg, icon='warning'):
                return
            
            # Disable button during migration
            self.apply_migration_button.config(state="disabled", text="Applying...")
            self.migration_status_label.config(text="⏳ Applying migrations...", foreground="blue")
            self.frame.update_idletasks()
            
            # Apply migrations
            results = migrator.perform_migrations(dry_run=False)
            
            if results.get("success"):
                summary = results.get("summary", {})
                folders = summary.get("folders_renamed", 0)
                json_entries = summary.get("json_entries_updated", 0)
                backfilled = summary.get("difficulty_ids_backfilled", 0)
                synced = summary.get("difficulty_fields_synced", 0)
                
                success_msg = f"✅ Update Complete!\n\n"
                if backfilled > 0:
                    success_msg += f"• Backfilled {backfilled} difficulty_id field(s)\n"
                if synced > 0:
                    success_msg += f"• Synced {synced} difficulty field(s)\n"
                success_msg += f"• Renamed {folders} folder(s)\n"
                success_msg += f"• Updated {json_entries} hack records\n\n"
                success_msg += "Your collection now uses the latest difficulty categories from SMWCentral!\n"
                if folders > 0:
                    success_msg += "(A backup was created in case you need to undo this change)"
                
                messagebox.showinfo("Update Complete", success_msg)
                
                self.migration_status_label.config(
                    text="✅ All migrations applied successfully",
                    foreground="green"
                )
                self.apply_migration_button.config(state="disabled", text="Apply Migrations")
                
                if self.logger:
                    if backfilled > 0:
                        self.logger.log(f"Backfilled {backfilled} difficulty_id fields", "Information")
                    if synced > 0:
                        self.logger.log(f"Synced {synced} difficulty fields", "Information")
                    for old_name, (new_name, count) in detected.items():
                        self.logger.log(f"Migrated '{old_name}' → '{new_name}' ({count:,} hacks)", "Information")
                    
                    # Build comprehensive summary message
                    summary_parts = []
                    if backfilled > 0:
                        summary_parts.append(f"{backfilled} IDs backfilled")
                    if synced > 0:
                        summary_parts.append(f"{synced} fields synced")
                    if folders > 0:
                        summary_parts.append(f"{folders} folders renamed")
                    if json_entries > 0:
                        summary_parts.append(f"{json_entries} entries updated")
                    
                    if summary_parts:
                        self.logger.log(f"Difficulty migration completed: {', '.join(summary_parts)}", "Information")
                    else:
                        self.logger.log("Difficulty migration completed: no changes needed", "Information")
            else:
                errors = results.get("errors", [])
                error_msg = "Migration failed:\n\n" + "\n".join(errors) if errors else "Unknown error occurred"
                messagebox.showerror("Migration Failed", error_msg)
                
                self.migration_status_label.config(text="❌ Migration failed", foreground="red")
                self.apply_migration_button.config(state="normal", text="Apply Migrations")
                
        except Exception as e:
            messagebox.showerror("Migration Error", f"Failed to apply migrations: {str(e)}")
            self.migration_status_label.config(text=f"❌ Error: {str(e)}", foreground="red")
            self.apply_migration_button.config(state="normal", text="Apply Migrations")
            
            if self.logger:
                self.logger.log(f"Error applying difficulty migrations: {str(e)}", "Error")
    def _fetch_missing_metadata(self):
        """Fetch missing metadata (release dates, etc.) for existing hacks"""
        if not messagebox.askyesno(
            "Fetch Metadata", 
            "This will verify all hacks in your collection and fetch missing data (like Release Dates) from SMWCentral.\n\n"
            "This process is rate-limited (1 request/sec) to respect the API.\n"
            "It may take several minutes depending on your collection size.\n\n"
            "Do you want to continue?"
        ):
            return

        self.fetch_metadata_button.config(state="disabled", text="Fetching...")
        self.migration_status_label.config(text="⏳ Fetching metadata...", foreground="blue")
        
        def run_backfill():
            try:
                import api_pipeline
                from config_manager import ConfigManager
                
                # Setup logging callback
                def log_cb(msg, level="Information"):
                    if self.logger:
                        self.logger.log(msg, level)
                        
                log_cb("Starting metadata backfill...", "Information")
                
                # Run the pipeline function
                count = api_pipeline.backfill_metadata(log_callback=log_cb)
                
                # Update UI on main thread
                def update_ui_success():
                    self.fetch_metadata_button.config(state="normal", text="Fetch Metadata")
                    self.migration_status_label.config(
                        text=f"✅ Metadata updated for {count} hacks", 
                        foreground="green"
                    )
                    messagebox.showinfo("Complete", f"Successfully updated metadata for {count} hacks.")
                    
                    # Trigger Collection Page Reload via injected callback
                    if hasattr(self, 'reload_collection_callback') and self.reload_collection_callback:
                        try:
                            print("DEBUG: Triggering Collection Page refresh via callback...")
                            self.reload_collection_callback()
                        except Exception as e:
                            print(f"DEBUG: Failed to reload collection callback: {e}")
                    
                self.frame.after(0, update_ui_success)
                
            except Exception as e:
                def update_ui_error():
                    self.fetch_metadata_button.config(state="normal", text="Fetch Metadata")
                    self.migration_status_label.config(text="❌ Fetch failed", foreground="red")
                    messagebox.showerror("Error", f"Failed to fetch metadata: {str(e)}")
                    if self.logger:
                        self.logger.log(f"Metadata backfill error: {str(e)}", "Error")
                
                self.frame.after(0, update_ui_error)

        import threading
        threading.Thread(target=run_backfill, daemon=True).start()

    def _browse_emulator(self):
        """Browse for emulator executable"""
        from tkinter import filedialog

        try:
            system = platform.system()

            # Set up file types based on platform
            if system == "Windows":
                filetypes = [("Executable Files", "*.exe"), ("All Files", "*.*")]
                initialdir = None
            elif system == "Darwin":  # macOS
                # Tk file dialogs can show .app bundles as grayed out on some macOS/Tk
                # builds. Prefer the native “choose application” picker via AppleScript.
                filetypes = [("All Files", "*"), ("Applications", "*.app")]
                initialdir = "/Applications"
            else:  # Linux
                filetypes = [("All Files", "*")]
                initialdir = None

            # Helper function to avoid duplicating the Tk dialog call
            def _tk_file_picker():
                return filedialog.askopenfilename(
                    title="Select Emulator",
                    filetypes=filetypes,
                    initialdir=initialdir,
                )

            filename = ""

            if system == "Darwin":
                try:
                    result = subprocess.run(
                        [
                            "osascript",
                            "-e",
                            'POSIX path of (choose file of type {"app"} with prompt "Select Emulator" default location (POSIX file "/Applications"))',
                        ],
                        check=True,
                        capture_output=True,
                        text=True,
                    )
                    filename = (result.stdout or "").strip()
                    if filename.endswith("/"):
                        filename = filename[:-1]
                except subprocess.CalledProcessError as e:
                    # User canceled AppleScript picker -> stop (no further dialogs)
                    if e.returncode == 1:
                        return

                    # Unexpected AppleScript failure -> fallback to Tk dialog
                    filename = _tk_file_picker()
                except Exception as ex:
                    # osascript not available/other error -> fallback to Tk dialog
                    if self.logger:
                        self.logger.log(f"AppleScript picker failed: {ex}. Using Tk fallback.", "Debug")
                    filename = _tk_file_picker()
            else:
                filename = _tk_file_picker()

            # macOS: if the user clicked inside a .app bundle, normalize to the bundle root
            if filename and system == "Darwin" and ".app/" in filename:
                # Find the first .app bundle in the path (handles nested .app cases)
                app_index = filename.find(".app/")
                if app_index != -1:
                    filename = filename[:app_index + 4]  # +4 to include ".app"

            # If user cancels, stop cleanly (avoid chaining dialogs)
            if not filename:
                return

            # macOS: Convert .app bundle to actual executable
            if system == "Darwin" and filename.endswith(".app"):
                filename = self._convert_app_to_executable(filename)

            self.emulator_path_entry.delete(0, tk.END)
            self.emulator_path_entry.insert(0, filename)
            
            # Auto-fill command line arguments for known emulators
            if hasattr(self, '_auto_fill_emulator_args'):
                self._auto_fill_emulator_args(filename)
                
            self._save_emulator_settings()

        except Exception as e:
            if self.logger:
                self.logger.log(f"Failed to browse for emulator: {e}", "Error")
            messagebox.showerror("Browse Error", f"Failed to browse for emulator:\n\n{e}")
    
    def _auto_fill_emulator_args(self, emulator_path):
        """Auto-fill command line arguments for known emulators if args field is empty"""
        # Only auto-fill if the args field is currently empty
        current_args = self.emulator_args_entry.get().strip()
        if current_args:
            return  # Don't overwrite existing arguments
        
        emulator_lower = emulator_path.lower()
        system = platform.system()
        suggested_args = None
        
        # RetroArch detection
        if "retroarch" in emulator_lower:
            if system == "Darwin":  # macOS
                suggested_args = '-L "~/Library/Application Support/RetroArch/cores/snes9x_libretro.dylib" "%1"'
            elif system == "Windows":
                suggested_args = '-L cores/snes9x_libretro.dll "%1"'
            else:  # Linux
                suggested_args = '-L ~/.config/retroarch/cores/snes9x_libretro.so "%1"'
        
        # Apply suggested arguments if found
        if suggested_args:
            self.emulator_args_entry.delete(0, tk.END)
            self.emulator_args_entry.insert(0, suggested_args)
            self.emulator_args_enabled_var.set(True)
            self._on_emulator_args_toggle()  # Update UI state
            
            if self.logger:
                self.logger.log(f"Auto-filled RetroArch command line arguments", "Information")
    
    def _convert_app_to_executable(self, app_path):
        """Convert macOS .app bundle path to actual executable path"""
        # Extract app name from path
        app_name = os.path.basename(app_path).replace(".app", "")
        
        # Standard macOS app structure: AppName.app/Contents/MacOS/AppName
        executable_path = os.path.join(app_path, "Contents", "MacOS", app_name)
        
        # Check if the standard executable exists
        if os.path.exists(executable_path):
            if self.logger:
                self.logger.log(f"Converted .app bundle to executable: {executable_path}", "Information")
            return executable_path
        
        # Fallback: Try to find any executable in Contents/MacOS/
        macos_dir = os.path.join(app_path, "Contents", "MacOS")
        if os.path.exists(macos_dir):
            for file in os.listdir(macos_dir):
                file_path = os.path.join(macos_dir, file)
                if os.path.isfile(file_path) and os.access(file_path, os.X_OK):
                    if self.logger:
                        self.logger.log(f"Found executable in .app bundle: {file_path}", "Information")
                    return file_path
        
        # If no executable found, return original path with warning
        if self.logger:
            self.logger.log(f"Could not find executable in .app bundle, using bundle path", "Warning")
        return app_path
    
    def _load_emulator_settings(self):
        """Load emulator settings from config"""
        try:
            config = self.setup_section.config
            
            emulator_path = config.get("emulator_path", "")
            emulator_args = config.get("emulator_args", "")
            emulator_args_enabled = config.get("emulator_args_enabled", False)
            
            self.emulator_path_entry.delete(0, tk.END)
            self.emulator_path_entry.insert(0, emulator_path)
            
            self.emulator_args_entry.delete(0, tk.END)
            self.emulator_args_entry.insert(0, emulator_args)
            
            self.emulator_args_enabled_var.set(emulator_args_enabled)
            
            # Update entry state based on checkbox
            self._on_emulator_args_toggle()
            
        except Exception as e:
            print(f"Error loading emulator settings: {e}")
    
    def _save_emulator_settings(self, event=None):
        """Save emulator settings to config"""
        try:
            config = self.setup_section.config
            
            emulator_path = self.emulator_path_entry.get().strip()
            emulator_args = self.emulator_args_entry.get().strip()
            emulator_args_enabled = self.emulator_args_enabled_var.get()
            
            config.set("emulator_path", emulator_path)
            config.set("emulator_args", emulator_args)
            config.set("emulator_args_enabled", emulator_args_enabled)
            
            # Save the config
            config.save()
            
            # Show success message briefly or via log
            if self.logger:
                self.logger.log(f"Emulator settings saved - path: '{emulator_path}'", "Information")
            
            # Notify callback if registered (e.g., collection page to refresh cache)
            if self.emulator_settings_callback:
                if self.logger:
                    self.logger.log(
                        "🔔 Calling emulator settings callback to refresh collection cache...",
                        "Debug",
                    )
                try:
                    self.emulator_settings_callback()
                except Exception as callback_error:
                    # Ensure that a failing callback does not break the save flow
                    if self.logger:
                        self.logger.log(
                            f"Error while running emulator settings callback: {callback_error}",
                            "Error",
                        )
                    else:
                        print(f"Error while running emulator settings callback: {callback_error}")
            else:
                if self.logger:
                    self.logger.log(f"⚠️ No emulator settings callback registered!", "Debug")

            # Trigger collection page reload if callback exists (from feature branch)
            if hasattr(self, 'reload_collection_callback') and self.reload_collection_callback:
                try:
                    self.reload_collection_callback()
                except Exception as e:
                    print(f"Error triggering collection reload: {e}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save emulator settings: {e}")
    
    def _on_emulator_args_toggle(self):
        """Handle toggle of emulator args checkbox"""
        enabled = self.emulator_args_enabled_var.get()
        state = "normal" if enabled else "disabled"
        self.emulator_args_entry.config(state=state)
        self._save_emulator_settings()