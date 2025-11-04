#!/usr/bin/env python3
"""
QUSB2SNES Upload Manager V3 - Simplified & Proven
Based on successful two-phase upload strategy with case-insensitive directory handling

Key Features:
- Two-phase approach: directory creation then file upload
- Proven MakeDir delay strategy (2-second delays between directory operations)
- Case-insensitive directory existence checking
- Simple, direct websocket communication
- Reliable error handling and retry logic
"""

import asyncio
import json
import logging
import os
import time
from pathlib import Path, PurePosixPath
from typing import Dict, List, Optional, Set, Callable
from dataclasses import dataclass

try:
    import websockets
except ImportError:
    websockets = None

# Configuration support
try:
    from config_manager import ConfigManager
except ImportError:
    ConfigManager = None


@dataclass
class UploadProgress:
    """Upload progress tracking"""
    files_completed: int = 0
    total_files: int = 0
    bytes_uploaded: int = 0
    total_bytes: int = 0
    current_file: str = ""
    
    @property
    def progress_percent(self) -> float:
        """Get overall progress percentage"""
        if self.total_files == 0:
            return 0.0
        return (self.files_completed / self.total_files) * 100.0


class QUSB2SNESUploadManagerV3:
    """
    Simplified, proven upload manager using two-phase strategy
    """
    
    def __init__(self, websocket_url: str = "ws://localhost:8080", config_manager: Optional[object] = None):
        self.websocket_url = websocket_url
        self.websocket = None
        self.device_name = None
        self.config_manager = config_manager
        
        # Configuration
        self.chunk_size = 1024  # Proven chunk size
        self.mkdir_delay = 2.0  # Critical: 2-second delay between MakeDir operations
        self.attachment_delay = 0.5  # Delay after device attachment
        self.name_delay = 0.1  # Delay after setting name
        
        # Progress tracking
        self.progress = UploadProgress()
        self.on_progress: Optional[Callable[[UploadProgress], None]] = None
        
        # Directory caching
        self.existing_directories: Set[str] = set()
        self.created_directories: Set[str] = set()
        
        # Logging
        self.logger = logging.getLogger("QUSB2SNESUploadV3")
    
    def _log_info(self, message: str):
        """Log info message"""
        if self.logger:
            self.logger.info(message)
        print(f"[UploadV3] {message}")
    
    def _log_error(self, message: str):
        """Log error message"""
        if self.logger:
            self.logger.error(message)
        print(f"[UploadV3] ERROR: {message}")
    
    def _log_debug(self, message: str):
        """Log debug message"""
        if self.logger:
            self.logger.debug(message)
    
    async def connect(self) -> bool:
        """Connect and setup QUSB2SNES session"""
        try:
            if websockets is None:
                self._log_error("websockets library not available")
                return False
            
            # Close existing connection if any
            if self.websocket and not self.websocket.closed:
                await self.websocket.close()
            
            # Connect
            self.websocket = await websockets.connect(self.websocket_url)
            
            # DeviceList
            cmd = {"Opcode": "DeviceList", "Space": "SNES"}
            await self.websocket.send(json.dumps(cmd))
            response = await self.websocket.recv()
            devices = json.loads(response).get("Results", [])
            
            if not devices:
                self._log_error("No QUSB2SNES devices found")
                return False
            
            self.device_name = devices[0]
            
            # Attach (no response expected)
            cmd = {"Opcode": "Attach", "Space": "SNES", "Operands": [self.device_name]}
            await self.websocket.send(json.dumps(cmd))
            await asyncio.sleep(self.attachment_delay)
            
            # Name (no response expected)
            cmd = {"Opcode": "Name", "Space": "SNES", "Operands": ["UploadV3"]}
            await self.websocket.send(json.dumps(cmd))
            await asyncio.sleep(self.name_delay)
            
            return True
            
        except Exception as e:
            self._log_error(f"Connection failed: {e}")
            return False
    
    async def disconnect(self):
        """Disconnect from QUSB2SNES"""
        if self.websocket and not self.websocket.closed:
            await self.websocket.close()
            self.websocket = None

    async def scan_sd_card_structure(self, root_path: str = "/roms") -> Set[str]:
        """
        Perform a comprehensive scan of SD card directory structure
        Returns a set of all existing directory paths
        """
        self._log_info(f"🔍 Scanning SD card structure from {root_path}")
        
        all_directories = set()
        directories_to_scan = [root_path]
        
        # Add the root path itself to the found directories
        all_directories.add(root_path)
        
        while directories_to_scan:
            current_dir = directories_to_scan.pop(0)
            
            try:
                self._log_debug(f"Scanning directory: {current_dir}")
                
                # List current directory
                cmd = {"Opcode": "List", "Space": "SNES", "Operands": [current_dir]}
                await self.websocket.send(json.dumps(cmd))
                
                response = await asyncio.wait_for(self.websocket.recv(), timeout=10.0)
                data = json.loads(response)
                
                if "Results" in data:
                    results = data["Results"]
                    for i in range(0, len(results), 2):
                        if i + 1 < len(results):
                            file_type = results[i]
                            file_name = results[i + 1]
                            
                            # Skip . and .. entries
                            if file_name in [".", ".."]:
                                continue
                            
                            if file_type == "0":  # Directory
                                # Build full path
                                if current_dir == "/":
                                    dir_path = f"/{file_name}"
                                else:
                                    dir_path = f"{current_dir}/{file_name}"
                                
                                all_directories.add(dir_path)
                                directories_to_scan.append(dir_path)
                                self._log_debug(f"Found directory: {dir_path}")
                
                # Small delay to avoid overwhelming the server
                await asyncio.sleep(0.1)
                
            except Exception as e:
                self._log_error(f"Failed to scan directory {current_dir}: {e}")
                # Continue scanning other directories
                continue
        
        self._log_info(f"📁 Scan complete: found {len(all_directories)} directories")
        return all_directories
    
    async def find_missing_directories(self, required_dirs: List[str]) -> List[str]:
        """
        Compare required directories against SD card structure
        Returns list of directories that need to be created
        """
        self._log_info("🔍 Analyzing SD card structure...")
        
        # Connect for scanning
        if not await self.connect():
            self._log_error("Failed to connect for SD card scan")
            return required_dirs  # Assume all are missing if we can't scan
        
        try:
            # Get complete SD card directory structure
            existing_dirs = await self.scan_sd_card_structure()
            await self.disconnect()
            
            # Store in cache for future use
            self.existing_directories.update(existing_dirs)
            
            # Find missing directories (case-insensitive comparison)
            missing_dirs = []
            
            for required_dir in required_dirs:
                # Check if any existing directory matches (case-insensitive)
                found = False
                for existing_dir in existing_dirs:
                    if existing_dir.lower() == required_dir.lower():
                        self._log_debug(f"Directory exists: {required_dir} (found as {existing_dir})")
                        found = True
                        break
                
                if not found:
                    missing_dirs.append(required_dir)
                    self._log_debug(f"Directory missing: {required_dir}")
            
            self._log_info(f"📊 Analysis complete:")
            self._log_info(f"   Required: {len(required_dirs)} directories")
            self._log_info(f"   Existing: {len(existing_dirs)} directories")  
            self._log_info(f"   Missing:  {len(missing_dirs)} directories")
            
            if missing_dirs:
                self._log_info("📋 Missing directories:")
                for missing_dir in missing_dirs:
                    self._log_info(f"   {missing_dir}")
            
            return missing_dirs
            
        except Exception as e:
            self._log_error(f"Failed to analyze SD card structure: {e}")
            return required_dirs  # Assume all are missing if analysis fails
        
        finally:
            await self.disconnect()
    
    async def check_directory_exists(self, dir_path: str) -> bool:
        """Check if directory exists (case-insensitive)"""
        # Check cache first
        if dir_path in self.existing_directories or dir_path in self.created_directories:
            return True
        
        try:
            parent_path = str(PurePosixPath(dir_path).parent)
            dir_name = PurePosixPath(dir_path).name
            
            self._log_debug(f"Checking existence: parent='{parent_path}', dir='{dir_name}'")
            
            # List parent directory
            cmd = {"Opcode": "List", "Space": "SNES", "Operands": [parent_path]}
            await self.websocket.send(json.dumps(cmd))
            
            response = await asyncio.wait_for(self.websocket.recv(), timeout=5.0)
            data = json.loads(response)
            
            if "Results" in data:
                results = data["Results"]
                for i in range(0, len(results), 2):
                    if i + 1 < len(results):
                        file_type = results[i]
                        file_name = results[i + 1]
                        
                        # Case-insensitive directory match
                        if file_type == "0" and file_name.lower() == dir_name.lower():
                            self._log_debug(f"Found existing directory: '{file_name}' matches '{dir_name}'")
                            self.existing_directories.add(dir_path)
                            return True
            
            self._log_debug(f"Directory not found: {dir_path}")
            return False
            
        except Exception as e:
            self._log_error(f"Could not check directory {dir_path}: {e}")
            # If we can't check, assume it doesn't exist and let MakeDir handle it
            return False
    
    async def create_directory(self, dir_path: str) -> bool:
        """Create a single directory"""
        try:
            cmd = {"Opcode": "MakeDir", "Space": "SNES", "Operands": [dir_path]}
            await self.websocket.send(json.dumps(cmd))
            await asyncio.sleep(0.1)  # Brief pause after MakeDir
            
            if self.websocket.closed:
                self._log_error(f"Connection closed after creating: {dir_path}")
                return False
            
            self.created_directories.add(dir_path)
            return True
            
        except Exception as e:
            self._log_error(f"Failed to create directory {dir_path}: {e}")
            return False
    
    def get_required_directories(self, file_mappings: List[tuple]) -> List[str]:
        """Get all unique directories needed for file uploads"""
        directories = set()
        
        for local_path, remote_path in file_mappings:
            remote_dir = str(PurePosixPath(remote_path).parent)
            if remote_dir != "/" and remote_dir != ".":
                # Build path hierarchy
                current_path = remote_dir
                while current_path != "/" and current_path != "":
                    directories.add(current_path)
                    current_path = str(PurePosixPath(current_path).parent)
        
        # Sort hierarchically (shorter paths first)
        return sorted(directories, key=lambda x: (x.count('/'), x))
    
    async def phase1_create_directories(self, file_mappings: List[tuple]) -> bool:
        """Phase 1: Create all required directories using smart analysis"""
        self._log_info("🏗️ PHASE 1: Smart Directory Creation")
        
        required_dirs = self.get_required_directories(file_mappings)
        
        if not required_dirs:
            self._log_info("✅ No directories need to be created")
            return True
        
        # Find which directories actually need to be created
        missing_dirs = await self.find_missing_directories(required_dirs)
        
        if not missing_dirs:
            self._log_info("✅ All required directories already exist")
            return True
        
        self._log_info(f"📂 Creating {len(missing_dirs)} missing directories")
        
        created_count = 0
        for i, dir_path in enumerate(missing_dirs, 1):
            self._log_info(f"📂 Creating directory {i}/{len(missing_dirs)}: {dir_path}")
            
            # Wait before creating (critical for server stability)
            if created_count > 0:  # No delay before first creation
                self._log_debug(f"Waiting {self.mkdir_delay}s (server limitation)")
                await asyncio.sleep(self.mkdir_delay)
            
            # Connect for directory creation
            if not await self.connect():
                self._log_error("Failed to connect for directory creation")
                return False
            
            success = await self.create_directory(dir_path)
            await self.disconnect()
            
            if success:
                created_count += 1
                self._log_info(f"✅ Created directory: {dir_path}")
            else:
                self._log_error(f"❌ Failed to create directory: {dir_path}")
                return False
        
        self._log_info(f"🎉 PHASE 1 COMPLETE! Created {created_count} new directories")
        return True
    
    async def upload_file(self, local_path: str, remote_path: str) -> bool:
        """Upload a single file using proven method"""
        try:
            # Read file data
            with open(local_path, 'rb') as f:
                file_data = f.read()
            
            if len(file_data) == 0:
                self._log_error(f"Cannot upload empty file: {local_path}")
                return False
            
            # PutFile command (no response expected)
            cmd = {"Opcode": "PutFile", "Space": "SNES", "Operands": [remote_path, hex(len(file_data))]}
            await self.websocket.send(json.dumps(cmd))
            
            # Send file data in chunks
            for i in range(0, len(file_data), self.chunk_size):
                chunk = file_data[i:i + self.chunk_size]
                await self.websocket.send(chunk)
            
            # Update progress
            self.progress.bytes_uploaded += len(file_data)
            
            return True
            
        except Exception as e:
            self._log_error(f"Failed to upload {local_path}: {e}")
            return False
    
    async def phase2_upload_files(self, file_mappings: List[tuple]) -> bool:
        """Phase 2: Upload all files in a single connection"""
        self._log_info("📤 PHASE 2: Uploading Files")
        
        if not file_mappings:
            self._log_info("✅ No files to upload")
            return True
        
        # Connect once for all uploads
        if not await self.connect():
            self._log_error("Failed to connect for file uploads")
            return False
        
        try:
            uploaded_count = 0
            for i, (local_path, remote_path) in enumerate(file_mappings, 1):
                self._log_info(f"📄 Uploading file {i}/{len(file_mappings)}: {os.path.basename(local_path)}")
                
                self.progress.current_file = os.path.basename(local_path)
                
                success = await self.upload_file(local_path, remote_path)
                
                if success:
                    uploaded_count += 1
                    self.progress.files_completed += 1
                    self._log_info(f"✅ Uploaded: {remote_path}")
                else:
                    self._log_error(f"❌ Failed to upload: {local_path}")
                    return False
                
                # Report progress
                if self.on_progress:
                    self.on_progress(self.progress)
            
            self._log_info(f"🎉 PHASE 2 COMPLETE! Uploaded {uploaded_count} files")
            return True
            
        finally:
            await self.disconnect()
    
    async def upload_files(self, file_mappings: List[tuple]) -> bool:
        """
        Main upload method using proven two-phase strategy
        
        Args:
            file_mappings: List of (local_path, remote_path) tuples
            
        Returns:
            bool: True if all uploads successful
        """
        if not file_mappings:
            self._log_info("No files to upload")
            return True
        
        # Initialize progress
        self.progress = UploadProgress()
        self.progress.total_files = len(file_mappings)
        self.progress.total_bytes = sum(os.path.getsize(local) for local, _ in file_mappings if os.path.exists(local))
        
        self._log_info(f"🚀 Starting two-phase upload of {len(file_mappings)} files")
        
        # Phase 1: Create directories
        if not await self.phase1_create_directories(file_mappings):
            self._log_error("Phase 1 (directory creation) failed")
            return False
        
        # Phase 2: Upload files
        if not await self.phase2_upload_files(file_mappings):
            self._log_error("Phase 2 (file upload) failed")
            return False
        
        self._log_info("🏆 TWO-PHASE UPLOAD SUCCESSFUL!")
        return True
    
    async def upload_directory_sync(self, local_root: str, remote_root: str, 
                                  file_filter: Optional[Callable[[str], bool]] = None) -> bool:
        """
        Sync a local directory to remote, maintaining structure
        
        Args:
            local_root: Local directory root
            remote_root: Remote directory root
            file_filter: Optional filter function for files
            
        Returns:
            bool: True if sync successful
        """
        if not os.path.exists(local_root):
            self._log_error(f"Local directory not found: {local_root}")
            return False
        
        # Build file mappings
        file_mappings = []
        
        for root, dirs, files in os.walk(local_root):
            for file in files:
                local_path = os.path.join(root, file)
                
                # Apply filter if provided
                if file_filter and not file_filter(local_path):
                    continue
                
                # Calculate relative path and convert to remote path
                rel_path = os.path.relpath(local_path, local_root)
                remote_path = str(PurePosixPath(remote_root) / rel_path.replace(os.sep, '/'))
                
                file_mappings.append((local_path, remote_path))
        
        self._log_info(f"📁 Syncing {local_root} → {remote_root} ({len(file_mappings)} files)")
        
        return await self.upload_files(file_mappings)
    
    def get_config_paths(self) -> tuple[str, str]:
        """
        Get local and remote paths from configuration
        Returns (local_root, remote_root) tuple
        """
        if not self.config_manager:
            return None, None
        
        try:
            # Get local ROM output directory (try both config keys)
            local_root = self.config_manager.get("output_rom_folder", "")
            if not local_root:
                local_root = self.config_manager.get("output_dir", "")
            
            if not local_root:
                self._log_error("No output_rom_folder or output_dir configured")
                return None, None
            
            # Get SD card sync directory (try multiple keys)
            remote_root = self.config_manager.get("qusb2snes_sync_to_folder", "")
            if not remote_root:
                remote_root = self.config_manager.get("qusb2snes_remote_folder", "/roms")
            if not remote_root:
                remote_root = "/roms"  # Default fallback
            
            # Normalize remote path
            if not remote_root.startswith("/"):
                remote_root = "/" + remote_root
            
            self._log_info(f"📂 Config paths: Local='{local_root}' → Remote='{remote_root}'")
            return local_root, remote_root
            
        except Exception as e:
            self._log_error(f"Failed to get configuration paths: {e}")
            return None, None
    
    async def sync_from_config(self, file_filter: Optional[Callable[[str], bool]] = None) -> bool:
        """
        Sync ROMs using paths from configuration manager
        
        Args:
            file_filter: Optional filter function for files
            
        Returns:
            bool: True if sync successful
        """
        local_root, remote_root = self.get_config_paths()
        
        if not local_root or not remote_root:
            self._log_error("Configuration paths not available")
            return False
        
        return await self.upload_directory_sync(local_root, remote_root, file_filter)