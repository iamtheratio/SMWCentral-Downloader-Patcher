"""
QUSB2SNES Settings UI Component - Simple Implementation
Provides QUSB2SNES sync configuration interface for Settings page

Copyright (c) 2025 iamtheratio
Licensed under the MIT License - see LICENSE file for details
"""

import tkinter as tk
from tkinter import ttk, messagebox
import asyncio
import threading
import sys
import os

# Add project path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qusb2snes_sync import QUSB2SNESSyncManager
from ui_constants import get_labelframe_padding


class QUSB2SNESSection:
    """Simple QUSB2SNES settings section"""
    
    def __init__(self, parent, config_manager, logger):
        self.parent = parent
        self.config = config_manager
        self.logger = logger
        self.frame = None
        
        # UI components
        self.enabled_var = None
        self.host_var = None
        self.port_var = None
        self.device_var = None
        self.remote_folder_var = None
        self.device_combo = None
        self.connect_button = None
        self.sync_button = None
        
        # Sync manager
        self.sync_manager = QUSB2SNESSyncManager()
        self.sync_manager.on_progress = self._on_progress
        self.sync_manager.on_error = self._on_error
        self.sync_manager.on_connected = self._on_connected
        self.sync_manager.on_disconnected = self._on_disconnected
        
        # State
        self.connected = False
        self.devices = []
        self.syncing = False
    
    def create(self, font):
        """Create the QUSB2SNES settings section"""
        self.frame = ttk.LabelFrame(self.parent, text="QUSB2SNES Sync", padding=get_labelframe_padding())
        
        # Initialize variables
        self.enabled_var = tk.BooleanVar(value=self.config.get("qusb2snes_enabled", False))
        self.host_var = tk.StringVar(value=self.config.get("qusb2snes_host", "localhost"))
        self.port_var = tk.IntVar(value=self.config.get("qusb2snes_port", 23074))
        self.device_var = tk.StringVar(value=self.config.get("qusb2snes_device", ""))
        self.remote_folder_var = tk.StringVar(value=self.config.get("qusb2snes_remote_folder", "/ROMS"))
        
        # Enable/Disable checkbox
        enable_cb = ttk.Checkbutton(
            self.frame, 
            text="Enable",
            variable=self.enabled_var,
            command=self._on_enabled_changed
        )
        enable_cb.grid(row=0, column=0, columnspan=9, sticky="w", pady=(0, 15))
        
        # Row 1: Section Headers
        ttk.Label(self.frame, text="Host:").grid(row=1, column=0, sticky="w", padx=(0, 5))
        ttk.Label(self.frame, text="Port:").grid(row=1, column=1, sticky="w", padx=(0, 5))
        ttk.Label(self.frame, text="Device:").grid(row=1, column=3, sticky="w", padx=(20, 5))
        ttk.Label(self.frame, text="Sync To Folder:").grid(row=1, column=5, sticky="w", padx=(20, 5))
        
        # Row 2: Input Controls
        # Column 1: Connection Section
        self.host_entry = ttk.Entry(self.frame, textvariable=self.host_var, width=12)
        self.host_entry.grid(row=2, column=0, sticky="ew", padx=(0, 5), pady=(0, 5))
        self.host_entry.bind('<KeyRelease>', self._on_setting_changed)
        
        self.port_entry = ttk.Entry(self.frame, textvariable=self.port_var, width=8)
        self.port_entry.grid(row=2, column=1, sticky="ew", padx=(0, 15), pady=(0, 5))
        self.port_entry.bind('<KeyRelease>', self._on_setting_changed)
        
        # Column 2: Device Section
        self.device_combo = ttk.Combobox(
            self.frame,
            textvariable=self.device_var,
            state="readonly",
            width=20
        )
        self.device_combo.grid(row=2, column=3, sticky="ew", padx=(20, 15), pady=(0, 5))
        self.device_combo.bind('<<ComboboxSelected>>', self._on_device_changed)
        
        # Column 3: Sync Section
        self.folder_entry = ttk.Entry(self.frame, textvariable=self.remote_folder_var, width=15)
        self.folder_entry.grid(row=2, column=5, sticky="ew", padx=(20, 5), pady=(0, 5))
        self.folder_entry.bind('<KeyRelease>', self._on_setting_changed)
        
        # Row 3: Action Buttons
        self.connect_button = ttk.Button(
            self.frame,
            text="Connect",
            command=self._on_connect_clicked,
            width=12
        )
        self.connect_button.grid(row=3, column=0, columnspan=2, sticky="ew", padx=(0, 15), pady=(5, 0))
        
        self.refresh_button = ttk.Button(
            self.frame,
            text="Refresh",
            command=self._on_refresh_clicked,
            width=12
        )
        self.refresh_button.grid(row=3, column=3, sticky="ew", padx=(20, 15), pady=(5, 0))
        
        self.sync_button = ttk.Button(
            self.frame,
            text="Sync",
            command=self._on_sync_clicked,
            width=12
        )
        self.sync_button.grid(row=3, column=5, sticky="ew", padx=(20, 5), pady=(5, 0))
        
        # Update UI state
        self._update_ui_state()
        
        return self.frame
    
    def _on_enabled_changed(self):
        """Handle enable/disable checkbox change"""
        self.config.set("qusb2snes_enabled", self.enabled_var.get())
        self._update_ui_state()
    
    def _on_setting_changed(self, event=None):
        """Handle setting changes"""
        try:
            self.config.set("qusb2snes_host", self.host_var.get())
            self.config.set("qusb2snes_port", self.port_var.get())
            self.config.set("qusb2snes_remote_folder", self.remote_folder_var.get())
        except tk.TclError:
            pass  # Ignore invalid port values during typing
    
    def _on_device_changed(self, event=None):
        """Handle device selection change"""
        self.config.set("qusb2snes_device", self.device_var.get())
    
    def _update_ui_state(self):
        """Update UI component states"""
        enabled = self.enabled_var.get()
        
        # Basic widgets that follow the enabled state
        basic_widgets = [
            self.host_entry,
            self.port_entry, 
            self.device_combo,
            self.folder_entry
        ]
        
        basic_state = "normal" if enabled else "disabled"
        for widget in basic_widgets:
            if widget:
                widget.configure(state=basic_state)
        
        # Connect button logic
        if self.connect_button:
            if not enabled:
                self.connect_button.configure(state="disabled", text="Connect", style="TButton")
            elif self.connected:
                # Connected state - normal gray "Disconnect" button
                self.connect_button.configure(state="normal", text="Disconnect", style="TButton")
            else:
                # Not connected - blue accent "Connect" button
                self.connect_button.configure(state="normal", text="Connect", style="Accent.TButton")
        
        # Refresh button - only enabled when connected
        if self.refresh_button:
            refresh_state = "normal" if (enabled and self.connected) else "disabled"
            self.refresh_button.configure(state=refresh_state)
        
        # Sync button - only enabled when connected and not syncing
        if self.sync_button:
            if not enabled or not self.connected:
                self.sync_button.configure(state="disabled", text="Sync", style="TButton")
            elif self.syncing:
                # Currently syncing - gray "Syncing" button
                self.sync_button.configure(state="disabled", text="Syncing", style="TButton")
            else:
                # Connected and ready - blue accent "Sync" button
                self.sync_button.configure(state="normal", text="Sync", style="Accent.TButton")
    
    def _on_connect_clicked(self):
        """Handle connect/disconnect button click"""
        # Disable connect button during connection process
        if self.connect_button:
            self.connect_button.configure(state="disabled", text="Connecting...")
        
        if self.connected:
            self._disconnect()
        else:
            self._connect()
    
    def _connect(self):
        """Connect to QUSB2SNES in background thread"""
        def connect_thread():
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                self.sync_manager.configure(
                    self.host_var.get(),
                    self.port_var.get(), 
                    "",  # Don't auto-attach device yet
                    self.remote_folder_var.get()
                )
                
                success = loop.run_until_complete(self.sync_manager.connect_and_attach())
                
                if success:
                    # Get devices
                    devices = loop.run_until_complete(self.sync_manager.get_devices())
                    self.parent.after(0, lambda: self._on_progress(f"Found {len(devices)} device(s): {', '.join(devices) if devices else 'None'}"))
                    
                    # Update UI in main thread
                    self.parent.after(0, lambda: self._update_devices(devices))
                    self.parent.after(0, lambda: self._on_connected())
                else:
                    # Connection failed - restore button state
                    self.parent.after(0, lambda: self._update_ui_state())
                
            except Exception as e:
                self.parent.after(0, lambda: self._on_error(f"Connection failed: {str(e)}"))
                # Restore button state on error
                self.parent.after(0, lambda: self._update_ui_state())
            finally:
                self._cleanup_event_loop(loop)
        
        threading.Thread(target=connect_thread, daemon=True).start()
    
    def _disconnect(self):
        """Disconnect from QUSB2SNES"""
        # Update button immediately
        if self.connect_button:
            self.connect_button.configure(state="disabled", text="Disconnecting...")
        
        def disconnect_thread():
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(self.sync_manager.disconnect())
            except:
                pass
            finally:
                self._cleanup_event_loop(loop)
                # Restore UI state in main thread
                self.parent.after(0, lambda: self._update_ui_state())
        
        threading.Thread(target=disconnect_thread, daemon=True).start()
    
    def _on_refresh_clicked(self):
        """Refresh device list"""
        if not self.connected:
            self._on_error("Connect to QUSB2SNES first")
            return
        
        self._on_progress("🔄 Refreshing device list...")
        
        # Simply re-run the device discovery part of the connection process
        def refresh_thread():
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                # Create a fresh client for device discovery only
                temp_client = self.sync_manager.sync_client.__class__(
                    self.sync_manager.host, 
                    self.sync_manager.port
                )
                
                if loop.run_until_complete(temp_client.connect()):
                    devices = loop.run_until_complete(temp_client.get_devices())
                    loop.run_until_complete(temp_client.disconnect())
                    
                    # Update UI in main thread
                    self.parent.after(0, lambda: self._update_devices(devices))
                else:
                    self.parent.after(0, lambda: self._on_error("Failed to connect for device refresh"))
                
            except Exception as e:
                self.parent.after(0, lambda: self._on_error(f"Refresh failed: {str(e)}"))
            finally:
                self._cleanup_event_loop(loop)
        
        threading.Thread(target=refresh_thread, daemon=True).start()
    
    def _on_sync_clicked(self):
        """Handle sync button click"""
        if not self.connected:
            self._on_error("Connect to QUSB2SNES first")
            return
        
        if not self.device_var.get():
            self._on_error("Select a device first")
            return
        
        local_rom_dir = self.config.get("output_dir", "")
        if not local_rom_dir:
            self._on_error("Configure ROM output directory in Setup section first")
            return
        
        if not os.path.exists(local_rom_dir):
            self._on_error(f"ROM directory does not exist: {local_rom_dir}")
            return
        
        # Count ROM files to sync (recursively search all subdirectories)
        rom_extensions = ['.smc', '.sfc', '.fig']
        rom_files = []
        total_dirs = 0
        try:
            for root, dirs, files in os.walk(local_rom_dir):
                total_dirs += len(dirs) if root == local_rom_dir else 0  # Count only direct subdirs
                for file in files:
                    if any(file.lower().endswith(ext) for ext in rom_extensions):
                        # Use proper path separators
                        full_path = os.path.normpath(os.path.join(root, file))
                        rom_files.append(full_path)
        except Exception as e:
            rom_files = [f"Error scanning directory: {str(e)}"]
            total_dirs = 0
        
        # Debug: Log what we found
        self._on_progress(f"📁 Scanning output directory: {local_rom_dir}")
        self._on_progress(f"🔍 Found {len(rom_files)} ROM files in {total_dirs} subdirectories")
        
        # Show first few files for debugging
        if rom_files and not str(rom_files[0]).startswith("Error"):
            sample_files = rom_files[:3]  # Show first 3 files
            for i, file_path in enumerate(sample_files, 1):
                rel_path = os.path.relpath(file_path, local_rom_dir)
                self._on_progress(f"   {i}. {rel_path}")
            if len(rom_files) > 3:
                self._on_progress(f"   ... and {len(rom_files) - 3} more files")
        
        # Create detailed confirmation message
        sync_info = f"""QUSB2SNES ROM Sync Operation
        
📁 SOURCE (Local Computer):
   {local_rom_dir}
   
📂 DESTINATION (SD Card):
   Device: {self.device_var.get()}
   Folder: {self.remote_folder_var.get()}
   
📋 OPERATION DETAILS:
   • ROM files found: {len(rom_files)} files
   • Subdirectories: {total_dirs} folders
   • File types: .smc, .sfc, .fig
   • Searches all subdirectories recursively
   • Missing files will be uploaded
   • Existing files will be updated if different
   
⚠️  NOTE: This will modify files on your SD card.
   Make sure you have backups if needed.
   
Do you want to proceed with the sync?"""
        
        # Confirm sync operation
        result = messagebox.askyesno(
            "Confirm ROM Sync Operation",
            sync_info
        )
        
        if not result:
            return
        
        # Set syncing state and update UI
        self.syncing = True
        self._update_ui_state()
        
        # Start sync in background thread
        def sync_thread():
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                # Create a completely fresh sync manager for this operation
                # to avoid cross-loop task reference issues
                from qusb2snes_sync import QUSB2SNESSyncManager
                fresh_sync_manager = QUSB2SNESSyncManager()
                fresh_sync_manager.on_progress = self._on_progress
                fresh_sync_manager.on_error = self._on_error
                
                # Configure with current settings
                fresh_sync_manager.configure(
                    self.host_var.get(),
                    int(self.port_var.get()),
                    self.device_var.get(),
                    self.remote_folder_var.get()
                )
                
                # Connect and perform sync
                if loop.run_until_complete(fresh_sync_manager.connect_and_attach()):
                    result = loop.run_until_complete(fresh_sync_manager.sync_roms(local_rom_dir))
                    
                    if result:
                        # Save current timestamp for next sync
                        import time
                        current_timestamp = time.time()
                        self.config.set("qusb2snes_last_sync", current_timestamp)
                        self.config.save()
                        
                        self.parent.after(0, lambda: self._on_progress(f"✅ Sync completed successfully"))
                    else:
                        self.parent.after(0, lambda: self._on_error("❌ Sync operation failed"))
                    
                    # Clean disconnect
                    loop.run_until_complete(fresh_sync_manager.disconnect())
                else:
                    self.parent.after(0, lambda: self._on_error("❌ Failed to connect for sync operation"))
                
            except Exception as e:
                self.parent.after(0, lambda: self._on_error(f"Sync failed: {str(e)}"))
            finally:
                # Properly close event loop with cleanup
                self._cleanup_event_loop(loop)
                # Reset syncing state and update UI
                self.parent.after(0, lambda: self._on_sync_complete())
        
        threading.Thread(target=sync_thread, daemon=True).start()
    
    def _on_sync_complete(self):
        """Called when sync operation completes (success or failure)"""
        self.syncing = False
        self._update_ui_state()
    
    def _update_devices(self, devices):
        """Update device list in UI thread"""
        self._on_progress(f"Updating device list with {len(devices)} devices: {devices}")
        self.devices = devices
        if self.device_combo:
            self.device_combo['values'] = devices
            
            if len(devices) == 1:
                # Auto-select the only device
                self.device_var.set(devices[0])
                self._on_device_changed()
                self._on_progress(f"Auto-selected only device: {devices[0]}")
            elif len(devices) > 1:
                # Multiple devices - auto-select if nothing is selected, otherwise keep current selection
                if not self.device_var.get() or self.device_var.get() not in devices:
                    self.device_var.set(devices[0])
                    self._on_device_changed()
                    self._on_progress(f"Auto-selected first device: {devices[0]} (multiple devices available)")
                else:
                    self._on_progress(f"Keeping current selection: {self.device_var.get()}")
            else:
                # No devices found
                self.device_var.set("")
                self._on_progress("No devices found. Make sure your SD2SNES/FX Pak Pro is connected.")
    
    def _cleanup_event_loop(self, loop):
        """Properly cleanup asyncio event loop to prevent warnings"""
        try:
            # Cancel all pending tasks
            pending = asyncio.all_tasks(loop)
            for task in pending:
                task.cancel()
            
            # Wait for cancelled tasks to finish
            if pending:
                loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
                
        except Exception:
            pass  # Ignore cleanup errors
        finally:
            loop.close()
    
    def _on_progress(self, message):
        """Handle progress messages"""
        if self.logger:
            self.logger.log(message, "Information")
    
    def _on_error(self, message):
        """Handle error messages"""
        if self.logger:
            self.logger.log(message, "Error")
    
    def _on_connected(self):
        """Handle connection success"""
        self.connected = True
        self._update_ui_state()
        self._on_progress("✅ Ready for device operations")
    
    def _on_disconnected(self):
        """Handle disconnection"""
        self.connected = False
        self.devices = []
        if self.device_combo:
            self.device_combo['values'] = []
            self.device_var.set("")
        self._update_ui_state()
        self._on_progress("🔌 Disconnected from QUSB2SNES")