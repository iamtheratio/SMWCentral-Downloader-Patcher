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

# Import V2 adapter with backward compatibility wrapper
from qusb2snes_upload_v2_adapter import QUSB2SNESUploadManager
from ui_constants import get_labelframe_padding

# Compatibility wrapper for V1 UI interface using V2/V3 implementation
class QUSB2SNESSyncManager:
    """Compatibility wrapper for V1 UI interface using V2/V3 implementation"""
    
    def __init__(self, config_manager=None, logging_system=None):
        # Import config manager if not provided
        if config_manager is None:
            try:
                from config_manager import ConfigManager
                config_manager = ConfigManager()
            except ImportError:
                config_manager = None
        
        self.upload_manager = QUSB2SNESUploadManager(config_manager=config_manager, logging_system=logging_system)
        self.host = "localhost" 
        self.port = 8080
        self.device_name = ""
        self.config_manager = config_manager
        self.logging_system = logging_system
        
        # Callback attributes for compatibility
        self.on_progress = None
        self.on_error = None
        self.on_connected = None
        self.on_disconnected = None
        
    def configure(self, host, port, device, remote_folder=None):
        """Configure connection settings"""
        self.host = host
        self.port = port
        self.device_name = device
        self.remote_folder = remote_folder or "/roms"
        
    async def connect_and_attach(self):
        """Connect and attach to device"""
        try:
            # Use V3 manager to connect  
            success = await self.upload_manager.v3_manager.connect()
            if success and self.on_connected:
                self.on_connected()
            return success
        except Exception as e:
            if self.on_error:
                self.on_error(f"Connection failed: {e}")
            return False
            
    async def get_devices(self):
        """Get available devices"""
        try:
            # Create a temporary connection just to get device list
            import websockets
            import json
            
            websocket = await websockets.connect("ws://localhost:23074")
            
            # Send DeviceList command
            cmd = {"Opcode": "DeviceList", "Space": "SNES"}
            await websocket.send(json.dumps(cmd))
            response = await websocket.recv()
            devices = json.loads(response).get("Results", [])
            
            await websocket.close()
            return devices or []
        except Exception as e:
            if self.on_error:
                self.on_error(f"Failed to get devices: {e}")
            return []
            
    async def disconnect(self):
        """Disconnect from device"""
        try:
            await self.upload_manager.v3_manager.disconnect()
            if self.on_disconnected:
                self.on_disconnected()
        except Exception as e:
            if self.on_error:
                self.on_error(f"Disconnect failed: {e}")
                
    async def sync_hacks_to_remote(self, remote_folder):
        """Sync ROMs to remote folder - compatibility method"""
        try:
            # Use the V2 adapter's sync_from_config method with timestamp filter
            if self.on_progress:
                self.on_progress("Starting sync...")
            
            # Create a file filter that checks qusb_last_sync timestamps and file existence
            file_filter = self._create_timestamp_filter(self.upload_manager.v3_manager)
            
            result = await self.upload_manager.v3_manager.sync_from_config(file_filter)
            
            if result:
                # Update qusb_last_sync timestamps after successful sync
                updated_hacks = []
                try:
                    updated_hacks = await self._update_sync_timestamps()
                except Exception as timestamp_error:
                    # Don't fail the sync if timestamp update fails
                    error_message = f"Warning: Failed to update timestamps: {timestamp_error}"
                    if self.logging_system:
                        self.logging_system.log(error_message, "Warning")
                    else:
                        print(error_message)
                    if self.on_progress:
                        self.on_progress("⚠️ Sync completed but timestamp update failed")
                
                if self.on_progress:
                    self.on_progress("✅ Sync completed successfully")
                
                # Return a proper result dictionary for UI compatibility
                return {
                    "success": True,
                    "uploaded": len(updated_hacks),
                    "updated_hacks": updated_hacks,
                    "error": None
                }
            else:
                if self.on_progress:
                    self.on_progress("❌ Sync failed")
                
                # Return failure result dictionary
                return {
                    "success": False,
                    "uploaded": 0,
                    "updated_hacks": [],
                    "error": "Sync operation failed"
                }
            
        except Exception as e:
            if self.on_error:
                self.on_error(f"Sync failed: {e}")
            
            # Return failure result dictionary
            return {
                "success": False,
                "uploaded": 0,
                "updated_hacks": [],
                "error": str(e)
            }
    
    def _create_timestamp_filter(self, v3_manager=None):
        """Create a file filter that checks qusb_last_sync timestamps and file existence"""
        try:
            import json
            import time
            from utils import PROCESSED_JSON_PATH
            
            # Load processed.json data
            processed_data = {}
            if os.path.exists(PROCESSED_JSON_PATH):
                with open(PROCESSED_JSON_PATH, 'r', encoding='utf-8') as f:
                    processed_data = json.load(f)
            
            def should_sync_file(file_path: str) -> bool:
                """Check if file should be synced based on file existence and timestamps"""
                try:
                    # Get file info
                    filename = os.path.basename(file_path)
                    name_without_ext = os.path.splitext(filename)[0].lower()
                    
                    if not os.path.exists(file_path):
                        return False
                    
                    # Check if file exists on SD card first
                    if v3_manager:
                        # Get the target path on SD card based on current sync folder
                        remote_folder = getattr(self, 'remote_folder', '/roms')
                        if not remote_folder.startswith('/'):
                            remote_folder = '/' + remote_folder
                        if not remote_folder.endswith('/'):
                            remote_folder += '/'
                        
                        sd_card_path = f"{remote_folder}{filename}"
                        
                        # Check if file exists on SD card
                        file_exists_on_sd = sd_card_path in v3_manager.existing_files
                        
                        if not file_exists_on_sd:
                            if self.logging_system:
                                self.logging_system.log(f"📤 Will sync: {filename} (missing from SD card location)", "Information")
                            return True
                    
                    local_mtime = int(os.path.getmtime(file_path))
                    
                    # Find matching hack in processed.json
                    matching_hack_data = None
                    for hack_data in processed_data.values():
                        if hack_data.get("obsolete", False):
                            continue
                        
                        hack_title = hack_data.get("title", "").lower()
                        if hack_title and (hack_title in name_without_ext or name_without_ext in hack_title):
                            matching_hack_data = hack_data
                            break
                    
                    if matching_hack_data:
                        # Check timestamp
                        qusb_last_sync = matching_hack_data.get("qusb_last_sync", 0)
                        
                        if qusb_last_sync == 0:
                            if self.logging_system:
                                self.logging_system.log(f"📤 Will sync: {filename} (never synced)", "Information")
                            return True
                        elif qusb_last_sync < local_mtime:
                            if self.logging_system:
                                self.logging_system.log(f"📤 Will sync: {filename} (file modified since last sync)", "Information")
                            return True
                        else:
                            if self.logging_system:
                                self.logging_system.log(f"⏭️ Skipping: {filename} (already up to date)", "Information")
                            return False
                    else:
                        # File not in processed.json - always sync
                        if self.logging_system:
                            self.logging_system.log(f"📤 Will sync: {filename} (not in processed.json)", "Information")
                        return True
                        
                except Exception as e:
                    if self.logging_system:
                        self.logging_system.log(f"Warning: Error checking timestamp for {file_path}: {e}", "Warning")
                    return True  # Default to syncing if we can't check
            
            return should_sync_file
            
        except Exception as e:
            print(f"Warning: Failed to create timestamp filter: {e}")
            # Return a filter that syncs everything if we can't create proper filter
            return lambda x: True
    
    async def _update_sync_timestamps(self):
        """Update qusb_last_sync timestamps for hacks that were actually uploaded"""
        updated_hacks = []  # Track updated hack titles
        try:
            import time
            import glob
            from hack_data_manager import HackDataManager
            from utils import PROCESSED_JSON_PATH
            
            # Initialize hack data manager
            hack_manager = HackDataManager()
            
            # Get current timestamp
            current_timestamp = int(time.time())
            
            # Get the output directory from config
            output_dir = self.config_manager.get("output_dir", "")
            if not output_dir or not os.path.exists(output_dir):
                if self.on_progress:
                    self.on_progress("⚠️ Output directory not found, skipping timestamp updates")
                return updated_hacks
            
            # Find all ROM files in output directory
            rom_extensions = ["*.smc", "*.sfc", "*.fig"]
            uploaded_files = []
            
            for ext in rom_extensions:
                pattern = os.path.join(output_dir, "**", ext)
                files = glob.glob(pattern, recursive=True)
                uploaded_files.extend(files)
            
            if not uploaded_files:
                if self.on_progress:
                    self.on_progress("📁 No ROM files found in output directory")
                return updated_hacks
            
            # Extract filenames without extensions for matching
            uploaded_filenames = set()
            for file_path in uploaded_files:
                filename = os.path.basename(file_path)
                name_without_ext = os.path.splitext(filename)[0]
                uploaded_filenames.add(name_without_ext.lower())  # Case-insensitive matching
            
            # Load processed.json to find matching hacks
            if not os.path.exists(PROCESSED_JSON_PATH):
                return updated_hacks
                
            import json
            with open(PROCESSED_JSON_PATH, 'r', encoding='utf-8') as f:
                processed_data = json.load(f)
            
            # Update timestamp for matching non-obsolete hacks
            updated_count = 0
            for hack_id, hack_data in processed_data.items():
                # Skip obsolete hacks
                if hack_data.get("obsolete", False):
                    continue
                
                # Get hack title for matching
                hack_title = hack_data.get("title", "").lower()
                if not hack_title:
                    continue
                
                # Check if this hack matches any uploaded file
                title_matched = False
                for uploaded_name in uploaded_filenames:
                    # Match if hack title is contained in filename or vice versa
                    if (hack_title in uploaded_name) or (uploaded_name in hack_title):
                        title_matched = True
                        break
                
                if title_matched:
                    # Update the timestamp for this hack
                    success = hack_manager.update_hack(hack_id, "qusb_last_sync", current_timestamp)
                    if success:
                        updated_count += 1
                        hack_name = hack_data.get('title', hack_id)
                        updated_hacks.append(hack_name)
                        
                        # Use logging system if available, otherwise print
                        log_message = f"📝 Updated timestamp for hack: {hack_name}"
                        if self.logging_system:
                            self.logging_system.log(log_message, "Information")
                        else:
                            print(log_message)
            
            if self.on_progress:
                self.on_progress(f"📝 Updated sync timestamps for {updated_count} uploaded hacks")
                
        except Exception as e:
            # Log error but don't fail the sync operation
            error_message = f"Warning: Failed to update sync timestamps: {e}"
            if self.logging_system:
                self.logging_system.log(error_message, "Warning")
            else:
                print(error_message)
            import traceback
            traceback.print_exc()
        
        return updated_hacks
            
    # Additional compatibility properties
    @property  
    def sync_client(self):
        """Return a mock sync client for compatibility"""
        class MockSyncClient:
            def cancel_operation(self):
                pass
        return MockSyncClient()


class QUSB2SNESSection:
    """Simple QUSB2SNES settings section"""
    
    def __init__(self, parent, config_manager, logger):
        self.parent = parent
        self.config = config_manager
        self.logger = logger
        
        # Recreate upload manager with correct logger
        self.upload_manager = QUSB2SNESUploadManager(config_manager=config_manager, logging_system=self.logger)
        
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
        self.sync_manager = QUSB2SNESSyncManager(config_manager=self.config, logging_system=self.logger)
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
        self.port_var = tk.IntVar(value=self.config.get("qusb2snes_port", 23074))  # Modern default port
        self.device_var = tk.StringVar(value=self.config.get("qusb2snes_device", ""))
        self.remote_folder_var = tk.StringVar(value=self.config.get("qusb2snes_remote_folder", "/ROMS"))
        
        # Row 0: Enable checkbox and labels
        enable_cb = ttk.Checkbutton(
            self.frame, 
            text="Enable",
            variable=self.enabled_var,
            command=self._on_enabled_changed
        )
        enable_cb.grid(row=0, column=0, sticky="nw", padx=(0, 30), pady=(5, 2))
        
        # Labels above their respective controls with increased spacing between groups
        ttk.Label(self.frame, text="Host:").grid(row=0, column=1, sticky="w", padx=(0, 5), pady=(5, 2))
        ttk.Label(self.frame, text="Port:").grid(row=0, column=2, sticky="w", padx=(5, 30), pady=(5, 2))  # Extra space after Port
        ttk.Label(self.frame, text="Device:").grid(row=0, column=3, sticky="w", padx=(0, 30), pady=(5, 2))  # Extra space after Device
        ttk.Label(self.frame, text="Sync To Folder:").grid(row=0, column=4, sticky="w", padx=(0, 5), pady=(5, 2))
        
        # Row 1: Input Controls (under their labels) with wider fields
        self.host_entry = ttk.Entry(self.frame, textvariable=self.host_var, width=15)  # Increased from 10
        self.host_entry.grid(row=1, column=1, sticky="ew", padx=(0, 5), pady=(0, 5))
        self.host_entry.bind('<KeyRelease>', self._on_setting_changed)
        
        self.port_entry = ttk.Entry(self.frame, textvariable=self.port_var, width=6)
        self.port_entry.grid(row=1, column=2, sticky="ew", padx=(5, 30), pady=(0, 5))  # Extra space after Port
        self.port_entry.bind('<KeyRelease>', self._on_setting_changed)
        
        self.device_combo = ttk.Combobox(
            self.frame,
            textvariable=self.device_var,
            state="readonly",
            width=20  # Increased from 15
        )
        self.device_combo.grid(row=1, column=3, sticky="ew", padx=(0, 30), pady=(0, 5))  # Extra space after Device
        self.device_combo.bind('<<ComboboxSelected>>', self._on_device_changed)
        
        # Much wider Sync To Folder field to match mockup
        self.folder_entry = ttk.Entry(self.frame, textvariable=self.remote_folder_var, width=35)
        self.folder_entry.grid(row=1, column=4, columnspan=2, sticky="ew", padx=(0, 5), pady=(0, 5))
        self.folder_entry.bind('<KeyRelease>', self._on_setting_changed)
        
        # Row 2: Action Buttons with consistent fixed width, left alignment, and increased spacing
        self.connect_button = ttk.Button(
            self.frame,
            text="Connect",
            command=self._on_connect_clicked,
            width=12
        )
        self.connect_button.grid(row=2, column=1, columnspan=2, sticky="w", padx=(0, 30), pady=(10, 5))  # Extra space after Connect
        
        self.refresh_button = ttk.Button(
            self.frame,
            text="Refresh",
            command=self._on_refresh_clicked,
            width=12
        )
        self.refresh_button.grid(row=2, column=3, sticky="w", padx=(0, 30), pady=(10, 5))  # Extra space after Refresh
        
        self.sync_button = ttk.Button(
            self.frame,
            text="Sync",
            command=self._on_sync_clicked,
            width=12
        )
        self.sync_button.grid(row=2, column=4, columnspan=2, sticky="w", padx=(0, 5), pady=(10, 5))
        
        # Row 3: Cleanup option checkbox
        self.cleanup_var = tk.BooleanVar(value=self.config.get("qusb2snes_cleanup_deleted", False))
        self.cleanup_checkbox = ttk.Checkbutton(
            self.frame,
            text="Remove deleted files from SD card during sync",
            variable=self.cleanup_var,
            command=self._on_cleanup_changed
        )
        self.cleanup_checkbox.grid(row=3, column=1, columnspan=5, sticky="w", padx=(0, 5), pady=(5, 10))
        
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
    
    def _on_cleanup_changed(self):
        """Handle cleanup option change"""
        self.config.set("qusb2snes_cleanup_deleted", self.cleanup_var.get())
        self.config.save()
    
    def _update_ui_state(self):
        """Update UI component states"""
        enabled = self.enabled_var.get()
        
        # Basic widgets that follow the enabled state
        basic_widgets = [
            self.host_entry,
            self.port_entry, 
            self.device_combo,
            self.folder_entry,
            self.cleanup_checkbox
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
        self._on_progress(f"📁 Scanning ROM directory...")
        self._on_progress(f"🔍 Found {len(rom_files)} ROM files")
        
        # Create simple confirmation message
        cleanup_enabled = self.config.get("qusb2snes_cleanup_deleted", False)
        
        sync_info = f"""Sync {len(rom_files)} ROM files to SD card?

📁 From: {os.path.basename(local_rom_dir)}
📂 To: {self.device_var.get()} - {self.remote_folder_var.get()}

⚠️ This will modify files on your SD card."""

        if cleanup_enabled:
            sync_info += "\n🗑️ Deleted files will be removed from SD card."
        
        # Confirm sync operation
        result = messagebox.askyesno(
            "Sync ROMs to SD Card",
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
                
                # Set up cancellation callback 
                def check_cancellation():
                    if self.sync_cancelled and sync_manager.sync_client:
                        sync_manager.sync_client.cancel_operation()
                
                # Check cancellation periodically during sync
                def periodic_cancellation_check():
                    check_cancellation()
                    if not self.sync_cancelled:
                        loop.call_later(0.5, periodic_cancellation_check)  # Check every 500ms
                
                periodic_cancellation_check()  # Start checking
                
                # Check for cancellation before sync
                if self.sync_cancelled:
                    self.parent.after(0, lambda: self._on_progress("❌ Sync cancelled"))
                    return
                
                # Use a fresh sync manager for this operation to avoid cross-loop issues
                # (the UI sync_manager belongs to the main thread's event loop)
                sync_manager = QUSB2SNESSyncManager(config_manager=self.config, logging_system=self.logger)
                sync_manager.on_progress = self._on_progress
                sync_manager.on_error = self._on_error
                
                # Configure with current settings
                sync_manager.configure(
                    self.host_var.get(),
                    int(self.port_var.get()),
                    self.device_var.get(),
                    self.remote_folder_var.get()
                )
                
                # Connect for sync (no UI disconnect needed)
                self.parent.after(0, lambda: self._on_progress("🔗 Connecting for sync..."))
                if not loop.run_until_complete(sync_manager.connect_and_attach()):
                    self.parent.after(0, lambda: self._on_error("❌ Failed to connect for sync"))
                    return
                
                self.parent.after(0, lambda: self._on_progress("🚀 Starting sync operation..."))
                
                # Check for cancellation before sync
                if self.sync_cancelled:
                    self.parent.after(0, lambda: self._on_progress("❌ Sync cancelled"))
                    return
                
                # Get sync progress from config
                last_sync_timestamp = self.config.get("qusb2snes_last_sync", 0)
                progress_tracker = self.config.get("qusb2snes_sync_progress", {})
                is_partial_sync = self.config.get("qusb2snes_partial_sync", False)
                cleanup_deleted = self.config.get("qusb2snes_cleanup_deleted", False)
                    
                
                # Handle null/empty values for first-time sync
                if last_sync_timestamp is None or last_sync_timestamp == "" or last_sync_timestamp == 0:
                    last_sync_timestamp = 0  # First sync - upload all files
                    progress_tracker = {}
                    is_partial_sync = False
                    self.parent.after(0, lambda: self._on_progress("📅 First sync - uploading all ROM files"))
                else:
                    last_sync_timestamp = float(last_sync_timestamp)
                    if is_partial_sync:
                        self.parent.after(0, lambda: self._on_progress("🔄 Resuming partial sync from last progress"))
                    else:
                        import time
                        time_since_last = time.time() - last_sync_timestamp
                        self.parent.after(0, lambda msg=f"📅 Incremental sync - checking files newer than {time_since_last/3600:.1f} hours ago": self._on_progress(msg))
                
                try:
                    # Use new per-hack sync method instead of filesystem-based sync
                    self.parent.after(0, lambda: self._on_progress("🔄 Using per-hack tracking for precise sync control"))
                    result = loop.run_until_complete(sync_manager.sync_hacks_to_remote(self.remote_folder_var.get()))
                except asyncio.CancelledError:
                    # Handle cancellation gracefully - individual hack timestamps already saved
                    self.parent.after(0, lambda: self._on_progress("❌ Sync cancelled - progress preserved per hack"))
                    return
                
                # Check if operation was cancelled during sync
                if self.sync_cancelled:
                    self.parent.after(0, lambda: self._on_progress("❌ Sync cancelled - progress preserved per hack"))
                    return
                
                if result and result.get("success"):
                    # Per-hack tracking - no global timestamp needed
                    # Individual hack timestamps are already updated by sync_hacks_to_remote
                    
                    uploaded_count = result.get("uploaded", 0)
                    updated_hacks = result.get("updated_hacks", [])
                    
                    if uploaded_count > 0:
                        self.parent.after(0, lambda: self._on_progress(f"✅ Sync complete: {uploaded_count} files uploaded, {len(updated_hacks)} hacks updated"))
                    else:
                        self.parent.after(0, lambda: self._on_progress(f"✅ Sync complete: All hacks up to date"))
                else:
                    # Handle sync failure - individual hack timestamps preserve progress
                    error_msg = result.get("error", "Unknown error") if result else "Unknown error"
                    uploaded_count = result.get("uploaded", 0) if result else 0
                    
                    if uploaded_count > 0:
                        self.parent.after(0, lambda msg=error_msg, count=uploaded_count: self._on_error(f"❌ Sync partially failed: {msg} ({count} hacks successfully synced before failure)"))
                    else:
                        self.parent.after(0, lambda msg=error_msg: self._on_error(f"❌ Sync failed: {msg}"))
                
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