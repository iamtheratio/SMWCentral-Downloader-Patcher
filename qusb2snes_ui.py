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
            text="Enable QUSB2SNES Sync",
            variable=self.enabled_var,
            command=self._on_enabled_changed
        )
        enable_cb.grid(row=0, column=0, columnspan=6, sticky="w", pady=(0, 10))
        
        # Connection settings row
        ttk.Label(self.frame, text="Host:").grid(row=1, column=0, sticky="w", padx=(0, 5))
        host_entry = ttk.Entry(self.frame, textvariable=self.host_var, width=15)
        host_entry.grid(row=1, column=1, padx=(0, 10))
        host_entry.bind('<KeyRelease>', self._on_setting_changed)
        
        ttk.Label(self.frame, text="Port:").grid(row=1, column=2, sticky="w", padx=(0, 5))
        port_entry = ttk.Entry(self.frame, textvariable=self.port_var, width=8)
        port_entry.grid(row=1, column=3, padx=(0, 10))
        port_entry.bind('<KeyRelease>', self._on_setting_changed)
        
        self.connect_button = ttk.Button(
            self.frame,
            text="Connect",
            command=self._on_connect_clicked
        )
        self.connect_button.grid(row=1, column=4, padx=(0, 10))
        
        # Device selection row
        ttk.Label(self.frame, text="Device:").grid(row=2, column=0, sticky="w", padx=(0, 5), pady=(5, 0))
        self.device_combo = ttk.Combobox(
            self.frame,
            textvariable=self.device_var,
            state="readonly",
            width=20
        )
        self.device_combo.grid(row=2, column=1, columnspan=2, sticky="ew", padx=(0, 10), pady=(5, 0))
        self.device_combo.bind('<<ComboboxSelected>>', self._on_device_changed)
        
        refresh_button = ttk.Button(
            self.frame,
            text="Refresh",
            command=self._on_refresh_clicked
        )
        refresh_button.grid(row=2, column=3, padx=(0, 10), pady=(5, 0))
        
        ttk.Label(self.frame, text="SD Card Folder:").grid(row=2, column=4, sticky="w", padx=(0, 5), pady=(5, 0))
        folder_entry = ttk.Entry(self.frame, textvariable=self.remote_folder_var, width=15)
        folder_entry.grid(row=2, column=5, pady=(5, 0))
        folder_entry.bind('<KeyRelease>', self._on_setting_changed)
        
        # Sync button row
        self.sync_button = ttk.Button(
            self.frame,
            text="Sync ROMs",
            command=self._on_sync_clicked
        )
        self.sync_button.grid(row=3, column=0, columnspan=6, pady=(10, 0))
        
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
        
        state = "normal" if enabled else "disabled"
        
        widgets = [
            self.connect_button, self.device_combo, self.sync_button
        ]
        
        for widget in widgets:
            if widget:
                widget.configure(state=state)
        
        # Update connect button text
        if self.connect_button:
            if self.connected:
                self.connect_button.configure(text="Disconnect")
            else:
                self.connect_button.configure(text="Connect")
    
    def _on_connect_clicked(self):
        """Handle connect/disconnect button click"""
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
                    
                    # Update UI in main thread
                    self.parent.after(0, lambda: self._update_devices(devices))
                
            except Exception as e:
                self.parent.after(0, lambda: self._on_error(f"Connection failed: {str(e)}"))
            finally:
                loop.close()
        
        threading.Thread(target=connect_thread, daemon=True).start()
    
    def _disconnect(self):
        """Disconnect from QUSB2SNES"""
        def disconnect_thread():
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(self.sync_manager.disconnect())
            except:
                pass
            finally:
                loop.close()
        
        threading.Thread(target=disconnect_thread, daemon=True).start()
    
    def _on_refresh_clicked(self):
        """Refresh device list"""
        if self.connected:
            self._connect()  # Reconnect to refresh devices
        else:
            self._on_error("Connect to QUSB2SNES first")
    
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
        
        # Confirm sync operation
        result = messagebox.askyesno(
            "Confirm Sync",
            f"Sync ROM files from:\n{local_rom_dir}\n\nTo:\n{self.remote_folder_var.get()}\n\nContinue?"
        )
        
        if not result:
            return
        
        # Start sync in background thread
        def sync_thread():
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                # Attach to selected device first
                success = loop.run_until_complete(
                    self.sync_manager.sync_client.attach_device(self.device_var.get())
                )
                
                if success:
                    # Start sync
                    loop.run_until_complete(self.sync_manager.sync_roms(local_rom_dir))
                else:
                    self.parent.after(0, lambda: self._on_error("Failed to attach to device"))
                
            except Exception as e:
                self.parent.after(0, lambda: self._on_error(f"Sync failed: {str(e)}"))
            finally:
                loop.close()
        
        threading.Thread(target=sync_thread, daemon=True).start()
    
    def _update_devices(self, devices):
        """Update device list in UI thread"""
        self.devices = devices
        if self.device_combo:
            self.device_combo['values'] = devices
            if devices and not self.device_var.get():
                self.device_var.set(devices[0])
                self._on_device_changed()
    
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
    
    def _on_disconnected(self):
        """Handle disconnection"""
        self.connected = False
        self.devices = []
        if self.device_combo:
            self.device_combo['values'] = []
        self._update_ui_state()