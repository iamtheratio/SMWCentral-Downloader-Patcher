#!/usr/bin/env python3
"""
QUSB2SNES ROM Uploader - Simple Sequential Processing
Following microservice and TDD principles - keep it simple!

Key Features:
- Generate list of files to upload
- Process each ROM one at a time (foreach loop)
- Ensure folder exists before upload
- Upload file
- Update qusb_last_sync in processed.json if matching entry exists
- Move to next ROM
"""

import asyncio
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple


class ROMUploader:
    """Simple ROM uploader following microservice principles"""
    
    def __init__(self, upload_manager, filesystem_manager, processed_json_path="processed.json"):
        self.upload_manager = upload_manager
        self.filesystem_manager = filesystem_manager
        self.processed_json_path = processed_json_path
    
    def create_file_list(self, source_directory: str, target_base_path: str = "/qusb_sync") -> List[Tuple[str, str]]:
        """
        Create list of files to upload
        
        Returns:
            List of (local_path, remote_path) tuples
        """
        files_to_upload = []
        
        for root, dirs, files in os.walk(source_directory):
            for file in files:
                if file.lower().endswith(('.smc', '.sfc', '.bin')):
                    local_path = os.path.join(root, file)
                    
                    # Create relative path for remote
                    rel_path = os.path.relpath(local_path, source_directory)
                    remote_path = f"{target_base_path}/{rel_path.replace(os.sep, '/')}"
                    
                    files_to_upload.append((local_path, remote_path))
        
        return files_to_upload
    
    async def upload_file_with_workflow(self, local_path: str, remote_path: str) -> bool:
        """
        Upload single file with complete workflow:
        1. Ensure folder structure exists
        2. Upload file
        3. Update qusb_last_sync if matching processed.json entry
        """
        try:
            # Step 1: Ensure folder structure exists
            remote_dir = str(Path(remote_path).parent)
            if remote_dir != "/" and remote_dir != ".":
                if not await self.filesystem_manager.ensure_directory(remote_dir):
                    return False
            
            # Step 2: Upload the file
            if not await self.upload_manager.upload_file(local_path, remote_path, ensure_directory=False):
                return False
            
            # Step 3: Update qusb_last_sync if matching entry exists
            filename = os.path.basename(local_path)
            self.update_qusb_last_sync(filename)
            
            return True
            
        except Exception:
            return False
    
    async def upload_rom_list(self, file_list: List[Tuple[str, str]]) -> Dict[str, bool]:
        """
        Process list of ROMs sequentially (foreach loop)
        
        Returns:
            Dict mapping remote_path to success status
        """
        results = {}
        
        # Process each ROM one at a time
        for local_path, remote_path in file_list:
            success = await self.upload_file_with_workflow(local_path, remote_path)
            results[remote_path] = success
            
            # Brief pause between files
            await asyncio.sleep(0.2)
        
        return results
    
    def update_qusb_last_sync(self, filename: str) -> bool:
        """Update qusb_last_sync field in processed.json if matching entry exists"""
        try:
            if not os.path.exists(self.processed_json_path):
                return False
            
            # Load processed.json
            with open(self.processed_json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Find matching entry and update
            for entry in data.values():
                if isinstance(entry, dict) and entry.get('filename') == filename:
                    entry['qusb_last_sync'] = datetime.now().isoformat()
                    break
            else:
                return False  # No matching entry found
            
            # Save updated data
            with open(self.processed_json_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception:
            return False