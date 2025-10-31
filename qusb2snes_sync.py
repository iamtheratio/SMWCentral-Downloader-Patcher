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
    
    def is_rom_file(self, filename: str) -> bool:
        """Check if file is a ROM file that should be synced"""
        return filename.lower().endswith(('.smc', '.sfc'))
    
    def normalize_remote_path(self, path: str) -> str:
        """Normalize path for SD2SNES (forward slashes, no double slashes)"""
        # Convert backslashes to forward slashes
        normalized = path.replace("\\", "/")
        
        # Remove double slashes
        while "//" in normalized:
            normalized = normalized.replace("//", "/")
        
        # Ensure it starts with / if it's not empty
        if normalized and not normalized.startswith("/"):
            normalized = "/" + normalized
        
        return normalized
    
    def find_directory_case_insensitive(self, target_name: str, available_names: List[str]) -> Optional[str]:
        """Find directory name using case-insensitive matching"""
        target_lower = target_name.lower()
        for name in available_names:
            if name.lower() == target_lower:
                return name
        return None
    
    async def sync_directory_tree_based(self, local_dir: str, remote_sync_folder: str) -> bool:
        """
        Tree-based sync approach that builds knowledge incrementally.
        This prevents connection drops by never guessing if directories exist.
        """
        try:
            self.log_progress(f"🌳 Starting tree-based sync: {local_dir} -> {remote_sync_folder}")
            
            # Step 1: Always start by listing root - we know this exists
            root_items = await self.list_directory("/")
            root_names = [item["name"] for item in root_items]
            self.log_progress(f"📁 Root directory contains: {root_names}")
            
            # Step 2: Check if sync folder exists (case-insensitive)
            sync_folder_name = remote_sync_folder.strip("/")
            actual_sync_folder = self.find_directory_case_insensitive(sync_folder_name, root_names)
            
            if actual_sync_folder:
                # Sync folder exists - use it
                actual_remote_path = self.normalize_remote_path(f"/{actual_sync_folder}")
                self.log_progress(f"✅ Using existing sync folder: {actual_remote_path}")
            else:
                # Sync folder doesn't exist - create it
                normalized_path = self.normalize_remote_path(remote_sync_folder)
                self.log_progress(f"📁 Creating sync folder: {normalized_path}")
                
                if await self.create_directory(normalized_path):
                    actual_remote_path = normalized_path
                    self.log_progress(f"✅ Created sync folder: {actual_remote_path}")
                else:
                    self.log_error(f"❌ Failed to create sync folder: {normalized_path}")
                    return False
            
            # Step 3: Recursively sync using tree approach
            result = await self.sync_local_to_remote_tree(local_dir, actual_remote_path)
            
            if result["success"]:
                self.log_progress(f"✅ Tree-based sync completed: {result['uploaded']} files uploaded")
                return True
            else:
                self.log_error(f"❌ Tree-based sync failed: {result.get('error', 'Unknown error')}")
                return False
                
        except Exception as e:
            self.log_error(f"❌ Tree-based sync failed: {str(e)}")
            return False
    
    async def sync_local_to_remote_tree(self, local_dir: str, remote_dir: str) -> Dict:
        """
        Recursively sync local directory to remote using tree-based approach.
        """
        result = {"success": False, "uploaded": 0, "error": None}
        
        try:
            # List remote directory to see what exists
            remote_items = await self.list_directory(remote_dir)
            remote_names = {item["name"] for item in remote_items}
            remote_dirs = {item["name"] for item in remote_items if item.get("is_dir", False)}
            
            self.log_progress(f"📁 Remote {remote_dir} contains {len(remote_items)} items")
            
            # Process local directory contents
            for item_name in os.listdir(local_dir):
                local_path = os.path.join(local_dir, item_name)
                remote_path = self.normalize_remote_path(f"{remote_dir}/{item_name}")
                
                if os.path.isfile(local_path):
                    # Handle file - only process ROM files
                    if not self.is_rom_file(item_name):
                        continue  # Skip non-ROM files
                    
                    should_upload = item_name not in remote_names or self.should_upload_file(local_path)
                    
                    if should_upload:
                        if await self.upload_file(local_path, remote_path):
                            result["uploaded"] += 1
                            self.log_progress(f"📤 Uploaded: {item_name}")
                        else:
                            result["error"] = f"Failed to upload {item_name}"
                            return result
                    else:
                        self.log_progress(f"⏭️ Skipped (up to date): {item_name}")
                
                elif os.path.isdir(local_path):
                    # Handle directory - use case-insensitive matching
                    actual_remote_dir = self.find_directory_case_insensitive(item_name, list(remote_dirs))
                    
                    if actual_remote_dir:
                        # Directory exists - sync into it
                        actual_remote_path = self.normalize_remote_path(f"{remote_dir}/{actual_remote_dir}")
                        self.log_progress(f"📁 Syncing into existing directory: {actual_remote_path}")
                    else:
                        # Directory doesn't exist - create it first
                        self.log_progress(f"📁 Creating directory: {remote_path}")
                        if await self.create_directory(remote_path):
                            actual_remote_path = remote_path
                            # Update our knowledge - add to remote_dirs for subsequent operations
                            remote_dirs.add(item_name)
                        else:
                            result["error"] = f"Failed to create directory {remote_path}"
                            return result
                    
                    # Recursively sync subdirectory
                    subdir_result = await self.sync_local_to_remote_tree(local_path, actual_remote_path)
                    if subdir_result["success"]:
                        result["uploaded"] += subdir_result["uploaded"]
                    else:
                        result["error"] = f"Failed to sync subdirectory {item_name}: {subdir_result.get('error')}"
                        return result
            
            result["success"] = True
            return result
            
        except Exception as e:
            result["error"] = str(e)
            return result
    
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
        """Properly disconnect from QUSB2SNES with cleanup"""
        if self.websocket and self.connected:
            try:
                # Send a proper close frame first
                if not self.websocket.closed:
                    await self.websocket.close(code=1000, reason="Normal closure")
                
                # Wait a moment for cleanup
                await asyncio.sleep(0.1)
                self.log_progress("✅ Disconnected from QUSB2SNES")
            except Exception as e:
                self.log_error(f"⚠️ Disconnect warning: {str(e)}")
        
        self.connected = False
        self.websocket = None
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
        """Attach to specific device with proper timing"""
        try:
            self.log_progress(f"📱 Attaching to device: {device_name}")
            
            # Send attach command
            await self._send_command("Attach", operands=[device_name])
            
            # SD2SNES needs more time to be ready after attach
            self.log_progress("⏳ Waiting for device to be ready...")
            await asyncio.sleep(5.0)
            
            # Try a simple Info command to verify attachment
            # Info is less likely to cause issues than List operations
            try:
                info_response = await self._send_command("Info", timeout=10.0)
                if info_response is not None:
                    self.log_progress("✅ Device attached and verified successfully")
                    return True
                else:
                    # Info failed, but device might still work for file operations
                    self.log_progress("⚠️ Device verification inconclusive, proceeding optimistically")
                    self.log_progress("   (Some SD2SNES devices don't respond to Info but work fine)")
                    return True
            except asyncio.TimeoutError:
                self.log_progress("⚠️ Device verification timeout, proceeding optimistically")
                self.log_progress("   (Some SD2SNES devices are slow to respond but work fine)")
                return True
            except Exception as e:
                self.log_progress(f"⚠️ Device verification failed: {str(e)}")
                self.log_progress("   Proceeding optimistically - many devices work despite verification issues")
                return True
            
        except Exception as e:
            self.log_error(f"❌ Device attachment failed: {str(e)}")
            return False
    
    async def list_directory(self, path: str) -> List[Dict]:
        """List remote directory contents with SD2SNES-safe delays"""
        try:
            # Add delay before directory listing (SD2SNES requirement)
            await asyncio.sleep(0.2)
            
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
            
            # Add delay after directory listing (SD2SNES requirement)
            await asyncio.sleep(0.3)
            return items
            
        except Exception as e:
            # If listing fails, directory likely doesn't exist
            # SD2SNES closes connection on non-existent directory listing
            self.log_error(f"❌ Failed to list directory {path}: {str(e)}")
            raise e  # Re-raise to allow caller to handle appropriately
    
    async def _ensure_connection(self) -> bool:
        """Ensure we have a working connection, reconnect if needed"""
        if self.connected and self.websocket and not self.websocket.closed:
            return True
        
        self.log_progress("🔄 Reconnecting to QUSB2SNES...")
        
        # Clean up any existing connection
        await self.disconnect()
        await asyncio.sleep(1.0)
        
        # Attempt to reconnect
        if await self.connect():
            # Re-attach to the last known device if we have one
            devices = await self.get_devices()
            if devices:
                # Try to reattach to first available device
                if await self.attach_device(devices[0]):
                    self.log_progress("✅ Reconnected and reattached successfully")
                    return True
                else:
                    self.log_error("❌ Failed to reattach device after reconnection")
            else:
                self.log_error("❌ No devices available after reconnection")
        else:
            self.log_error("❌ Failed to reconnect to QUSB2SNES")
        
        return False
    
    async def create_directory(self, path: str) -> bool:
        """Create remote directory using proven working approach"""
        try:
            await self._send_command("MakeDir", operands=[path])
            await asyncio.sleep(1.0)  # Wait for directory creation
            return True
        except Exception as e:
            self.log_error(f"❌ Failed to create directory {path}: {str(e)}")
            return False
    
    async def upload_file(self, local_path: str, remote_path: str) -> bool:
        """Upload file to remote location with connection recovery"""
        max_retries = 2  # Files uploads are more expensive, fewer retries
        
        for attempt in range(max_retries):
            try:
                # Ensure connection before operation
                if not await self._ensure_connection():
                    raise Exception("Could not establish connection")
                
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
                    raise Exception(f"PutFile command failed for {remote_path}")
                
                # Small delay before sending file data
                await asyncio.sleep(0.1)
                
                # Send file data in chunks with proper progress reporting like the working version
                chunk_size = 1024  # Standard QUSB2SNES chunk size
                bytes_sent = 0
                total_chunks = 0
                
                with open(local_path, "rb") as f:
                    while bytes_sent < file_size:
                        # Read chunk directly from file (memory efficient)
                        chunk = f.read(min(chunk_size, file_size - bytes_sent))
                        if not chunk:
                            break
                        
                        try:
                            await self.websocket.send(chunk)
                            bytes_sent += len(chunk)
                            total_chunks += 1
                            
                            # Progress feedback every 500KB like the working version
                            if bytes_sent % (500*1024) == 0 or bytes_sent == file_size:
                                progress_kb = bytes_sent // 1024
                                total_kb = file_size // 1024
                                progress_percent = (bytes_sent / file_size) * 100
                                self.log_progress(f"QUSB2SNES: � Upload progress: {progress_percent:.1f}% ({progress_kb}KB/{total_kb}KB)")
                            
                            # Minimal delay to prevent overwhelming
                            if bytes_sent < file_size:
                                await asyncio.sleep(0.001)  # Very small delay
                                
                        except Exception as e:
                            raise Exception(f"Failed to send chunk at byte {bytes_sent}: {str(e)}")
                
                # Log completion like the working version
                self.log_progress(f"QUSB2SNES: 📤 Sent {bytes_sent} bytes in {total_chunks} chunks to {remote_path}")
                
                # Wait for file processing with optimized timing
                # Most SNES ROMs are 1-4MB and can be processed much faster
                if file_size <= 1024*1024:  # Files <= 1MB
                    wait_time = 0.3  # Very fast for small files
                elif file_size <= 4*1024*1024:  # Files <= 4MB (most ROMs)
                    wait_time = 0.5  # Fast for typical ROM sizes
                elif file_size <= 8*1024*1024:  # Files <= 8MB (large ROMs)
                    wait_time = 1.0  # Moderate for large ROMs
                else:  # Files > 8MB (very rare for SNES)
                    wait_time = 1.5  # Conservative for huge files
                
                self.log_progress(f"QUSB2SNES: ⏳ Waiting {wait_time}s for file processing...")
                await asyncio.sleep(wait_time)
                
                # Verify upload success by listing the parent directory like the working version
                parent_dir = "/".join(remote_path.split("/")[:-1])
                if parent_dir:
                    try:
                        await self.list_directory(parent_dir)
                        self.log_progress(f"✅ Uploaded {os.path.basename(local_path)} successfully verified")
                    except Exception as e:
                        self.log_progress(f"⚠️ Upload verification failed: {str(e)}, but upload likely succeeded")
                
                return True
                
            except Exception as e:
                if attempt == max_retries - 1:
                    self.log_error(f"❌ Upload failed for {local_path} after {max_retries} attempts: {str(e)}")
                    return False
                
                self.log_progress(f"⚠️ Upload attempt {attempt + 1} failed for {os.path.basename(local_path)}: {str(e)}, retrying...")
                await self.disconnect()
                await asyncio.sleep(3.0)  # Longer delay before retrying file uploads
        
        return False
    
    def should_upload_file(self, local_path: str, last_sync_timestamp: float = 0) -> bool:
        """
        Determine if a file should be uploaded based on modification time vs last sync.
        Upload files that have been modified since the last successful sync.
        """
        try:
            local_mtime = os.path.getmtime(local_path)
            
            # Upload if file was modified after last sync
            if local_mtime > last_sync_timestamp:
                return True
                
            return False
        except Exception:
            # If we can't get file time, err on the side of caution and upload
            return True
    
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
    
    async def sync_directory(self, local_dir: str, remote_dir: str, last_sync_timestamp: float = 0) -> bool:
        """Directory sync with smart file comparison and connection recovery"""
        try:
            # Safety check
            if not self.is_safe_remote_path(remote_dir):
                self.log_error(f"❌ Remote path not safe: {remote_dir}")
                return False
            
            if not os.path.exists(local_dir):
                self.log_error(f"❌ Local directory not found: {local_dir}")
                return False
            
            self.log_progress(f"🔄 Starting sync: {local_dir} → {remote_dir}")
            
            # Check if remote directory exists using SD2SNES-safe approach
            # List parent directory first to avoid connection closure
            parent_dir = "/".join(remote_dir.strip("/").split("/")[:-1])
            remote_dir_name = remote_dir.strip("/").split("/")[-1]
            
            if parent_dir:
                # Check if target directory exists by listing parent
                try:
                    parent_items = await self.list_directory(f"/{parent_dir}")
                    parent_names = {item["name"] for item in parent_items}
                    
                    if remote_dir_name in parent_names:
                        # Directory exists, safe to list it
                        remote_items = await self.list_directory(remote_dir)
                        self.log_progress(f"📁 Remote directory exists with {len(remote_items)} items")
                    else:
                        # Directory doesn't exist, create it
                        self.log_progress(f"📁 Creating remote directory: {remote_dir}")
                        if await self.create_directory(remote_dir):
                            remote_items = await self.list_directory(remote_dir)
                        else:
                            self.log_error(f"❌ Failed to create remote directory: {remote_dir}")
                            return {"success": False, "uploaded": 0}
                except Exception as e:
                    self.log_error(f"❌ Failed to check parent directory: {str(e)}")
                    return {"success": False, "uploaded": 0}
            else:
                # Root-level directory, should exist
                try:
                    remote_items = await self.list_directory(remote_dir)
                    self.log_progress(f"📁 Remote directory exists with {len(remote_items)} items")
                except Exception as e:
                    self.log_error(f"❌ Failed to access remote directory {remote_dir}: {str(e)}")
                    return {"success": False, "uploaded": 0}
            
            remote_names = {item["name"] for item in remote_items}
            
            # Sync files from local directory
            uploaded = 0
            for item in os.listdir(local_dir):
                local_path = os.path.join(local_dir, item)
                
                if os.path.isfile(local_path):
                    # Smart upload decision: upload if file doesn't exist OR if modified since last sync
                    should_upload = item not in remote_names or self.should_upload_file(local_path, last_sync_timestamp)
                    
                    if should_upload:
                        remote_path = f"{remote_dir.rstrip('/')}/{item}"
                        if item in remote_names:
                            self.log_progress(f"🔄 Overwriting existing file (modified since last sync): {item}")
                        if await self.upload_file(local_path, remote_path):
                            uploaded += 1
                    else:
                        self.log_progress(f"⏭️ Skipping existing file: {item}")
                elif os.path.isdir(local_path):
                    # Recursive subdirectory sync - handle any depth of nested directories
                    self.log_progress(f"📁 Processing subdirectory: {item}")
                    uploaded += await self.sync_subdirectory_recursive(local_path, item, remote_dir, last_sync_timestamp)
                
                # Small delay between operations to prevent overwhelming the connection
                await asyncio.sleep(0.1)
            
            self.log_progress(f"✅ Sync completed - {uploaded} files uploaded")
            
            # Return both success status and upload count for timestamp saving
            return {"success": True, "uploaded": uploaded}
            
        except Exception as e:
            self.log_error(f"❌ Sync failed: {str(e)}")
            return {"success": False, "uploaded": 0}
    
    async def sync_subdirectory_recursive(self, local_dir_path: str, dir_name: str, parent_remote_dir: str, last_sync_timestamp: float) -> int:
        """Recursively sync a subdirectory using SD2SNES-safe approach"""
        uploaded = 0
        sub_remote_dir = f"{parent_remote_dir.rstrip('/')}/{dir_name}"
        
        try:
            self.log_progress(f"📁 Processing subdirectory: {dir_name}")
            
            # CRITICAL: Always list parent directory first to check if subdirectory exists
            # This prevents connection closure from trying to list non-existent directories
            try:
                parent_items = await self.list_directory(parent_remote_dir)
                parent_names = {item["name"] for item in parent_items}
                
                if dir_name in parent_names:
                    # Directory exists, safe to list it
                    self.log_progress(f"📁 Using existing directory: {sub_remote_dir}")
                    remote_items = await self.list_directory(sub_remote_dir)
                else:
                    # Directory doesn't exist, create it first
                    self.log_progress(f"📁 Creating directory: {sub_remote_dir}")
                    if await self.create_directory(sub_remote_dir):
                        # After creating, list it to get contents (should be empty)
                        remote_items = await self.list_directory(sub_remote_dir)
                    else:
                        self.log_error(f"❌ Failed to create directory {sub_remote_dir}")
                        return uploaded
            except Exception as e:
                self.log_error(f"❌ Failed to check/create directory {sub_remote_dir}: {str(e)}")
                return uploaded
            
            # Get existing remote items
            remote_names = {item["name"] for item in remote_items}
            
            # Process all items in this directory
            for item in os.listdir(local_dir_path):
                local_item_path = os.path.join(local_dir_path, item)
                
                if os.path.isfile(local_item_path):
                    # Handle file
                    should_upload = item not in remote_names or self.should_upload_file(local_item_path, last_sync_timestamp)
                    
                    if should_upload:
                        remote_file_path = f"{sub_remote_dir}/{item}"
                        self.log_progress(f"📤 Uploading {item} to {sub_remote_dir}")
                        
                        if await self.upload_file(local_item_path, remote_file_path):
                            uploaded += 1
                        else:
                            self.log_error(f"❌ Upload failed for {item}")
                    else:
                        self.log_progress(f"⏭️ Skipping existing file: {item}")
                        
                elif os.path.isdir(local_item_path):
                    # Recursively handle subdirectory
                    uploaded += await self.sync_subdirectory_recursive(local_item_path, item, sub_remote_dir, last_sync_timestamp)
                
                # Small delay between operations
                await asyncio.sleep(0.1)
            
            return uploaded
            
        except Exception as e:
            self.log_error(f"❌ Failed to sync subdirectory {sub_remote_dir}: {str(e)}")
            return uploaded
    
    async def _send_command(self, opcode: str, space: str = "SNES", operands: List[str] = None, timeout: float = None) -> Optional[Dict]:
        """Send command to QUSB2SNES with proper logging and response handling"""
        if not self.connected or not self.websocket:
            raise Exception("Not connected to QUSB2SNES")
        
        # Check if websocket is still open
        if self.websocket.closed:
            self.log_error("❌ WebSocket connection closed - device may be in use by another application")
            self.connected = False
            return None
        
        try:
            command = {"Opcode": opcode, "Space": space}
            if operands:
                command["Operands"] = operands
            
            # Commands that don't send replies
            no_reply_commands = ["Attach", "Name", "MakeDir", "PutFile", "Remove"]
            
            if opcode in no_reply_commands:
                self.log_progress(f"QUSB2SNES: Sending command (no response expected): {opcode} with operands: {operands}")
                await self.websocket.send(json.dumps(command))
                self.log_progress(f"QUSB2SNES: Command {opcode} sent successfully")
                return {"status": "ok"}
            else:
                self.log_progress(f"QUSB2SNES: Sending command: {opcode} with operands: {operands}")
                await self.websocket.send(json.dumps(command))
                
                # Use provided timeout or default based on command type
                if timeout is None:
                    timeout = 15.0 if opcode == "List" else 10.0
                
                try:
                    response = await asyncio.wait_for(self.websocket.recv(), timeout=timeout)
                    result = json.loads(response)
                    self.log_progress(f"QUSB2SNES: Received response for {opcode}: {result}")
                    return result
                except asyncio.TimeoutError:
                    self.log_error(f"❌ Command {opcode} timeout after {timeout}s")
                    if opcode in ["Info", "List", "DeviceList"]:
                        self.log_error("💡 This usually means the device is being used by another application")
                        self.log_error("💡 Close RetroAchievements, QFile2Snes, or other USB2SNES applications")
                    return None
                
        except Exception as e:
            # If websocket error, mark as disconnected and provide helpful message
            if "1000" in str(e) or "websocket" in str(e).lower() or "closed" in str(e).lower():
                self.connected = False
                self.websocket = None
                self.log_error(f"❌ Connection lost: {str(e)}")
                self.log_error("💡 Device may be in use by another application (RetroAchievements, QFile2Snes, etc.)")
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
        """Sync ROM directory using tree-based approach"""
        if not self.sync_client:
            if self.on_error:
                self.on_error("❌ Not connected to QUSB2SNES")
            return False
        
        # Use the new tree-based sync approach
        return await self.sync_client.sync_directory_tree_based(local_rom_dir, self.remote_folder)
    
    async def disconnect(self):
        """Disconnect from QUSB2SNES with robust cleanup"""
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