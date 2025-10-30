#!/usr/bin/env python3
"""
QUSB2SNES Sync Core Module - Simple Implementation
Implements basic QUSB2SNES sync functionality validated by tests

Copyright (c) 2025 iamtheratio
Licensed under the MIT License - see LICENSE file for details
"""

import asyncio
import json
import os
import time
from typing import List, Dict, Optional, Callable

try:
    import websockets
except ImportError:
    print("❌ Missing websockets library. Install with: pip install websockets")
    raise


class QUSB2SNESSync:
    """Simple QUSB2SNES sync implementation"""
    
    def __init__(self, host: str = "localhost", port: int = 23074):
        self.host = host
        self.port = port
        self.websocket = None
        self.connected = False
        self.app_name = "SMWCentral Downloader"
        
        # Simple callbacks
        self.on_progress: Optional[Callable[[str], None]] = None
        self.on_error: Optional[Callable[[str], None]] = None
    
    def log_progress(self, message: str):
        """Simple progress logging"""
        if self.on_progress:
            self.on_progress(message)
    
    def log_error(self, message: str):
        """Simple error logging"""
        if self.on_error:
            self.on_error(message)
    
    async def connect(self) -> bool:
        """Connect to QUSB2SNES server"""
        try:
            uri = f"ws://{self.host}:{self.port}"
            self.log_progress(f"🔗 Connecting to QUSB2SNES at {uri}")
            
            self.websocket = await asyncio.wait_for(
                websockets.connect(uri), 
                timeout=5.0
            )
            self.connected = True
            
            # Identify app and wait for it to process
            name_cmd = {"Opcode": "Name", "Operands": [self.app_name]}
            await self.websocket.send(json.dumps(name_cmd))
            await asyncio.sleep(0.5)  # Give server time to process app identification
            
            self.log_progress("✅ Connected to QUSB2SNES")
            return True
            
        except Exception as e:
            self.log_error(f"❌ Connection failed: {str(e)}")
            return False
    
    async def disconnect(self):
        """Disconnect from QUSB2SNES"""
        if self.websocket and self.connected:
            try:
                await self.websocket.close()
                self.log_progress("✅ Disconnected from QUSB2SNES")
            except:
                pass
        
        self.connected = False
        self.websocket = None
    
    async def get_devices(self) -> List[str]:
        """Get list of available devices"""
        try:
            response = await self._send_command("DeviceList")
            if response and "Results" in response:
                return response["Results"]
            return []
        except Exception as e:
            self.log_error(f"❌ Failed to get devices: {str(e)}")
            return []
    
    async def attach_device(self, device_name: str) -> bool:
        """Attach to specific device"""
        try:
            self.log_progress(f"📱 Attaching to device: {device_name}")
            await self._send_command("Attach", operands=[device_name])
            await asyncio.sleep(2.0)
            
            # Verify attachment
            info_response = await self._send_command("Info")
            if info_response and info_response.get("Results"):
                self.log_progress("✅ Device attached successfully")
                return True
            
            self.log_error("❌ Device attachment verification failed")
            return False
            
        except Exception as e:
            self.log_error(f"❌ Device attachment failed: {str(e)}")
            return False
    
    async def list_directory(self, path: str) -> List[Dict]:
        """List remote directory contents"""
        try:
            response = await self._send_command("List", operands=[path])
            if not response or "Results" not in response:
                return []
            
            results = response["Results"]
            items = []
            
            for i in range(0, len(results), 2):
                if i + 1 < len(results):
                    item_type = results[i]
                    item_name = results[i + 1]
                    
                    if item_name not in [".", ".."]:
                        items.append({
                            "name": item_name,
                            "is_dir": item_type == "0"
                        })
            
            return items
            
        except Exception as e:
            self.log_error(f"❌ Failed to list directory {path}: {str(e)}")
            return []
    
    async def create_directory(self, path: str) -> bool:
        """Create remote directory"""
        try:
            await self._send_command("MakeDir", operands=[path])
            await asyncio.sleep(0.5)
            return True
        except Exception as e:
            self.log_error(f"❌ Failed to create directory {path}: {str(e)}")
            return False
    
    async def upload_file(self, local_path: str, remote_path: str) -> bool:
        """Upload file to remote location"""
        try:
            if not os.path.exists(local_path):
                self.log_error(f"❌ Local file not found: {local_path}")
                return False
            
            file_size = os.path.getsize(local_path)
            self.log_progress(f"📤 Uploading {os.path.basename(local_path)} ({file_size} bytes)")
            
            # Send PutFile command with proper error handling
            size_hex = format(file_size, 'X')
            response = await self._send_command("PutFile", operands=[remote_path, size_hex])
            
            # If command failed, don't proceed with file data
            if response is None:
                self.log_error(f"❌ PutFile command failed for {remote_path}")
                return False
            
            await asyncio.sleep(0.2)
            
            # Send file data
            with open(local_path, "rb") as f:
                data = f.read()
                await self.websocket.send(data)
            
            await asyncio.sleep(0.5)
            self.log_progress(f"✅ Uploaded {os.path.basename(local_path)}")
            return True
            
        except Exception as e:
            self.log_error(f"❌ Upload failed for {local_path}: {str(e)}")
            return False
    
    def is_safe_remote_path(self, path: str) -> bool:
        """Check if remote path is safe for operations"""
        path = path.lower().strip()
        
        forbidden = [
            "/", "/sd2snes", "/saves", "/system", 
            "/firmware", "/boot", "/kernel"
        ]
        
        for forbidden_path in forbidden:
            if path == forbidden_path or path.startswith(forbidden_path + "/"):
                return False
        
        return True
    
    async def sync_directory(self, local_dir: str, remote_dir: str) -> bool:
        """Simple directory sync implementation"""
        try:
            # Safety check
            if not self.is_safe_remote_path(remote_dir):
                self.log_error(f"❌ Remote path not safe: {remote_dir}")
                return False
            
            if not os.path.exists(local_dir):
                self.log_error(f"❌ Local directory not found: {local_dir}")
                return False
            
            self.log_progress(f"🔄 Starting sync: {local_dir} → {remote_dir}")
            
            # Check if remote directory exists, create only if needed
            try:
                remote_items = await self.list_directory(remote_dir)
                self.log_progress(f"📁 Remote directory exists with {len(remote_items)} items")
            except Exception:
                # Directory doesn't exist, create it
                self.log_progress(f"📁 Creating remote directory: {remote_dir}")
                await self.create_directory(remote_dir)
                remote_items = await self.list_directory(remote_dir)
            
            remote_names = {item["name"] for item in remote_items}
            
            # Sync files from local directory
            uploaded = 0
            for item in os.listdir(local_dir):
                # Check connection health before each operation
                if not self.connected or (self.websocket and self.websocket.closed):
                    self.log_error("❌ Connection lost during sync, stopping")
                    break
                    
                local_path = os.path.join(local_dir, item)
                
                if os.path.isfile(local_path):
                    if item not in remote_names:
                        remote_path = f"{remote_dir.rstrip('/')}/{item}"
                        if await self.upload_file(local_path, remote_path):
                            uploaded += 1
                elif os.path.isdir(local_path):
                    # Simple subdirectory sync
                    sub_remote_dir = f"{remote_dir.rstrip('/')}/{item}"
                    
                    # Check if subdirectory exists, create only if needed
                    try:
                        await self.list_directory(sub_remote_dir)
                        self.log_progress(f"📁 Subdirectory exists: {sub_remote_dir}")
                    except Exception:
                        # Subdirectory doesn't exist, create it
                        self.log_progress(f"📁 Creating subdirectory: {sub_remote_dir}")
                        await self.create_directory(sub_remote_dir)
                    
                    # Sync files in subdirectory
                    for sub_item in os.listdir(local_path):
                        sub_local_path = os.path.join(local_path, sub_item)
                        if os.path.isfile(sub_local_path):
                            sub_remote_path = f"{sub_remote_dir}/{sub_item}"
                            if await self.upload_file(sub_local_path, sub_remote_path):
                                uploaded += 1
            
            self.log_progress(f"✅ Sync completed - {uploaded} files uploaded")
            return True
            
        except Exception as e:
            self.log_error(f"❌ Sync failed: {str(e)}")
            return False
    
    async def _send_command(self, opcode: str, space: str = "SNES", operands: List[str] = None) -> Optional[Dict]:
        """Send command to QUSB2SNES with connection health checking"""
        if not self.connected or not self.websocket:
            raise Exception("Not connected to QUSB2SNES")
        
        # Check if websocket is still open
        if self.websocket.closed:
            self.log_error("❌ WebSocket connection closed, cannot send command")
            self.connected = False
            return None
        
        try:
            command = {"Opcode": opcode, "Space": space}
            if operands:
                command["Operands"] = operands
            
            await self.websocket.send(json.dumps(command))
            
            # Commands that don't send replies
            no_reply_commands = ["Attach", "Name", "MakeDir", "PutFile", "Remove"]
            
            if opcode in no_reply_commands:
                return {"status": "ok"}  # Return success indicator for no-reply commands
            
            # Wait for response
            try:
                response = await asyncio.wait_for(self.websocket.recv(), timeout=10.0)
                return json.loads(response)
            except asyncio.TimeoutError:
                self.log_error("❌ Command timeout")
                return None
                
        except Exception as e:
            # If websocket error, mark as disconnected
            if "1000" in str(e) or "websocket" in str(e).lower():
                self.connected = False
                self.websocket = None
            raise e


# Simple sync manager for UI integration
class QUSB2SNESSyncManager:
    """Simple sync manager for UI integration"""
    
    def __init__(self):
        self.sync_client = None
        self.enabled = False
        self.host = "localhost"
        self.port = 23074
        self.device = ""
        self.remote_folder = "/ROMS"
        
        # Simple callbacks
        self.on_progress: Optional[Callable[[str], None]] = None
        self.on_error: Optional[Callable[[str], None]] = None
        self.on_connected: Optional[Callable[[], None]] = None
        self.on_disconnected: Optional[Callable[[], None]] = None
    
    def configure(self, host: str, port: int, device: str, remote_folder: str):
        """Configure sync settings"""
        self.host = host
        self.port = port
        self.device = device
        self.remote_folder = remote_folder
    
    async def connect_and_attach(self) -> bool:
        """Connect and optionally attach to device"""
        try:
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
                        # Device attachment failed, but connection succeeded
                        return True
                else:
                    # No device specified, just return successful connection
                    if self.on_connected:
                        self.on_connected()
                    return True
            
            return False
            
        except Exception as e:
            if self.on_error:
                self.on_error(f"❌ Connection failed: {str(e)}")
            return False
    
    async def get_devices(self) -> List[str]:
        """Get available devices"""
        if not self.sync_client:
            temp_client = QUSB2SNESSync(self.host, self.port)
            if await temp_client.connect():
                devices = await temp_client.get_devices()
                await temp_client.disconnect()
                return devices
        else:
            return await self.sync_client.get_devices()
        
        return []
    
    async def sync_roms(self, local_rom_dir: str) -> bool:
        """Sync ROM directory"""
        if not self.sync_client:
            if self.on_error:
                self.on_error("❌ Not connected to QUSB2SNES")
            return False
        
        return await self.sync_client.sync_directory(local_rom_dir, self.remote_folder)
    
    async def disconnect(self):
        """Disconnect from QUSB2SNES"""
        if self.sync_client:
            await self.sync_client.disconnect()
            self.sync_client = None
            if self.on_disconnected:
                self.on_disconnected()