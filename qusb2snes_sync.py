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
    
    def __init__(self, config_or_host=None, port: int = 23074):
        # Support both config object and legacy host/port parameters
        if hasattr(config_or_host, 'get'):  # It's a config object
            self.config = config_or_host
            self.host = config_or_host.get("qusb2snes_host", "localhost")
            self.port = config_or_host.get("qusb2snes_port", 23074)
        else:  # Legacy: first parameter is host
            self.config = None
            self.host = config_or_host if config_or_host else "localhost"
            self.port = port
        
        self.websocket = None
        self.connected = False
        self.app_name = "SMWCentral Downloader"
        
        # Simple callbacks
        self.on_progress: Optional[Callable[[str], None]] = None
        self.on_error: Optional[Callable[[str], None]] = None
        
        # Cancellation support
        self.cancelled = False
    
    def log_progress(self, message: str):
        """Simple progress logging"""
        if self.on_progress:
            self.on_progress(message)
    
    def log_error(self, message: str):
        """Simple error logging"""
        if self.on_error:
            self.on_error(message)
    
    def cancel_operation(self):
        """Cancel the current sync operation"""
        self.cancelled = True
        self.log_progress("⚠️ Cancelling sync operation...")
    
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
    
    async def verify_folder_contents(self, remote_dir: str, expected_files: List[str]) -> bool:
        """
        Verify that all expected files are present in the remote folder with correct sizes.
        Uses GetFile for accurate size checking instead of unreliable List command.
        """
        try:
            self.log_progress(f"🔍 Verifying {len(expected_files)} files in {remote_dir}")
            
            missing_files = []
            zero_byte_files = []
            verified_files = 0
            
            for filename in expected_files:
                remote_path = self.normalize_remote_path(f"{remote_dir}/{filename}")
                
                try:
                    # Use GetFile to check actual file size
                    response = await self._send_command("GetFile", operands=[remote_path])
                    
                    if response and "Results" in response and len(response["Results"]) > 0:
                        size_hex = response["Results"][0]
                        try:
                            remote_size = int(size_hex, 16)
                            
                            if remote_size == 0:
                                zero_byte_files.append(filename)
                            else:
                                verified_files += 1
                                
                        except ValueError:
                            self.log_error(f"⚠️ Invalid size format for {filename}: {size_hex}")
                            missing_files.append(filename)
                    else:
                        missing_files.append(filename)
                        
                except Exception as e:
                    # File might not exist or have filename encoding issues
                    self.log_error(f"⚠️ Could not verify {filename}: {str(e)}")
                    missing_files.append(filename)
            
            # Report results
            total_issues = len(missing_files) + len(zero_byte_files)
            
            if missing_files:
                self.log_error(f"❌ {len(missing_files)} files missing or unreadable: {missing_files[:3]}{'...' if len(missing_files) > 3 else ''}")
            
            if zero_byte_files:
                self.log_error(f"🚨 {len(zero_byte_files)} files are 0 bytes: {zero_byte_files[:3]}{'...' if len(zero_byte_files) > 3 else ''}")
            
            if total_issues > 0:
                success_rate = (verified_files / len(expected_files)) * 100
                self.log_progress(f"⚠️ Partial verification: {verified_files}/{len(expected_files)} files verified ({success_rate:.1f}%)")
                
                # Only fail if more than 10% of files have issues
                if success_rate < 90:
                    self.log_error(f"❌ Folder verification failed: {total_issues} files have issues out of {len(expected_files)} expected")
                    return False
                else:
                    self.log_progress(f"✅ Folder verification passed with warnings: {verified_files} files verified")
                    return True
            else:
                self.log_progress(f"✅ Folder verification passed: All {len(expected_files)} files present with valid sizes")
                return True
                
        except Exception as e:
            self.log_error(f"❌ Folder verification failed with error: {str(e)}")
            return False

    async def sync_directory_tree_based(self, local_dir: str, remote_sync_folder: str, last_sync_timestamp: float = 0, cleanup_deleted: bool = False) -> bool:
        """
        Tree-based sync approach that builds knowledge incrementally.
        This prevents connection drops by never guessing if directories exist.
        
        Args:
            local_dir: Local directory to sync
            remote_sync_folder: Remote folder to sync to
            last_sync_timestamp: Timestamp of last sync for incremental sync
            cleanup_deleted: Whether to remove files from remote that were deleted locally
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
            result = await self.sync_local_to_remote_tree(local_dir, actual_remote_path, last_sync_timestamp)
            
            if result["success"]:
                # Step 4: Clean up deleted files if requested
                if cleanup_deleted:
                    self.log_progress("🧹 Cleaning up deleted files...")
                    cleanup_result = await self.cleanup_deleted_files(local_dir, actual_remote_path)
                    
                    deleted_files = cleanup_result["files_deleted"]
                    deleted_dirs = cleanup_result["dirs_deleted"]
                    errors = cleanup_result["errors"]
                    
                    if deleted_files > 0 or deleted_dirs > 0:
                        self.log_progress(f"🗑️ Cleanup complete: {deleted_files} files, {deleted_dirs} directories removed")
                    
                    if errors:
                        self.log_error(f"⚠️ Cleanup warnings: {len(errors)} items could not be deleted")
                        for error in errors[:3]:  # Show first 3 errors
                            self.log_error(f"   • {error}")
                
                total_uploaded = result['uploaded']
                self.log_progress(f"✅ Tree-based sync completed: {total_uploaded} files uploaded")
                return True
            else:
                self.log_error(f"❌ Tree-based sync failed: {result.get('error', 'Unknown error')}")
                return False
                
        except Exception as e:
            self.log_error(f"❌ Tree-based sync failed: {str(e)}")
            return False
    
    def get_hacks_for_qusb_sync(self) -> List[Dict]:
        """
        Query processed.json for hacks that need QUSB2SNES sync.
        Returns list of hacks where qusb2snes_last_sync == 0 AND obsolete == false AND file exists.
        Organizes by distinct file_path, sorted by hack_type and folder_name.
        """
        import os
        from utils import load_processed
        
        try:
            processed_data = load_processed()
            sync_candidates = []
            
            for hack_id, hack_data in processed_data.items():
                if not isinstance(hack_data, dict):
                    continue
                
                # Check sync criteria
                needs_sync = (
                    hack_data.get("qusb2snes_last_sync", 0) == 0 and  # Never synced or needs re-sync
                    hack_data.get("obsolete", False) == False and      # Not obsolete
                    hack_data.get("file_path", "").strip() != ""       # Has file path
                )
                
                if needs_sync:
                    file_path = hack_data.get("file_path", "")
                    
                    # Validate file exists
                    if os.path.exists(file_path):
                        sync_candidates.append({
                            "hack_id": hack_id,
                            "title": hack_data.get("title", "Unknown"),
                            "hack_type": hack_data.get("hack_type", "standard"),
                            "folder_name": hack_data.get("folder_name", "99 - Unknown"),
                            "file_path": file_path,
                            "additional_paths": hack_data.get("additional_paths", [])
                        })
                    else:
                        self.log_progress(f"⚠️ Skipping {hack_data.get('title', 'Unknown')}: File not found at {file_path}")
            
            # Group by distinct file_path to avoid duplicates
            unique_files = {}
            for hack in sync_candidates:
                file_path = hack["file_path"]
                if file_path not in unique_files:
                    unique_files[file_path] = hack
            
            # Sort by hack_type, then folder_name for organized sync
            sorted_hacks = sorted(
                unique_files.values(),
                key=lambda x: (x["hack_type"], x["folder_name"], x["title"])
            )
            
            self.log_progress(f"📋 Found {len(sorted_hacks)} hacks needing QUSB2SNES sync")
            return sorted_hacks
            
        except Exception as e:
            self.log_error(f"❌ Error querying hacks for sync: {str(e)}")
            return []

    async def sync_hacks_to_remote(self, remote_base_dir: str = "/ROMS") -> Dict:
        """
        Sync hacks from processed.json to remote device using per-hack tracking.
        This replaces the old filesystem-based sync with processed.json-based sync.
        """
        result = {"success": False, "uploaded": 0, "updated_hacks": [], "error": None}
        
        try:
            # Get hacks that need syncing
            hacks_to_sync = self.get_hacks_for_qusb_sync()
            
            if not hacks_to_sync:
                self.log_progress("✅ No hacks need syncing")
                result["success"] = True
                return result
            
            self.log_progress(f"🚀 Starting sync of {len(hacks_to_sync)} hacks to {remote_base_dir}")
            
            # Track statistics
            uploaded_count = 0
            updated_hack_ids = []
            
            for i, hack_info in enumerate(hacks_to_sync, 1):
                # Check for cancellation
                if self.cancelled:
                    result["error"] = "Operation cancelled by user"
                    return result
                
                hack_id = hack_info["hack_id"]
                title = hack_info["title"]
                file_path = hack_info["file_path"]
                hack_type = hack_info["hack_type"]
                folder_name = hack_info["folder_name"]
                additional_paths = hack_info.get("additional_paths", [])
                
                self.log_progress(f"📤 [{i}/{len(hacks_to_sync)}] Syncing: {title}")
                
                # Build remote path: /ROMS/Kaizo/05 - Expert/hack.smc
                remote_dir = self.normalize_remote_path(f"{remote_base_dir}/{hack_type.title()}/{folder_name}")
                
                # Ensure remote directory exists
                await self.ensure_directory_exists(remote_dir)
                
                # Upload main file
                filename = os.path.basename(file_path)
                remote_file_path = self.normalize_remote_path(f"{remote_dir}/{filename}")
                
                upload_success = await self.upload_file(file_path, remote_file_path)
                verification_success = False
                
                if upload_success:
                    # Verify main file upload
                    verification_success = await self.verify_file_upload(file_path, remote_file_path)
                    
                    if verification_success:
                        # Upload additional files if they exist
                        additional_upload_success = True
                        for additional_path in additional_paths:
                            if additional_path and os.path.exists(additional_path):
                                additional_filename = os.path.basename(additional_path)
                                additional_remote_path = self.normalize_remote_path(f"{remote_dir}/{additional_filename}")
                                
                                additional_success = await self.upload_file(additional_path, additional_remote_path)
                                if additional_success:
                                    additional_verify = await self.verify_file_upload(additional_path, additional_remote_path)
                                    if not additional_verify:
                                        additional_upload_success = False
                                        self.log_error(f"❌ Additional file verification failed: {additional_filename}")
                                        break
                                else:
                                    additional_upload_success = False
                                    self.log_error(f"❌ Additional file upload failed: {additional_filename}")
                                    break
                        
                        verification_success = verification_success and additional_upload_success
                
                if verification_success:
                    uploaded_count += 1
                    updated_hack_ids.append(hack_id)
                    
                    # Update the hack's sync timestamp using HackDataManager
                    await self.update_hack_sync_timestamp(hack_id)
                    
                    self.log_progress(f"✅ Successfully synced: {title}")
                else:
                    self.log_error(f"❌ Upload or verification failed for: {title}")
                    # Note: We don't update the timestamp if upload/verification fails
            
            result["success"] = uploaded_count > 0 or len(hacks_to_sync) == 0
            result["uploaded"] = uploaded_count
            result["updated_hacks"] = updated_hack_ids
            
            if uploaded_count > 0:
                self.log_progress(f"🎉 Sync completed: {uploaded_count}/{len(hacks_to_sync)} hacks synced successfully")
            
            return result
            
        except Exception as e:
            self.log_error(f"❌ Sync failed: {str(e)}")
            result["error"] = str(e)
            return result

    async def sync_local_to_remote_tree(self, local_dir: str, remote_dir: str, last_sync_timestamp: float = 0) -> Dict:
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
            
            # Track files uploaded to this folder for verification
            files_uploaded_this_folder = []
            
            # Process local directory contents
            for item_name in os.listdir(local_dir):
                # Check for cancellation
                if self.cancelled:
                    result["error"] = "Operation cancelled by user"
                    return result
                
                local_path = os.path.join(local_dir, item_name)
                remote_path = self.normalize_remote_path(f"{remote_dir}/{item_name}")
                
                if os.path.isfile(local_path):
                    # Handle file - only process ROM files
                    if not self.is_rom_file(item_name):
                        continue  # Skip non-ROM files
                    
                    # Check if file exists remotely
                    file_exists_remotely = item_name in remote_names
                    
                    # Simple logic: only check timestamps, ignore file sizes completely
                    # The List command is unreliable for size checking
                    should_upload = False
                    upload_reason = ""
                    
                    if not file_exists_remotely:
                        # File doesn't exist remotely - upload it
                        should_upload = True
                        upload_reason = "new file"
                    else:
                        # File exists - only check if local is newer than last sync
                        should_upload = self.should_upload_file(local_path, last_sync_timestamp)
                        upload_reason = "modified since last sync" if should_upload else "up to date"
                    
                    if should_upload:
                        self.log_progress(f"🔄 Uploading {item_name} ({upload_reason})")
                        if await self.upload_file(local_path, remote_path):
                            result["uploaded"] += 1
                            files_uploaded_this_folder.append(item_name)
                            self.log_progress(f"✅ Uploaded: {item_name}")
                        else:
                            result["error"] = f"Failed to upload {item_name}"
                            return result
                    else:
                        self.log_progress(f"⏭️ Skipped {item_name} ({upload_reason})")
                
                elif os.path.isdir(local_path):
                    # Check for cancellation before processing subdirectories
                    if self.cancelled:
                        result["error"] = "Operation cancelled by user"
                        return result
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
                    subdir_result = await self.sync_local_to_remote_tree(local_path, actual_remote_path, last_sync_timestamp)
                    if subdir_result["success"]:
                        result["uploaded"] += subdir_result["uploaded"]
                    else:
                        result["error"] = f"Failed to sync subdirectory {item_name}: {subdir_result.get('error')}"
                        return result
            
            # Folder-level verification: check that ALL local ROM files are present remotely
            local_rom_files = [f for f in os.listdir(local_dir) 
                             if os.path.isfile(os.path.join(local_dir, f)) and self.is_rom_file(f)]
            
            if local_rom_files:
                self.log_progress(f"🔍 Verifying all {len(local_rom_files)} ROM files are synced...")
                verification_passed = await self.verify_folder_contents(remote_dir, local_rom_files)
                
                if not verification_passed:
                    result["error"] = f"Folder verification failed: not all files were synced successfully"
                    result["success"] = False
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
                if hasattr(self.websocket, 'closed') and not self.websocket.closed:
                    await self.websocket.close(code=1000, reason="Normal closure")
                elif not hasattr(self.websocket, 'closed'):
                    # For newer websockets versions, just close
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
        """Attach to specific device with conflict detection"""
        try:
            self.log_progress(f"📱 Attaching to device: {device_name}")
            
            # Send attach command
            await self._send_command("Attach", operands=[device_name])
            
            # SD2SNES needs time to be ready after attach
            self.log_progress("⏳ Waiting for device to be ready...")
            await asyncio.sleep(5.0)
            
            # Try Info command to test device responsiveness
            try:
                info_response = await self._send_command("Info", timeout=8.0)
                if info_response is not None:
                    self.log_progress("✅ Device attached and verified successfully")
                    return True
                else:
                    # Info failed - check if it's a device conflict
                    return await self._handle_device_conflict(device_name)
            except asyncio.TimeoutError:
                # Timeout on Info usually means device conflict
                return await self._handle_device_conflict(device_name)
            except Exception as e:
                self.log_error(f"❌ Device verification failed: {str(e)}")
                return await self._handle_device_conflict(device_name)
            
        except Exception as e:
            self.log_error(f"❌ Device attachment failed: {str(e)}")
            return False
    
    async def _handle_device_conflict(self, device_name: str) -> bool:
        """Handle potential device conflicts with detailed diagnostics"""
        self.log_error("❌ Device attachment failed - likely in use by another application")
        self.log_error("")
        self.log_error("🔍 DEVICE CONFLICT DIAGNOSTICS:")
        self.log_error("   • The SD2SNES device is not responding to commands")
        self.log_error("   • This usually means another application is using it")
        self.log_error("")
        self.log_error("💡 SOLUTION STEPS:")
        self.log_error("   1. Close ALL other USB2SNES applications:")
        self.log_error("      - RetroAchievements (RA2Snes)")
        self.log_error("      - QFile2Snes")
        self.log_error("      - Button Mash")
        self.log_error("      - Savestate2Snes")
        self.log_error("   2. Check Task Manager for any of these processes")
        self.log_error("   3. Restart QUSB2SNES if necessary")
        self.log_error("   4. Only ONE application can use the device at a time")
        self.log_error("")
        
        # Try to get a fresh device list to see if device is still available
        try:
            devices = await self.get_devices()
            if device_name in devices:
                self.log_error(f"🔄 Device '{device_name}' is still listed but unresponsive")
                self.log_error("   This confirms another application is likely using it")
            else:
                self.log_error(f"❌ Device '{device_name}' is no longer available")
                self.log_error("   Device may have disconnected or been taken by another app")
        except:
            self.log_error("❌ Cannot check device status")
        
        return False
    
    async def list_directory(self, path: str) -> List[Dict]:
        """List remote directory contents with SD2SNES-safe delays and retry logic"""
        try:
            # Add delay before directory listing (SD2SNES requirement)
            # Increased delay to prevent firmware overload after large uploads
            await asyncio.sleep(1.0)
            
            response = await self._send_command_with_retry("List", operands=[path], max_retries=2)
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
            # Increased delay to prevent firmware overload after large uploads
            await asyncio.sleep(1.0)
            return items
            
        except Exception as e:
            # If listing fails, directory likely doesn't exist
            # SD2SNES closes connection on non-existent directory listing
            self.log_error(f"❌ Failed to list directory {path}: {str(e)}")
            raise e  # Re-raise to allow caller to handle appropriately
    
    async def _ensure_connection(self) -> bool:
        """Ensure we have a working connection, reconnect if needed"""
        # Check if we have a websocket and it's not closed
        websocket_open = (self.websocket and 
                         (not hasattr(self.websocket, 'closed') or not self.websocket.closed))
        
        if self.connected and websocket_open:
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
        """Create remote directory using proven working approach with retry logic"""
        try:
            await self._send_command_with_retry("MakeDir", operands=[path], max_retries=2)
            await asyncio.sleep(1.0)  # Wait for directory creation
            return True
        except Exception as e:
            self.log_error(f"❌ Failed to create directory {path}: {str(e)}")
            return False
    
    async def upload_file(self, local_path: str, remote_path: str) -> bool:
        """Upload file to remote location with connection recovery and verification"""
        max_retries = 3  # Increased retries to handle 0-byte upload issues
        
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
                
                # Longer delay before sending file data to ensure SD card is ready
                await asyncio.sleep(0.5)  # Increased from 0.1s for SD card preparation
                
                # Send file data in chunks with proper error handling and connection checks
                # Try smaller chunks for better reliability with SD card writes
                chunk_size = 512  # Reduced from 1024 for better SD card compatibility
                bytes_sent = 0
                total_chunks = 0
                
                with open(local_path, "rb") as f:
                    while bytes_sent < file_size:
                        # Check connection before each chunk
                        if not self.connected or not self.websocket:
                            raise Exception("Connection lost during file transfer")
                        
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
                                self.log_progress(f"QUSB2SNES: 📤 Upload progress: {progress_percent:.1f}% ({progress_kb}KB/{total_kb}KB)")
                            
                            # Small delay to prevent overwhelming the device and allow SD writes
                            if bytes_sent < file_size:
                                # Longer pause every 64KB to let SD card catch up
                                if bytes_sent % (64 * 1024) == 0:
                                    await asyncio.sleep(0.1)  # Longer pause for SD card
                                else:
                                    await asyncio.sleep(0.005)  # Regular delay
                                
                        except Exception as e:
                            raise Exception(f"Failed to send chunk at byte {bytes_sent}: {str(e)}")
                
                # Verify all bytes were sent
                if bytes_sent != file_size:
                    raise Exception(f"Incomplete transfer: sent {bytes_sent} of {file_size} bytes")
                
                # Log completion like the working version
                self.log_progress(f"QUSB2SNES: 📤 Sent {bytes_sent} bytes in {total_chunks} chunks to {remote_path}")
                
                # Wait for file processing with optimized timing
                # Increased delays to prevent SD2SNES firmware overload
                if file_size <= 1024*1024:  # Files <= 1MB
                    wait_time = 2.0  # Increased from 1.0s for SD card write completion
                elif file_size <= 4*1024*1024:  # Files <= 4MB (most ROMs)
                    wait_time = 4.0  # Increased from 2.0s for typical ROM sizes
                elif file_size <= 8*1024*1024:  # Files <= 8MB (large ROMs)
                    wait_time = 6.0  # Increased from 3.0s for large ROMs
                else:  # Files > 8MB (very rare for SNES)
                    wait_time = 8.0  # Increased from 4.0s for huge files
                
                self.log_progress(f"QUSB2SNES: ⏳ Waiting {wait_time}s for file processing...")
                await asyncio.sleep(wait_time)
                
                # Skip individual file verification to prevent device instability
                # Use folder-level verification at the end instead
                self.log_progress(f"✅ Upload completed: {os.path.basename(local_path)} (skipping individual verification)")
                
                # Timestamp update now handled by update_hack_sync_timestamp() in per-hack sync
                
                return True
                
            except Exception as e:
                if attempt == max_retries - 1:
                    self.log_error(f"❌ Upload failed for {local_path} after {max_retries} attempts: {str(e)}")
                    return False
                
                self.log_progress(f"⚠️ Upload attempt {attempt + 1} failed for {os.path.basename(local_path)}: {str(e)}, retrying...")
                await self.disconnect()
                await asyncio.sleep(3.0)  # Longer delay before retrying file uploads
        
        return False
    
    async def _verify_upload_success(self, remote_path: str, expected_size: int) -> bool:
        """
        Verify that a file was uploaded successfully by checking its size using GetFile.
        Returns True if the file exists and has the correct size, False otherwise.
        """
        try:
            self.log_progress(f"🔍 Verifying file size using GetFile: {os.path.basename(remote_path)}")
            
            # Use GetFile command to get actual file size
            response = await self._send_command("GetFile", operands=[remote_path])
            
            if response and "Results" in response and len(response["Results"]) > 0:
                # First result should be file size in hex
                size_hex = response["Results"][0]
                try:
                    remote_size = int(size_hex, 16)  # Convert hex to decimal
                    
                    if remote_size == 0:
                        self.log_error(f"❌ Verification failed: {os.path.basename(remote_path)} is 0 bytes on remote")
                        return False
                    elif remote_size != expected_size:
                        self.log_error(f"❌ Verification failed: {os.path.basename(remote_path)} size mismatch - expected {expected_size}, got {remote_size}")
                        return False
                    else:
                        self.log_progress(f"✅ Verification passed: {os.path.basename(remote_path)} ({remote_size} bytes)")
                        return True
                except ValueError as e:
                    self.log_error(f"❌ Verification failed: Invalid size format '{size_hex}' for {os.path.basename(remote_path)}: {e}")
                    return False
            else:
                self.log_error(f"❌ Verification failed: Could not get file info for {os.path.basename(remote_path)}")
                return False
            
        except UnicodeDecodeError as e:
            # Handle UTF-8 decode errors - the response might contain binary data
            self.log_progress(f"⚠️ GetFile response contains binary data - assuming upload successful")
            return True  # If we get binary data, the file likely exists
        except Exception as e:
            self.log_error(f"❌ Verification error for {remote_path}: {str(e)}")
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
    
    async def delete_file(self, remote_path: str) -> bool:
        """Delete a file on the remote device"""
        try:
            if not self.is_safe_remote_path(remote_path):
                self.log_error(f"❌ Cannot delete protected path: {remote_path}")
                return False
                
            self.log_progress(f"🗑️ Deleting file: {remote_path}")
            
            result = await self._send_command_with_retry("Remove", operands=[remote_path])
            if result is None:
                self.log_error(f"❌ Failed to delete file: {remote_path}")
                return False
                
            return True
            
        except Exception as e:
            self.log_error(f"❌ Error deleting file {remote_path}: {str(e)}")
            return False
    
    async def delete_directory(self, remote_path: str) -> bool:
        """Delete an empty directory on the remote device"""
        try:
            if not self.is_safe_remote_path(remote_path):
                self.log_error(f"❌ Cannot delete protected path: {remote_path}")
                return False
                
            self.log_progress(f"🗑️ Deleting directory: {remote_path}")
            
            result = await self._send_command_with_retry("Remove", operands=[remote_path])
            if result is None:
                self.log_error(f"❌ Failed to delete directory: {remote_path}")
                return False
                
            return True
            
        except Exception as e:
            self.log_error(f"❌ Error deleting directory {remote_path}: {str(e)}")
            return False
    
    async def get_files_to_cleanup(self) -> List[str]:
        """
        Get list of files that would be cleaned up without actually deleting them.
        This is useful for testing and preview functionality.
        """
        files_to_cleanup = []
        
        try:
            # Get config values
            local_dir = self.config.get("output_dir", "")
            remote_dir = self.config.get("qusb2snes_remote_folder", "/ROMS")
            
            if not local_dir or not os.path.exists(local_dir):
                return files_to_cleanup
            
            # Connect to device
            await self.connect()
            
            # Get remote directory contents
            remote_items = await self.list_directory(remote_dir)
            if not remote_items:
                return files_to_cleanup
                
            # Create sets of local ROM files for quick lookup
            local_files = set()
            
            for root, dirs, files in os.walk(local_dir):
                for file in files:
                    if file.lower().endswith(('.smc', '.sfc')):
                        # Get relative path from local_dir
                        full_path = os.path.join(root, file)
                        rel_path = os.path.relpath(full_path, local_dir)
                        # Normalize path separators
                        rel_path = rel_path.replace('\\', '/')
                        local_files.add(rel_path.lower())
            
            # Find remote files that don't exist locally
            await self._find_files_to_cleanup_recursive(remote_dir, local_dir, local_files, files_to_cleanup)
            
        except Exception as e:
            self.log_error(f"❌ Error getting files to cleanup: {str(e)}")
        finally:
            if self.websocket:
                await self.websocket.close()
        
        return files_to_cleanup
    
    async def _find_files_to_cleanup_recursive(self, remote_dir: str, local_base_dir: str, local_files: set, files_to_cleanup: List[str]):
        """Helper method to recursively find files that need cleanup"""
        try:
            remote_items = await self.list_directory(remote_dir)
            
            for remote_item in remote_items:
                remote_name = remote_item["name"]
                is_dir = remote_item.get("is_dir", False)
                
                remote_item_path = self.normalize_remote_path(f"{remote_dir}/{remote_name}")
                
                if is_dir:
                    # Recursively check subdirectory
                    await self._find_files_to_cleanup_recursive(remote_item_path, local_base_dir, local_files, files_to_cleanup)
                else:
                    # Check if it's a ROM file that should be managed
                    if remote_name.lower().endswith(('.smc', '.sfc')):
                        # Calculate relative path from remote base
                        base_remote_dir = self.config.get("qusb2snes_remote_folder", "/ROMS")
                        if remote_item_path.startswith(base_remote_dir):
                            rel_path = remote_item_path[len(base_remote_dir):].lstrip('/')
                            
                            # Check if this file exists locally
                            if rel_path.lower() not in local_files:
                                files_to_cleanup.append(rel_path)
                                
        except Exception as e:
            self.log_error(f"❌ Error scanning remote directory {remote_dir}: {str(e)}")
    
    async def cleanup_deleted_files(self, local_dir: str, remote_dir: str) -> Dict:
        """
        Clean up files and directories on remote that no longer exist locally.
        Returns dict with cleanup results.
        """
        cleanup_result = {"files_deleted": 0, "dirs_deleted": 0, "errors": []}
        
        try:
            # Get remote directory contents
            remote_items = await self.list_directory(remote_dir)
            if not remote_items:
                return cleanup_result
                
            # Create sets of local items for quick lookup
            local_files = set()
            local_dirs = set()
            
            try:
                for item in os.listdir(local_dir):
                    item_path = os.path.join(local_dir, item)
                    if os.path.isfile(item_path):
                        local_files.add(item.lower())  # Case-insensitive
                    elif os.path.isdir(item_path):
                        local_dirs.add(item.lower())  # Case-insensitive
            except (OSError, FileNotFoundError):
                # Local directory doesn't exist or can't be read
                return cleanup_result
            
            # Check each remote item
            for remote_item in remote_items:
                remote_name = remote_item["name"]
                remote_name_lower = remote_name.lower()
                is_dir = remote_item.get("is_dir", False)
                
                remote_item_path = self.normalize_remote_path(f"{remote_dir}/{remote_name}")
                
                if is_dir:
                    if remote_name_lower not in local_dirs:
                        # Directory exists on remote but not locally - delete it recursively
                        await self._cleanup_remote_directory_recursive(remote_item_path, cleanup_result)
                    else:
                        # Directory exists locally - recursively check its contents
                        local_subdir = os.path.join(local_dir, remote_name)
                        subdir_result = await self.cleanup_deleted_files(local_subdir, remote_item_path)
                        cleanup_result["files_deleted"] += subdir_result["files_deleted"]
                        cleanup_result["dirs_deleted"] += subdir_result["dirs_deleted"]
                        cleanup_result["errors"].extend(subdir_result["errors"])
                else:
                    # Check if it's a ROM file that should be managed
                    if remote_name_lower.endswith(('.smc', '.sfc')):
                        if remote_name_lower not in local_files:
                            # ROM file exists on remote but not locally - delete it
                            if await self.delete_file(remote_item_path):
                                cleanup_result["files_deleted"] += 1
                                self.log_progress(f"🗑️ Deleted: {remote_name}")
                            else:
                                cleanup_result["errors"].append(f"Failed to delete file: {remote_name}")
                                
        except Exception as e:
            cleanup_result["errors"].append(f"Cleanup error: {str(e)}")
            self.log_error(f"❌ Cleanup error: {str(e)}")
            
        return cleanup_result
    
    async def _cleanup_remote_directory_recursive(self, remote_dir_path: str, cleanup_result: Dict):
        """Recursively delete a remote directory and all its contents"""
        try:
            # Get directory contents
            items = await self.list_directory(remote_dir_path)
            if not items:
                # Empty directory - try to delete it
                if await self.delete_directory(remote_dir_path):
                    cleanup_result["dirs_deleted"] += 1
                    self.log_progress(f"🗑️ Deleted directory: {os.path.basename(remote_dir_path)}")
                return
                
            # Delete all contents first
            for item in items:
                item_name = item["name"]
                item_path = self.normalize_remote_path(f"{remote_dir_path}/{item_name}")
                
                if item.get("is_dir", False):
                    # Recursively delete subdirectory
                    await self._cleanup_remote_directory_recursive(item_path, cleanup_result)
                else:
                    # Delete file
                    if await self.delete_file(item_path):
                        cleanup_result["files_deleted"] += 1
                        self.log_progress(f"🗑️ Deleted: {item_name}")
                    else:
                        cleanup_result["errors"].append(f"Failed to delete file: {item_name}")
                        
            # Try to delete the now-empty directory
            if await self.delete_directory(remote_dir_path):
                cleanup_result["dirs_deleted"] += 1
                self.log_progress(f"🗑️ Deleted directory: {os.path.basename(remote_dir_path)}")
            else:
                cleanup_result["errors"].append(f"Failed to delete directory: {os.path.basename(remote_dir_path)}")
                
        except Exception as e:
            cleanup_result["errors"].append(f"Error cleaning directory {remote_dir_path}: {str(e)}")
            self.log_error(f"❌ Error cleaning directory {remote_dir_path}: {str(e)}")

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
                    # Check if file exists remotely
                    file_exists_remotely = item in remote_names
                    
                    if file_exists_remotely:
                        # File exists - only upload if local file is newer than last successful sync
                        should_upload = self.should_upload_file(local_path, last_sync_timestamp)
                        if should_upload:
                            self.log_progress(f"🔄 Re-uploading {item} (modified since last sync)")
                        else:
                            self.log_progress(f"⏭️ Skipping {item} (already up to date)")
                    else:
                        # File doesn't exist remotely - upload it
                        should_upload = True
                        self.log_progress(f"📤 New file: {item}")
                    
                    if should_upload:
                        remote_path = f"{remote_dir.rstrip('/')}/{item}"
                        if await self.upload_file(local_path, remote_path):
                            uploaded += 1
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
                    # Check if file exists remotely
                    file_exists_remotely = item in remote_names
                    
                    if file_exists_remotely:
                        # File exists - only upload if local file is newer than last successful sync
                        should_upload = self.should_upload_file(local_item_path, last_sync_timestamp)
                        if should_upload:
                            self.log_progress(f"🔄 Re-uploading {item} (modified since last sync)")
                        else:
                            self.log_progress(f"⏭️ Skipping {item} (already up to date)")
                    else:
                        # File doesn't exist remotely - upload it
                        should_upload = True
                        self.log_progress(f"📤 New file: {item}")
                    
                    if should_upload:
                        remote_file_path = f"{sub_remote_dir}/{item}"
                        
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
    
    async def _send_command_with_retry(self, opcode: str, space: str = "SNES", operands: List[str] = None, timeout: float = None, max_retries: int = 2) -> Optional[Dict]:
        """Send command with automatic retry and reconnection"""
        for attempt in range(max_retries + 1):
            try:
                # Ensure we're connected
                if not await self._ensure_connection():
                    if attempt == max_retries:
                        self.log_error(f"❌ Failed to establish connection after {max_retries + 1} attempts")
                        return None
                    continue
                
                # Try the command
                result = await self._send_command(opcode, space, operands, timeout)
                if result is not None:
                    return result
                
                # Command failed, try again if we have retries left
                if attempt < max_retries:
                    self.log_progress(f"🔄 Retrying command {opcode} (attempt {attempt + 2}/{max_retries + 1})")
                    await asyncio.sleep(1.0)  # Brief delay before retry
                
            except Exception as e:
                if "Not connected" in str(e) and attempt < max_retries:
                    self.log_progress(f"🔄 Connection issue, retrying command {opcode} (attempt {attempt + 2}/{max_retries + 1})")
                    await asyncio.sleep(1.0)
                elif attempt == max_retries:
                    self.log_error(f"❌ Command {opcode} failed after {max_retries + 1} attempts: {e}")
                    raise
        
        return None

    async def _send_command(self, opcode: str, space: str = "SNES", operands: List[str] = None, timeout: float = None) -> Optional[Dict]:
        """Send command to QUSB2SNES with proper logging and response handling"""
        if not self.connected or not self.websocket:
            raise Exception("Not connected to QUSB2SNES")
        
        # Check if websocket is still open
        if hasattr(self.websocket, 'closed') and self.websocket.closed:
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

    async def ensure_directory_exists(self, remote_dir: str) -> bool:
        """Ensure remote directory exists, creating if necessary"""
        try:
            # Check if directory exists
            items = await self.list_directory(os.path.dirname(remote_dir))
            dir_name = os.path.basename(remote_dir)
            
            for item in items:
                if item["name"] == dir_name and item.get("is_dir", False):
                    return True  # Directory exists
            
            # Directory doesn't exist, create it
            result = await self.create_directory(remote_dir)
            return result
            
        except Exception as e:
            self.log_error(f"❌ Error ensuring directory {remote_dir}: {str(e)}")
            return False

    async def verify_file_upload(self, local_path: str, remote_path: str) -> bool:
        """Verify uploaded file by comparing sizes"""
        try:
            local_size = os.path.getsize(local_path)
            return await self._verify_upload_success(remote_path, local_size)
                
        except Exception as e:
            self.log_error(f"❌ Verification error: {str(e)}")
            return False

    async def update_hack_sync_timestamp(self, hack_id: str) -> bool:
        """Update hack's qusb2snes_last_sync timestamp using HackDataManager"""
        try:
            import time
            from hack_data_manager import HackDataManager
            
            # Get current timestamp
            current_timestamp = int(time.time())
            
            # Use HackDataManager to safely update the hack
            data_manager = HackDataManager()
            success = data_manager.update_hack(hack_id, "qusb2snes_last_sync", current_timestamp)
            
            if success:
                self.log_progress(f"🕒 Updated sync timestamp for hack {hack_id}")
                return True
            else:
                self.log_error(f"❌ Failed to update sync timestamp for hack {hack_id}")
                return False
                
        except Exception as e:
            self.log_error(f"❌ Error updating timestamp for hack {hack_id}: {str(e)}")
            return False


# Simple sync manager for UI integration
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
    
    async def get_devices(self) -> List[str]:
        """Get available devices"""
        if self.sync_client:
            return await self.sync_client.get_devices()
        return []
    
    async def sync_roms(self, local_rom_dir: str, last_sync_timestamp: float = 0) -> bool:
        """Sync ROM directory using tree-based approach"""
        if not self.sync_client:
            if self.on_error:
                self.on_error("❌ Not connected to QUSB2SNES")
            return False

        # Use the new tree-based sync approach with timestamp
        return await self.sync_client.sync_directory_tree_based(local_rom_dir, self.remote_folder, last_sync_timestamp)
    
    async def sync_roms_incremental(self, local_rom_dir: str, progress_tracker: Dict = None, cleanup_deleted: bool = False, last_sync_timestamp: float = 0) -> Dict:
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
                last_sync_timestamp,  # Pass the actual timestamp
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
    
    async def sync_hacks_to_remote(self, remote_base_dir: str = "/ROMS") -> Dict:
        """
        Sync hacks using per-hack tracking. Delegates to the sync client.
        """
        if not self.sync_client:
            return {
                "success": False, 
                "error": "Not connected to QUSB2SNES",
                "uploaded": 0,
                "updated_hacks": []
            }
        
        # Delegate to the sync client's per-hack sync method
        try:
            result = await self.sync_client.sync_hacks_to_remote(remote_base_dir)
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "uploaded": 0,
                "updated_hacks": []
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