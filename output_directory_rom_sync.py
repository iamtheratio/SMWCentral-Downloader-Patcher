#!/usr/bin/env python3
"""
Output Directory Based ROM Sync with Smart Timestamp Comparison

This implements the complete sync strategy:
1. Scan the output ROM folder (from settings) to get ALL ROM files
2. For each ROM file, check if it exists in processed.json (only obsolete = false entries)
3. Compare timestamps:
   - If qusb_last_sync > local file modified date: skip (already uploaded newer version)
   - If qusb_last_sync = 0 or < local file modified date OR not in processed.json: upload
4. After upload: if ROM exists in processed.json, update qusb_last_sync timestamp

This syncs ALL files in the output directory, not just those in processed.json,
but uses processed.json for smart timestamp tracking to avoid re-uploading unchanged files.
"""

import asyncio
import os
import json
import time
from typing import List, Dict, Optional
from pathlib import Path
from config_manager import ConfigManager
from hack_data_manager import HackDataManager
from utils import load_processed

# Import V2 components  
from qusb2snes_connection import QUSB2SNESConnection
from qusb2snes_device import QUSB2SNESDevice
from qusb2snes_upload_v2_adapter import QUSB2SNESUploadManager

class OutputDirectoryROMSync:
    """
    ROM Sync based on scanning the output directory and matching against processed.json
    
    Flow:
    1. Scan output_dir for ROM files (.smc/.sfc)
    2. For each ROM file, find matching entry in processed.json
    3. Check if obsolete = false AND qusb2snes_last_sync = 0
    4. Upload qualifying files
    5. Update qusb2snes_last_sync timestamps after successful uploads
    """
    
    def __init__(self):
        self.config = ConfigManager()
        self.hack_data_manager = HackDataManager()
        
        # V2 components
        self.connection = QUSB2SNESConnection()
        self.device_manager = QUSB2SNESDevice(self.connection)
        self.upload_manager = QUSB2SNESUploadManager(
            connection=self.connection, 
            device_manager=self.device_manager, 
            filesystem_manager=None,
            config_manager=self.config
        )
        
    def log_info(self, message: str):
        """Log information message"""
        print(f"[OutputDirSync] {message}")
    
    def log_error(self, message: str):
        """Log error message"""
        print(f"[OutputDirSync] ERROR: {message}")
    
    def scan_output_directory(self) -> List[Dict]:
        """
        Scan the output directory for ROM files
        
        Returns:
            List of dicts with file info: {
                "local_path": full path to ROM file,
                "filename": just the filename,
                "relative_path": path relative to output_dir,
                "category": extracted from path (Kaizo, Traditional, etc.),
                "difficulty": extracted from path
            }
        """
        output_dir = self.config.get("output_dir", "")
        if not output_dir:
            self.log_error("No output directory configured in settings")
            return []
        
        if not os.path.exists(output_dir):
            self.log_error(f"Output directory does not exist: {output_dir}")
            return []
        
        self.log_info(f"Scanning output directory: {output_dir}")
        
        rom_files = []
        rom_extensions = ('.smc', '.sfc')
        
        try:
            for root, dirs, files in os.walk(output_dir):
                for filename in files:
                    if filename.lower().endswith(rom_extensions):
                        local_path = os.path.join(root, filename)
                        relative_path = os.path.relpath(local_path, output_dir)
                        
                        # Extract category and difficulty from path structure
                        # Expected structure: output_dir/Category/Difficulty/filename.smc
                        path_parts = relative_path.split(os.sep)
                        category = path_parts[0] if len(path_parts) > 1 else "Unknown"
                        difficulty = path_parts[1] if len(path_parts) > 2 else "Unknown"
                        
                        rom_files.append({
                            "local_path": local_path,
                            "filename": filename,
                            "relative_path": relative_path,
                            "category": category,
                            "difficulty": difficulty
                        })
        
        except Exception as e:
            self.log_error(f"Error scanning output directory: {e}")
            return []
        
        self.log_info(f"Found {len(rom_files)} ROM files in output directory")
        return rom_files
    
    def evaluate_files_for_sync(self, rom_files: List[Dict]) -> List[Dict]:
        """
        Evaluate which ROM files need syncing based on timestamp comparison with processed.json
        
        Logic:
        1. Get all ROM files from output directory
        2. For each file, check if it exists in processed.json (only obsolete = false entries)
        3. Compare local file modified time vs qusb_last_sync timestamp
        4. Upload if: no processed.json entry OR qusb_last_sync = 0 OR qusb_last_sync < file modified time
        
        Args:
            rom_files: List of ROM file dicts from scan_output_directory()
            
        Returns:
            List of ROM files that need syncing (ALL files get evaluated, not just processed.json matches)
        """
        try:
            processed_data = load_processed()
            sync_candidates = []
            
            self.log_info(f"Evaluating {len(rom_files)} ROM files for sync...")
            
            for rom_file in rom_files:
                filename = rom_file["filename"]
                local_path = rom_file["local_path"]
                
                # Get local file modification time
                try:
                    local_mtime = os.path.getmtime(local_path)
                except OSError:
                    self.log_error(f"Cannot get modification time for {local_path}")
                    continue
                
                # Look for matching entry in processed.json (only non-obsolete entries)
                matching_hack_id = None
                matching_hack_data = None
                
                # Strategy 1: Match by file_path (exact path match)
                for hack_id, hack_data in processed_data.items():
                    if not isinstance(hack_data, dict):
                        continue
                    
                    # Skip obsolete entries
                    if hack_data.get("obsolete", False):
                        continue
                    
                    stored_file_path = hack_data.get("file_path", "")
                    if stored_file_path and os.path.normpath(stored_file_path) == os.path.normpath(local_path):
                        matching_hack_id = hack_id
                        matching_hack_data = hack_data
                        break
                
                # Strategy 2: Match by filename (if exact path match failed)
                if not matching_hack_id:
                    for hack_id, hack_data in processed_data.items():
                        if not isinstance(hack_data, dict):
                            continue
                        
                        # Skip obsolete entries
                        if hack_data.get("obsolete", False):
                            continue
                        
                        stored_file_path = hack_data.get("file_path", "")
                        if stored_file_path and os.path.basename(stored_file_path) == filename:
                            matching_hack_id = hack_id
                            matching_hack_data = hack_data
                            break
                
                # Strategy 3: Match by title (convert filename to title format)
                if not matching_hack_id:
                    file_title = os.path.splitext(filename)[0]
                    
                    for hack_id, hack_data in processed_data.items():
                        if not isinstance(hack_data, dict):
                            continue
                        
                        # Skip obsolete entries
                        if hack_data.get("obsolete", False):
                            continue
                        
                        stored_title = hack_data.get("title", "")
                        if stored_title and stored_title.lower() in file_title.lower():
                            matching_hack_id = hack_id
                            matching_hack_data = hack_data
                            break
                
                # Determine if file needs syncing
                needs_sync = False
                sync_reason = ""
                
                if matching_hack_data:
                    # File exists in processed.json (non-obsolete)
                    qusb_last_sync = matching_hack_data.get("qusb2snes_last_sync", 0)
                    
                    if qusb_last_sync == 0:
                        needs_sync = True
                        sync_reason = "never synced"
                    elif qusb_last_sync < local_mtime:
                        needs_sync = True
                        sync_reason = "file modified since last sync"
                    else:
                        needs_sync = False
                        sync_reason = "already up to date"
                    
                    # Add processed.json info to ROM file data
                    rom_file["hack_id"] = matching_hack_id
                    rom_file["hack_title"] = matching_hack_data.get("title", "Unknown")
                    rom_file["hack_type"] = matching_hack_data.get("hack_type", "standard")
                    rom_file["folder_name"] = matching_hack_data.get("folder_name", "99 - Unknown")
                    rom_file["in_processed_json"] = True
                    
                else:
                    # File NOT in processed.json - always sync
                    needs_sync = True
                    sync_reason = "not in processed.json"
                    
                    # Use defaults for non-processed.json files
                    rom_file["hack_id"] = None
                    rom_file["hack_title"] = os.path.splitext(filename)[0]  # Use filename as title
                    rom_file["hack_type"] = rom_file["category"].lower() if rom_file["category"] != "Unknown" else "standard"
                    rom_file["folder_name"] = rom_file["difficulty"] if rom_file["difficulty"] != "Unknown" else "99 - Unknown"
                    rom_file["in_processed_json"] = False
                
                # Log decision
                if needs_sync:
                    self.log_info(f"✓ Will sync: {filename} ({sync_reason})")
                    sync_candidates.append(rom_file)
                else:
                    self.log_info(f"⏭️ Skipping: {filename} ({sync_reason})")
            
            self.log_info(f"Found {len(sync_candidates)} files needing sync")
            return sync_candidates
            
        except Exception as e:
            self.log_error(f"Error evaluating files for sync: {e}")
            return []
    
    async def update_hack_sync_timestamp(self, hack_id: str) -> bool:
        """Update hack's qusb2snes_last_sync timestamp (only if hack exists in processed.json)"""
        if not hack_id:
            # No hack_id means file is not in processed.json - skip timestamp update
            return True
            
        try:
            current_timestamp = int(time.time())
            success = self.hack_data_manager.update_hack(hack_id, "qusb2snes_last_sync", current_timestamp)
            
            if success:
                self.log_info(f"🕒 Updated sync timestamp for hack {hack_id}")
                return True
            else:
                self.log_error(f"❌ Failed to update sync timestamp for hack {hack_id}")
                return False
                
        except Exception as e:
            self.log_error(f"❌ Error updating timestamp for hack {hack_id}: {e}")
            return False
    
    async def connect(self) -> bool:
        """Connect to QUSB2SNES and attach device"""
        self.log_info("Connecting to QUSB2SNES...")
        
        if not await self.connection.connect():
            self.log_error("Failed to connect to QUSB2SNES server")
            return False
        
        self.log_info("Detecting devices...")
        devices = await self.device_manager.discover_devices()
        if not devices:
            self.log_error("No SD2SNES devices detected")
            await self.connection.disconnect()
            return False
        
        # Attach to first available device
        device_name = devices[0].name
        if not await self.device_manager.attach_device(device_name):
            self.log_error(f"Failed to attach to device: {device_name}")
            await self.connection.disconnect()
            return False
        
        self.log_info(f"✅ Connected to device: {device_name}")
        return True
    
    async def disconnect(self):
        """Disconnect from QUSB2SNES"""
        await self.connection.disconnect()
        self.log_info("Disconnected from QUSB2SNES")
    
    async def sync_rom_files(self, remote_base_dir: str = "/ROMS") -> Dict:
        """
        Complete sync process: scan directory -> match with processed.json -> upload -> update timestamps
        
        Returns:
            Dict with sync results: {
                "success": bool,
                "scanned": int,
                "matched": int, 
                "uploaded": int,
                "updated_hacks": List[str],
                "error": Optional[str]
            }
        """
        result = {
            "success": False,
            "scanned": 0,
            "matched": 0,
            "uploaded": 0,
            "updated_hacks": [],
            "error": None
        }
        
        try:
            # Step 1: Scan output directory for ROM files
            self.log_info("🔍 Step 1: Scanning output directory for ROM files...")
            rom_files = self.scan_output_directory()
            result["scanned"] = len(rom_files)
            
            if not rom_files:
                result["success"] = True  # No files to sync is success
                self.log_info("✅ No ROM files found in output directory")
                return result
            
            # Step 2: Evaluate files for sync based on timestamp comparison
            self.log_info("🔗 Step 2: Evaluating files for sync (timestamp comparison)...")
            sync_candidates = self.evaluate_files_for_sync(rom_files)
            result["matched"] = len(sync_candidates)
            
            if not sync_candidates:
                result["success"] = True  # No files need sync is success
                self.log_info("✅ No files need syncing (all up to date or obsolete)")
                return result
            
            # Step 3: Upload files
            self.log_info(f"📤 Step 3: Uploading {len(sync_candidates)} files...")
            
            uploaded_count = 0
            updated_hack_ids = []
            
            for i, rom_file in enumerate(sync_candidates, 1):
                local_path = rom_file["local_path"]
                filename = rom_file["filename"]
                hack_id = rom_file["hack_id"]
                hack_title = rom_file["hack_title"]
                hack_type = rom_file["hack_type"]
                folder_name = rom_file["folder_name"]
                
                self.log_info(f"📤 [{i}/{len(sync_candidates)}] Uploading: {hack_title}")
                
                # Build remote path: /ROMS/Kaizo/05 - Expert/hack.smc
                remote_dir = f"{remote_base_dir}/{hack_type.title()}/{folder_name}"
                remote_file_path = f"{remote_dir}/{filename}"
                
                # Upload using V2 upload manager
                upload_success = await self.upload_manager.upload_file(local_path, remote_file_path)
                
                if upload_success:
                    uploaded_count += 1
                    updated_hack_ids.append(hack_id)
                    
                    # Update sync timestamp only if file is in processed.json
                    if rom_file["in_processed_json"]:
                        await self.update_hack_sync_timestamp(hack_id)
                        self.log_info(f"✅ Uploaded & updated timestamp: {hack_title}")
                    else:
                        self.log_info(f"✅ Uploaded (not in processed.json): {hack_title}")
                else:
                    self.log_error(f"❌ Failed to upload: {hack_title}")
            
            result["uploaded"] = uploaded_count
            result["updated_hacks"] = updated_hack_ids
            result["success"] = uploaded_count > 0 or len(sync_candidates) == 0
            
            if uploaded_count > 0:
                self.log_info(f"🎉 Sync completed: {uploaded_count}/{len(sync_candidates)} files uploaded successfully")
            else:
                self.log_error(f"❌ No files were uploaded successfully")
            
            return result
            
        except Exception as e:
            self.log_error(f"Sync failed: {e}")
            result["error"] = str(e)
            return result

async def test_output_directory_sync():
    """Test the output directory based sync approach"""
    print("🧪 Testing Output Directory Based ROM Sync")
    print("=" * 60)
    
    sync_manager = OutputDirectoryROMSync()
    
    try:
        # Test Step 1: Directory scanning
        print("\n📁 Testing directory scanning...")
        rom_files = sync_manager.scan_output_directory()
        print(f"✅ Found {len(rom_files)} ROM files")
        
        if rom_files:
            print("\nSample files:")
            for rom_file in rom_files[:3]:  # Show first 3
                print(f"  📄 {rom_file['filename']} ({rom_file['category']}/{rom_file['difficulty']})")
            if len(rom_files) > 3:
                print(f"     ... and {len(rom_files) - 3} more")
        
        # Test Step 2: Evaluate files for sync
        print("\n🔗 Testing file evaluation for sync...")
        sync_candidates = sync_manager.evaluate_files_for_sync(rom_files)
        print(f"✅ Found {len(sync_candidates)} files needing sync")
        
        if sync_candidates:
            print("\nFiles ready for sync:")
            for candidate in sync_candidates[:3]:  # Show first 3
                in_processed = "📝" if candidate["in_processed_json"] else "📄"
                print(f"  🎯 {candidate['hack_title']} ({candidate['filename']}) {in_processed}")
            if len(sync_candidates) > 3:
                print(f"     ... and {len(sync_candidates) - 3} more")
            
            # Show breakdown
            in_processed_count = sum(1 for c in sync_candidates if c["in_processed_json"])
            not_in_processed_count = len(sync_candidates) - in_processed_count
            print(f"\n📊 Breakdown: {in_processed_count} in processed.json, {not_in_processed_count} not in processed.json")
        
        # Test Step 3: Connection test
        print("\n🔗 Testing QUSB2SNES connection...")
        if await sync_manager.connect():
            print("✅ Connected successfully")
            
            # Test Step 4: Full sync (if user confirms)
            if sync_candidates:
                print(f"\n⚠️ Ready to upload {len(sync_candidates)} files to SD2SNES device")
                response = input("Proceed with actual upload? (y/N): ").strip().lower()
                
                if response == 'y':
                    print("\n🚀 Starting full sync...")
                    result = await sync_manager.sync_rom_files()
                    
                    if result["success"]:
                        print(f"🎉 Sync completed successfully!")
                        print(f"📊 Results: {result['uploaded']}/{result['matched']} files uploaded")
                    else:
                        print(f"❌ Sync failed: {result.get('error', 'Unknown error')}")
                else:
                    print("ℹ️ Skipping actual upload")
            else:
                print("ℹ️ No files need syncing")
            
            await sync_manager.disconnect()
        else:
            print("⚠️ Could not connect to QUSB2SNES - skipping upload test")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(test_output_directory_sync())