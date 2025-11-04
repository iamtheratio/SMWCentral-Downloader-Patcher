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
    
    def __init__(self, websocket_url: str = "ws://localhost:23074", config_manager: Optional[object] = None, logging_system: Optional[object] = None):
        self.websocket_url = websocket_url
        self.websocket = None
        self.device_name = None
        self.config_manager = config_manager
        self.logging_system = logging_system  # Application logging system
        
        # Configuration
        self.chunk_size = 1024  # Proven chunk size
        self.mkdir_delay = 2.0  # Critical: 2-second delay between MakeDir operations
        self.attachment_delay = 0.5  # Delay after device attachment
        self.name_delay = 0.1  # Delay after setting name
        
        # Progress tracking
        self.progress = UploadProgress()
        self.on_progress: Optional[Callable[[UploadProgress], None]] = None
        
        # Directory and file caching
        self.existing_directories: Set[str] = set()
        self.existing_files: Set[str] = set()
        self.created_directories: Set[str] = set()
        
        # Logging
        self.logger = logging.getLogger("QUSB2SNESUploadV3")
    
    def _log_info(self, message: str):
        """Log info message"""
        # Use application logging system if available
        if self.logging_system:
            self.logging_system.log(message, "Information")
        else:
            # Fallback to console
            print(message)
    
    def _log_error(self, message: str):
        """Log error message"""
        # Use application logging system if available
        if self.logging_system:
            self.logging_system.log(message, "Error")
        else:
            # Fallback to console
            print(f"ERROR: {message}")
    
    def _log_warning(self, message: str):
        """Log warning message"""
        # Use application logging system if available
        if self.logging_system:
            self.logging_system.log(message, "Warning")
        else:
            # Fallback to console
            print(f"WARNING: {message}")
    
    def _log_debug(self, message: str):
        """Log debug message"""
        if self.logger:
            self.logger.debug(message)
    
    def _normalize_sd_path(self, path: str) -> str:
        """
        Normalize path for SD card operations (convert to Pascal case)
        SD card file systems may have case sensitivity issues,
        so we normalize to Pascal case for consistent, readable paths.
        Example: /ROMS2/kaizo/expert → /Roms2/Kaizo/Expert
        """
        if not path or path == "/":
            return path
        
        # Split path into components
        parts = path.strip('/').split('/')
        
        # Convert each part to Pascal case (first letter uppercase, rest lowercase)
        normalized_parts = []
        for part in parts:
            if part:  # Skip empty parts
                # Handle special cases like "01 - Newcomer" or "Tool-Assisted"
                if ' - ' in part:
                    # Split on " - " and capitalize each section
                    sections = part.split(' - ')
                    normalized_sections = [section.strip().capitalize() for section in sections]
                    normalized_part = ' - '.join(normalized_sections)
                elif '-' in part and not part.startswith('-'):
                    # Handle hyphenated words like "Tool-Assisted"
                    words = part.split('-')
                    normalized_words = [word.capitalize() for word in words if word]
                    normalized_part = '-'.join(normalized_words)
                else:
                    # Regular word - just capitalize
                    normalized_part = part.capitalize()
                
                normalized_parts.append(normalized_part)
        
        # Rebuild the path
        if normalized_parts:
            return '/' + '/'.join(normalized_parts)
        else:
            return path
    
    async def connect(self) -> bool:
        """Connect and setup QUSB2SNES session"""
        try:
            if websockets is None:
                self._log_error("websockets library not available")
                return False
            
            # Close existing connection if any
            if self.websocket:
                try:
                    await self.websocket.close()
                except:
                    pass
            
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
        if self.websocket:
            try:
                await self.websocket.close()
            except Exception as e:
                self._log_debug(f"Error during disconnect: {e}")
            finally:
                self.websocket = None

    async def scan_sd_card_structure(self, root_path: str = "/roms") -> tuple[Set[str], Set[str]]:
        """
        Perform a focused recursive scan of SD card directory structure
        Scans root directory + complete recursive contents of sync folder only
        Returns a tuple of (all_directories, all_files) as sets of paths
        """
        # Normalize the root path for SD card operations
        normalized_root_path = self._normalize_sd_path(root_path)
        self._log_info(f"🔍 Focused recursive scan of SD card...")
        if normalized_root_path != root_path:
            self._log_debug(f"Using normalized path: {root_path} → {normalized_root_path}")
        
        all_directories = set()
        all_files = set()
        
        # Step 1: Scan root directory to find sync folder
        sync_folder_exists = False
        actual_sync_path = normalized_root_path
        
        try:
            self._log_debug(f"Scanning root directory /")
            cmd = {"Opcode": "List", "Space": "SNES", "Operands": ["/"]}
            await self.websocket.send(json.dumps(cmd))
            
            response = await asyncio.wait_for(self.websocket.recv(), timeout=10.0)
            data = json.loads(response)
            
            if "Results" in data:
                results = data["Results"]
                all_directories.add("/")  # Add root to directories
                
                for i in range(0, len(results), 2):
                    if i + 1 < len(results):
                        file_type = results[i]
                        file_name = results[i + 1]
                        
                        if file_name in [".", ".."]:
                            continue
                        
                        if file_type == "0":  # Directory
                            dir_path = f"/{file_name}"
                            all_directories.add(dir_path)
                            self._log_debug(f"Found root directory: {dir_path}")
                            
                            # Check if this is our sync folder (case-insensitive)
                            if dir_path.lower() == normalized_root_path.lower():
                                sync_folder_exists = True
                                actual_sync_path = dir_path
                                self._log_info(f"✅ Found sync folder: {dir_path}")
                        elif file_type == "1":  # File
                            file_path = f"/{file_name}"
                            all_files.add(file_path)
                            self._log_debug(f"Found root file: {file_path}")
            
        except Exception as e:
            self._log_error(f"Failed to scan root directory: {e}")
            return all_directories, all_files
        
        if not sync_folder_exists:
            self._log_info(f"📁 Sync folder {normalized_root_path} not found - will be created")
            return all_directories, all_files
        
        # Step 2: Recursively scan all contents within sync folder
        async def scan_directory_recursive(dir_path: str):
            """Recursively scan a directory and all subdirectories"""
            try:
                self._log_debug(f"Recursively scanning: {dir_path}")
                cmd = {"Opcode": "List", "Space": "SNES", "Operands": [dir_path]}
                await self.websocket.send(json.dumps(cmd))
                
                # Small delay to avoid overwhelming the connection
                await asyncio.sleep(0.1)
                
                response = await asyncio.wait_for(self.websocket.recv(), timeout=10.0)
                data = json.loads(response)
                
                if "Results" in data:
                    results = data["Results"]
                    subdirs_to_scan = []
                    
                    for i in range(0, len(results), 2):
                        if i + 1 < len(results):
                            file_type = results[i]
                            file_name = results[i + 1]
                            
                            if file_name in [".", ".."]:
                                continue
                            
                            if file_type == "0":  # Directory
                                subdir_path = f"{dir_path}/{file_name}"
                                all_directories.add(subdir_path)
                                subdirs_to_scan.append(subdir_path)
                                self._log_debug(f"Found subdirectory: {subdir_path}")
                            elif file_type == "1":  # File
                                file_path = f"{dir_path}/{file_name}"
                                all_files.add(file_path)
                                self._log_debug(f"Found file: {file_path}")
                    
                    # Recursively scan all subdirectories found
                    for subdir in subdirs_to_scan:
                        await scan_directory_recursive(subdir)
                        
            except Exception as e:
                self._log_debug(f"Could not scan directory {dir_path}: {e}")
        
        # Start recursive scan from the sync folder
        self._log_info(f"🔍 Recursively scanning sync folder: {actual_sync_path}")
        await scan_directory_recursive(actual_sync_path)
        
        self._log_info(f"📁 Found {len(all_directories)} directories, {len(all_files)} files")
        return all_directories, all_files
    
    async def find_missing_directories(self, required_dirs: List[str], remote_root: str = "/roms") -> List[str]:
        """
        Compare required directories against SD card structure
        Returns list of directories that need to be created
        """
        self._log_info("🔍 Checking directory structure...")
        
        # Connect for scanning
        if not await self.connect():
            self._log_error("Connection failed - assuming all directories missing")
            return required_dirs  # Assume all are missing if we can't scan
        
        try:
            # Get complete SD card directory structure using the correct remote root
            existing_dirs, existing_files = await self.scan_sd_card_structure(remote_root)
            await self.disconnect()
            
            # Store in cache for future use
            self.existing_directories.update(existing_dirs)
            # Store files for sync filtering
            self.existing_files = existing_files
            
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
            
            self._log_info(f"📊 Need to create {len(missing_dirs)} of {len(required_dirs)} directories")
            
            if missing_dirs:
                self._log_debug("Missing directories:")
                for missing_dir in missing_dirs[:5]:  # Show first 5 only
                    self._log_debug(f"   {missing_dir}")
                if len(missing_dirs) > 5:
                    self._log_debug(f"   ... and {len(missing_dirs) - 5} more")
            
            return missing_dirs
            
        except Exception as e:
            self._log_error(f"Directory check failed: {e}")
            return required_dirs  # Assume all are missing if analysis fails
        
        finally:
            await self.disconnect()
    
    async def check_file_exists(self, file_path: str) -> bool:
        """Check if file exists on SD card (case-insensitive)"""
        # Check cache first
        if file_path in self.existing_files:
            return True
        
        try:
            parent_path = str(PurePosixPath(file_path).parent)
            file_name = PurePosixPath(file_path).name
            
            self._log_debug(f"Checking file existence: parent='{parent_path}', file='{file_name}'")
            
            # List parent directory
            cmd = {"Opcode": "List", "Space": "SNES", "Operands": [parent_path]}
            await self.websocket.send(json.dumps(cmd))
            
            response = await asyncio.wait_for(self.websocket.recv(), timeout=5.0)
            data = json.loads(response)
            
            if data.get("Results", []):
                existing_files = set()
                for item in data["Results"]:
                    if item.get("Type") == "1":  # File type
                        existing_files.add(f"{parent_path}/{item['Name']}")
                
                # Check if our file exists (case-insensitive)
                for existing_file in existing_files:
                    if PurePosixPath(existing_file).name.lower() == file_name.lower():
                        # Update cache
                        self.existing_files.add(file_path)
                        return True
            
            return False
            
        except Exception as e:
            self._log_error(f"Error checking file existence for '{file_path}': {e}")
            return False

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
            
            # Check if connection is still valid (simplified check)
            if not self.websocket:
                self._log_error(f"Connection lost after creating: {dir_path}")
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
        sorted_dirs = sorted(directories, key=lambda x: (x.count('/'), x))
        
        # Debug: log the required directories
        self._log_debug(f"Required directories ({len(sorted_dirs)}): {sorted_dirs[:5]}..." if len(sorted_dirs) > 5 else f"Required directories: {sorted_dirs}")
        
        return sorted_dirs
    
    async def phase1_create_directories(self, file_mappings: List[tuple]) -> bool:
        """Phase 1: Create all required directories using smart analysis"""
        self._log_info("🏗️ PHASE 1: Smart Directory Creation")
        
        required_dirs = self.get_required_directories(file_mappings)
        
        if not required_dirs:
            self._log_info("✅ No directories need to be created")
            return True
        
        # Extract remote root from file mappings to determine scan directory
        remote_root = "/" 
        if file_mappings:
            # Get the first remote path and extract its root
            first_remote_path = file_mappings[0][1]  # (local, remote) tuple
            # Find the root directory (e.g., "/ROMS2" from "/ROMS2/Kaizo/file.smc")
            path_parts = first_remote_path.split('/')
            if len(path_parts) >= 2:
                remote_root = "/" + path_parts[1]  # "/ROMS2"
        
        # Always check if directories actually exist on SD card
        # (Previous optimization was unreliable - SD card might be formatted/changed)
        self._log_info(f"🔍 Checking which directories need to be created...")
        
        # Find which directories actually need to be created
        missing_dirs = await self.find_missing_directories(required_dirs, remote_root)
        
        if not missing_dirs:
            self._log_info("✅ All required directories already exist")
            return True
        
        self._log_info(f"📂 Creating {len(missing_dirs)} missing directories")
        
        created_count = 0
        for i, dir_path in enumerate(missing_dirs, 1):
            self._log_info(f"📂 Creating directory {i}/{len(missing_dirs)}: {os.path.basename(dir_path)}")
            
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
                self._log_info(f"✅ Created: {os.path.basename(dir_path)}")
            else:
                self._log_error(f"❌ Failed to create: {os.path.basename(dir_path)}")
                return False
        
        self._log_info(f"📁 Created {created_count} directories")
        return True
    
    def _has_existing_sync_timestamps(self) -> bool:
        """Check if any hacks have qusb_last_sync timestamps (indicating previous sync)"""
        try:
            import json
            from utils import PROCESSED_JSON_PATH
            
            if not os.path.exists(PROCESSED_JSON_PATH):
                return False
                
            with open(PROCESSED_JSON_PATH, 'r', encoding='utf-8') as f:
                processed_data = json.load(f)
            
            # Check if any non-obsolete hack has a sync timestamp
            for hack_data in processed_data.values():
                if (not hack_data.get("obsolete", False) and 
                    hack_data.get("qusb_last_sync", 0) > 0):
                    return True
                    
            return False
            
        except Exception as e:
            self._log_debug(f"Could not check sync timestamps: {e}")
            return False
    
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
                    self._log_info(f"✅ Uploaded: {os.path.basename(local_path)}")
                else:
                    self._log_error(f"❌ Failed: {os.path.basename(local_path)}")
                    return False
                
                # Report progress
                if self.on_progress:
                    self.on_progress(self.progress)
            
            self._log_info(f"📤 Uploaded {uploaded_count} files")
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
        
        # Scan SD card structure first to get existing files for filter decisions
        try:
            self._log_info("📂 Scanning SD card structure for sync decisions...")
            existing_dirs, existing_files = await self.scan_sd_card_structure(remote_root)
            self.existing_files = existing_files
            self._log_info(f"📂 Found {len(existing_files)} files on SD card")
        except Exception as e:
            self._log_error(f"Could not scan SD card structure: {e} - proceeding with timestamp-only sync")
            self.existing_files = set()
        
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
                
                # Normalize the remote path for consistent SD card formatting
                normalized_remote_path = self._normalize_sd_path(remote_path)
                
                file_mappings.append((local_path, normalized_remote_path))
        
        # Log summary statistics if the filter supports it
        if file_filter and hasattr(file_filter, 'log_summary'):
            file_filter.log_summary()
        
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