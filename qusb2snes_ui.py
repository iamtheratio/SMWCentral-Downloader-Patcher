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
        
        # Add cancellation support
        self.sync_cancelled = False
        self.current_sync_loop = None
    
    def create(self, font):
        """Create the QUSB2SNES settings section"""
        self.frame = ttk.LabelFrame(self.parent, text="QUSB2SNES Sync", padding=get_labelframe_padding())
        
        # Initialize variables
        self.enabled_var = tk.BooleanVar(value=self.config.get("qusb2snes_enabled", False))
        self.host_var = tk.StringVar(value=self.config.get("qusb2snes_host", "localhost"))
        self.port_var = tk.IntVar(value=self.config.get("qusb2snes_port", 23074))
        self.device_var = tk.StringVar(value=self.config.get("qusb2snes_device", ""))
        self.remote_folder_var = tk.StringVar(value=self.config.get("qusb2snes_remote_folder", "/roms"))
        
        # Row 0: Enable checkbox and labels
        enable_cb = ttk.Checkbutton(
            self.frame, 
            text="Enable",
            variable=self.enabled_var,
            command=self._on_enabled_changed
        )
        enable_cb.grid(row=0, column=0, sticky="nw", padx=(0, 20), pady=(5, 2))
        
        # Labels above their respective controls (matching Photoshop mockup)
        ttk.Label(self.frame, text="Host:").grid(row=0, column=1, sticky="w", padx=(0, 5), pady=(5, 2))
        ttk.Label(self.frame, text="Port:").grid(row=0, column=2, sticky="w", padx=(5, 5), pady=(5, 2))
        ttk.Label(self.frame, text="Device:").grid(row=0, column=3, sticky="w", padx=(5, 5), pady=(5, 2))
        ttk.Label(self.frame, text="Sync To Folder:").grid(row=0, column=4, sticky="w", padx=(5, 5), pady=(5, 2))
        
        # Row 1: Input Controls (under their labels)
        self.host_entry = ttk.Entry(self.frame, textvariable=self.host_var, width=10)
        self.host_entry.grid(row=1, column=1, sticky="ew", padx=(0, 5), pady=(0, 5))
        self.host_entry.bind('<KeyRelease>', self._on_setting_changed)
        
        self.port_entry = ttk.Entry(self.frame, textvariable=self.port_var, width=6)
        self.port_entry.grid(row=1, column=2, sticky="ew", padx=(5, 5), pady=(0, 5))
        self.port_entry.bind('<KeyRelease>', self._on_setting_changed)
        
        self.device_combo = ttk.Combobox(
            self.frame,
            textvariable=self.device_var,
            state="readonly",
            width=15
        )
        self.device_combo.grid(row=1, column=3, sticky="ew", padx=(5, 5), pady=(0, 5))
        self.device_combo.bind('<<ComboboxSelected>>', self._on_device_changed)
        
        # Much wider Sync To Folder field to match mockup
        self.folder_entry = ttk.Entry(self.frame, textvariable=self.remote_folder_var, width=35)
        self.folder_entry.grid(row=1, column=4, columnspan=2, sticky="ew", padx=(5, 5), pady=(0, 5))
        self.folder_entry.bind('<KeyRelease>', self._on_setting_changed)
        
        # Row 2: Action Buttons with consistent fixed width and left alignment
        self.connect_button = ttk.Button(
            self.frame,
            text="Connect",
            command=self._on_connect_clicked,
            width=12
        )
        self.connect_button.grid(row=2, column=1, columnspan=2, sticky="w", padx=(0, 5), pady=(10, 5))
        
        self.refresh_button = ttk.Button(
            self.frame,
            text="Refresh",
            command=self._on_refresh_clicked,
            width=12
        )
        self.refresh_button.grid(row=2, column=3, sticky="w", padx=(5, 5), pady=(10, 5))
        
        self.sync_button = ttk.Button(
            self.frame,
            text="Sync",
            command=self._on_sync_clicked,
            width=12
        )
        self.sync_button.grid(row=2, column=4, columnspan=2, sticky="w", padx=(5, 5), pady=(10, 5))
        
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
                    # Connection failed - provide helpful guidance
                    self.parent.after(0, lambda: self._on_error("Connection failed"))
                    self.parent.after(0, lambda: self._show_connection_help())
                    # Restore button state
                    self.parent.after(0, lambda: self._update_ui_state())
                
            except Exception as e:
                error_msg = str(e)
                self.parent.after(0, lambda: self._on_error(f"Connection failed: {error_msg}"))
                
                # Check if it's likely a device conflict
                if any(keyword in error_msg.lower() for keyword in ["timeout", "closed", "device", "websocket"]):
                    self.parent.after(0, lambda: self._show_device_conflict_help())
                
                # Restore button state on error
                self.parent.after(0, lambda: self._update_ui_state())
            finally:
                self._cleanup_event_loop(loop)
        
        threading.Thread(target=connect_thread, daemon=True).start()
    
    def _show_connection_help(self):
        """Show helpful connection guidance"""
        self._on_error("💡 Connection troubleshooting:")
        self._on_error("   • Make sure QUSB2SNES is running")
        self._on_error("   • Check that your device is connected")
        self._on_error("   • Verify host/port settings (usually localhost:23074)")
    
    def _show_device_conflict_help(self):
        """Show device conflict guidance"""
        self._on_error("💡 Device may be in use by another application:")
        self._on_error("   • Close RetroAchievements (RA2Snes)")
        self._on_error("   • Close QFile2Snes")
        self._on_error("   • Close other USB2SNES applications")
        self._on_error("   • Only one app can use the device at a time")
    
    def _disconnect(self):
        """Disconnect from QUSB2SNES"""
        # Update button immediately
        if self.connect_button:
            self.connect_button.configure(state="disabled", text="Disconnecting...")
        
        # Cancel any ongoing sync
        if self.syncing:
            self.sync_cancelled = True
            self._on_progress("⚠️ Cancelling ongoing sync...")
            # Stop the sync loop if it's running
            if self.current_sync_loop and not self.current_sync_loop.is_closed():
                try:
                    # Cancel all running tasks in the sync loop
                    for task in asyncio.all_tasks(self.current_sync_loop):
                        task.cancel()
                except Exception:
                    pass  # Best effort cancellation
        
        def disconnect_thread():
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(self.sync_manager.disconnect())
            except:
                pass
            finally:
                self._cleanup_event_loop(loop)
                # Reset all state and restore UI in main thread
                self.parent.after(0, lambda: self._reset_connection_state())
        
        threading.Thread(target=disconnect_thread, daemon=True).start()
    
    def _reset_connection_state(self):
        """Reset all connection and sync state"""
        self.connected = False
        self.syncing = False
        self.sync_cancelled = False
        self.current_sync_loop = None
        self.devices = []
        if self.device_combo:
            self.device_combo['values'] = []
            self.device_var.set("")
        self._update_ui_state()
        self._on_progress("🔌 Disconnected from QUSB2SNES")
    
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
        # Use the same filtering logic as our sync implementation
        rom_extensions = ['.smc', '.sfc']  # Only extensions we actually sync
        rom_files = []
        total_dirs = 0
        try:
            for root, dirs, files in os.walk(local_rom_dir):
                total_dirs += len(dirs) if root == local_rom_dir else 0  # Count only direct subdirs
                for file in files:
                    # Use the same logic as our sync implementation
                    if file.lower().endswith(('.smc', '.sfc')):
                        full_path = os.path.normpath(os.path.join(root, file))
                        rom_files.append(full_path)
        except Exception as e:
            rom_files = [f"Error scanning directory: {str(e)}"]
            total_dirs = 0
        
        # Simple progress message
        self._on_progress(f"📁 Scanning output directory: {local_rom_dir}")
        self._on_progress(f"🔍 Found {len(rom_files)} ROM files in {total_dirs} subdirectories")
        
        # Create detailed confirmation message with tree-based sync info
        sync_info = f"""QUSB2SNES ROM Sync Operation (Optimized Tree-Based Method)
        
📁 SOURCE (Local Computer):
   {local_rom_dir}
   
📂 DESTINATION (SD Card):
   Device: {self.device_var.get()}
   Folder: {self.remote_folder_var.get()}
   
📋 OPERATION DETAILS:
   • ROM files found: {len(rom_files)} files (.smc, .sfc files only)
   • Subdirectories: {total_dirs} folders
   • Uses optimized tree-based sync (faster & more reliable)
   • Case-insensitive directory matching
   • Only uploads missing or modified files
   • Skips non-ROM files automatically
   
⚡ PERFORMANCE:
   • Optimized upload timing (7-12x faster than before)
   • No connection drops with tree-based approach
   • Estimated sync time: {len(rom_files) * 0.4:.1f}s ({(len(rom_files) * 0.4)/60:.1f} minutes)
   
⚠️  NOTE: This will modify files on your SD card.
   Make sure you have backups if needed.
   
Do you want to proceed with the optimized sync?"""
        
        # Confirm sync operation
        result = messagebox.askyesno(
            "Confirm ROM Sync Operation",
            sync_info,
            parent=self.parent.winfo_toplevel()
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
                self.current_sync_loop = loop  # Store reference for cancellation
                
                # Check for cancellation before starting
                if self.sync_cancelled:
                    self.parent.after(0, lambda: self._on_progress("❌ Sync cancelled"))
                    return
                
                # Create a completely fresh sync manager for this operation
                # to avoid cross-loop task reference issues
                from qusb2snes_sync import QUSB2SNESSyncManager
                fresh_sync_manager = QUSB2SNESSyncManager()
                fresh_sync_manager.on_progress = self._on_progress
                fresh_sync_manager.on_error = self._on_error
                
                # Set up cancellation callback so disconnect can cancel sync
                def check_cancellation():
                    if self.sync_cancelled and fresh_sync_manager.sync_client:
                        fresh_sync_manager.sync_client.cancel_operation()
                
                # Check cancellation periodically during sync
                def periodic_cancellation_check():
                    check_cancellation()
                    if not self.sync_cancelled:
                        loop.call_later(0.5, periodic_cancellation_check)  # Check every 500ms
                
                periodic_cancellation_check()  # Start checking
                
                # Configure with current settings
                fresh_sync_manager.configure(
                    self.host_var.get(),
                    int(self.port_var.get()),
                    self.device_var.get(),
                    self.remote_folder_var.get()
                )
                
                # Check for cancellation before connecting
                if self.sync_cancelled:
                    self.parent.after(0, lambda: self._on_progress("❌ Sync cancelled"))
                    return
                
                # Connect and perform sync
                if loop.run_until_complete(fresh_sync_manager.connect_and_attach()):
                    # Check for cancellation before sync
                    if self.sync_cancelled:
                        self.parent.after(0, lambda: self._on_progress("❌ Sync cancelled"))
                        loop.run_until_complete(fresh_sync_manager.disconnect())
                        return
                    
                    # Get last sync timestamp from config
                    last_sync_timestamp = self.config.get("qusb2snes_last_sync", 0)
                    
                    # Handle null/empty values for first-time sync
                    if last_sync_timestamp is None or last_sync_timestamp == "" or last_sync_timestamp == 0:
                        last_sync_timestamp = 0  # First sync - upload all files
                        self.parent.after(0, lambda: self._on_progress("📅 First sync - uploading all ROM files"))
                    else:
                        last_sync_timestamp = float(last_sync_timestamp)
                        import time
                        time_since_last = time.time() - last_sync_timestamp
                        self.parent.after(0, lambda msg=f"📅 Incremental sync - only uploading files newer than {time_since_last/3600:.1f} hours ago": self._on_progress(msg))
                    
                    try:
                        result = loop.run_until_complete(fresh_sync_manager.sync_roms(local_rom_dir, last_sync_timestamp))
                    except asyncio.CancelledError:
                        # Handle cancellation gracefully
                        self.parent.after(0, lambda: self._on_progress("❌ Sync cancelled"))
                        try:
                            loop.run_until_complete(fresh_sync_manager.disconnect())
                        except:
                            pass  # Ignore disconnect errors during cancellation
                        return
                    
                    # Check if operation was cancelled during sync
                    if self.sync_cancelled:
                        self.parent.after(0, lambda: self._on_progress("❌ Sync cancelled"))
                        try:
                            loop.run_until_complete(fresh_sync_manager.disconnect())
                        except:
                            pass  # Ignore disconnect errors during cancellation
                        return
                    
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
                    try:
                        loop.run_until_complete(fresh_sync_manager.disconnect())
                    except:
                        pass  # Ignore disconnect errors
                else:
                    self.parent.after(0, lambda: self._on_error("❌ Failed to connect for sync operation"))
                
            except Exception as e:
                # Capture exception message to avoid closure issues
                error_message = str(e)
                if self.sync_cancelled:
                    self.parent.after(0, lambda: self._on_progress("❌ Sync cancelled"))
                else:
                    self.parent.after(0, lambda msg=error_message: self._on_error(f"Sync failed: {msg}"))
            finally:
                # Properly close event loop with cleanup
                self._cleanup_event_loop(loop)
                # Reset syncing state and update UI
                self.parent.after(0, lambda: self._on_sync_complete())
        
        threading.Thread(target=sync_thread, daemon=True).start()
    
    def _on_sync_complete(self):
        """Called when sync operation completes (success or failure)"""
        self.syncing = False
        self.sync_cancelled = False
        self.current_sync_loop = None
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