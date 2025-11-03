#!/usr/bin/env python3
"""
Simple ROM Uploader Using Working Sync
Uses proven qusb2snes_sync.py patterns instead of complex V2 architecture
"""

import asyncio
import json
import os
import tempfile
from datetime import datetime
from pathlib import Path
from typing import List, Tuple

from qusb2snes_sync import QUSB2SNESSync


class SimpleROMUploader:
    """
    Simple ROM uploader using proven working sync patterns
    No complex retry logic, state management, or connection recovery
    """
    
    def __init__(self, host="localhost", port=23074):
        self.sync = QUSB2SNESSync(host, port)
        self.processed_json_path = "processed.json"
    
    def create_file_list(self, source_directory: str, target_base_path: str = "/qusb_sync") -> List[Tuple[str, str]]:
        """Create list of (local_path, remote_path) tuples"""
        files = []
        
        for root, dirs, filenames in os.walk(source_directory):
            for filename in filenames:
                if filename.lower().endswith(('.smc', '.sfc', '.bin')):
                    local_path = os.path.join(root, filename)
                    
                    # Skip large files
                    if os.path.getsize(local_path) > 5 * 1024 * 1024:
                        continue
                    
                    # Create remote path
                    rel_path = os.path.relpath(local_path, source_directory)
                    remote_path = f"{target_base_path}/{rel_path.replace(os.sep, '/')}"
                    
                    files.append((local_path, remote_path))
        
        return files
    
    async def upload_file_simple(self, local_path: str, remote_path: str) -> bool:
        """
        Upload single file using working sync pattern
        No complex retry logic - fail fast and clean
        """
        try:
            # Ensure remote directory exists
            remote_dir = str(Path(remote_path).parent)
            if remote_dir != "/" and remote_dir != ".":
                success = await self.sync.ensure_directory_exists(remote_dir)
                if not success:
                    return False
            
            # Upload file using working sync method
            success = await self.sync.upload_file(local_path, remote_path)
            
            # Update processed.json if successful
            if success:
                filename = os.path.basename(local_path)
                self.update_qusb_last_sync(filename)
            
            return success
            
        except Exception as e:
            print(f"❌ Upload failed: {e}")
            return False
    
    async def upload_rom_list(self, file_list: List[Tuple[str, str]]) -> dict:
        """
        Upload list of ROMs sequentially using working sync
        Simple foreach loop - no complex batch logic
        """
        results = {}
        
        try:
            # Single connection for entire session
            if not await self.sync.connect():
                print("❌ Failed to connect to QUsb2snes")
                return results
            
            # Get and attach device (simple)
            devices = await self.sync.get_devices()
            if not devices:
                print("❌ No devices found")
                return results
            
            if not await self.sync.attach_device(devices[0]):
                print(f"❌ Failed to attach to {devices[0]}")
                return results
            
            print(f"✅ Connected and attached to {devices[0]}")
            
            # Upload each file sequentially
            for i, (local_path, remote_path) in enumerate(file_list):
                print(f"📤 Uploading {i+1}/{len(file_list)}: {os.path.basename(local_path)}")
                
                success = await self.upload_file_simple(local_path, remote_path)
                results[remote_path] = success
                
                if success:
                    print(f"✅ Upload successful: {os.path.basename(local_path)}")
                else:
                    print(f"❌ Upload failed: {os.path.basename(local_path)}")
                
                # Brief pause between files
                await asyncio.sleep(0.2)
        
        finally:
            # CRITICAL: Always clean up
            await self.sync.disconnect()
        
        return results
    
    def update_qusb_last_sync(self, filename: str) -> bool:
        """Update qusb_last_sync in processed.json"""
        try:
            if not os.path.exists(self.processed_json_path):
                return False
            
            with open(self.processed_json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Find and update matching entry
            for entry in data.values():
                if isinstance(entry, dict) and entry.get('filename') == filename:
                    entry['qusb_last_sync'] = datetime.now().isoformat()
                    break
            else:
                return False
            
            with open(self.processed_json_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception:
            return False


async def test_simple_rom_upload():
    """Test the simple ROM uploader"""
    print("🚀 Testing Simple ROM Upload with Working Sync")
    
    # Create test file
    temp_dir = tempfile.mkdtemp(prefix="simple_rom_test_")
    test_file = os.path.join(temp_dir, "working_test.smc")
    
    with open(test_file, "wb") as f:
        f.write(b"SMC" + b"T" * 1021)  # 1KB test
    
    try:
        # Test the simple uploader
        uploader = SimpleROMUploader()
        file_list = uploader.create_file_list(temp_dir, "/working_test")
        
        if not file_list:
            print("❌ No files found")
            return False
        
        print(f"📋 Found {len(file_list)} files to upload")
        
        # Upload using working sync
        results = await uploader.upload_rom_list(file_list)
        
        # Check results
        success_count = sum(1 for success in results.values() if success)
        print(f"📊 Results: {success_count}/{len(results)} successful")
        
        return success_count == len(results)
        
    finally:
        # Cleanup test files
        import shutil
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)


if __name__ == "__main__":
    success = asyncio.run(test_simple_rom_upload())
    if success:
        print("\n🎉 Simple ROM upload with working sync PASSED!")
    else:
        print("\n❌ Simple ROM upload with working sync FAILED!")