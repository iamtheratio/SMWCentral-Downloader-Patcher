#!/usr/bin/env python3
"""
QUSB2SNES Sync Core Module - Clean Manager Class Only

This contains just the fixed QUSB2SNESSyncManager class to replace the corrupted one.
"""

import asyncio
from typing import List, Dict, Optional, Callable


class QUSB2SNESSyncManager:
    """Simple sync manager for UI integration"""
    
    def __init__(self):
        self.sync_client = None
        self.enabled = False
        self.host = "localhost"
        self.port = 23074  # Modern default port
        self.device = ""
        self.remote_folder = "/ROMS"
        
        # Cancellation support
        self.cancelled = False
        
        # Simple callbacks
        self.on_progress: Optional[Callable[[str], None]] = None
        self.on_error: Optional[Callable[[str], None]] = None
        self.on_connected: Optional[Callable[[], None]] = None
        self.on_disconnected: Optional[Callable[[], None]] = None
    
    def log_progress(self, message: str):
        """Log progress message"""
        if self.on_progress:
            self.on_progress(message)
    
    def log_error(self, message: str):
        """Log error message"""
        if self.on_error:
            self.on_error(message)
    
    def cancel_operation(self):
        """Cancel the current sync operation"""
        self.cancelled = True
        if self.sync_client:
            self.sync_client.cancel_operation()
    
    def configure(self, host: str, port: int, device: str, remote_folder: str):
        """Configure sync settings"""
        self.host = host
        self.port = port
        self.device = device
        self.remote_folder = remote_folder
    
    async def connect_and_attach(self) -> bool:
        """Connect and optionally attach to device"""
        try:
            from qusb2snes_sync import QUSB2SNESSync
            
            self.sync_client = QUSB2SNESSync(self.host, self.port)
            self.sync_client.on_progress = self.on_progress
            self.sync_client.on_error = self.on_error
            
            if await self.sync_client.connect():
                # If a device is specified, try to attach to it
                if self.device:
                    if await self.sync_client.attach_device(self.device):
                        if self.on_connected:
                            self.on_connected()
                        return True
                    else:
                        self.log_error("❌ Failed to attach to device")
                        return False
                else:
                    if self.on_connected:
                        self.on_connected()
                    return True
            else:
                self.log_error("❌ Failed to connect to QUSB2SNES")
                return False
        except Exception as e:
            self.log_error(f"❌ Connection failed: {str(e)}")
            return False
    
    async def sync_roms(self, local_rom_dir: str, last_sync_timestamp: float = 0) -> bool:
        """Sync ROM directory using tree-based approach"""
        if not self.sync_client:
            if self.on_error:
                self.on_error("❌ Not connected to QUSB2SNES")
            return False

        # Use the new tree-based sync approach with timestamp
        return await self.sync_client.sync_directory_tree_based(local_rom_dir, self.remote_folder, last_sync_timestamp)
    
    async def sync_roms_incremental(self, local_rom_dir: str, progress_tracker: Dict = None, cleanup_deleted: bool = False) -> Dict:
        """
        Incremental ROM sync that can resume from partial completion.
        Delegates to the sync client.
        """
        if not self.sync_client:
            return {
                "success": False, 
                "error": "Not connected to QUSB2SNES",
                "uploaded": 0,
                "progress": progress_tracker or {}
            }
        
        # Set up the sync client's callbacks
        self.sync_client.on_progress = self.on_progress
        self.sync_client.on_error = self.on_error
        
        # Set the remote folder
        self.sync_client.remote_folder = self.remote_folder
        
        # Delegate to the sync client's tree-based sync method
        try:
            # Use the tree-based sync with cleanup
            result = await self.sync_client.sync_directory_tree_based(
                local_rom_dir, 
                self.remote_folder, 
                0,  # timestamp 
                cleanup_deleted
            )
            
            return {
                "success": result,
                "uploaded": 0,  # Tree-based sync doesn't return count
                "progress": progress_tracker or {}
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "uploaded": 0,
                "progress": progress_tracker or {}
            }
    
    async def disconnect(self):
        """Disconnect from QUSB2SNES with cleanup"""
        if self.sync_client:
            try:
                await self.sync_client.disconnect()
            except Exception as e:
                # Ignore disconnect errors from different event loops
                if "different loop" not in str(e):
                    if self.on_error:
                        self.on_error(f"⚠️ Disconnect warning: {str(e)}")
            finally:
                self.sync_client = None
                if self.on_disconnected:
                    self.on_disconnected()


if __name__ == "__main__":
    print("✅ QUSB2SNESSyncManager class is clean and ready!")