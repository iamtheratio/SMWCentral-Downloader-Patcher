#!/usr/bin/env python3
"""
Upload Manager V2 Simple - Hybrid Architecture
Uses V2 foundation (Connection, Device, FileSystem managers) with simple upload logic

Key principles:
- V2 foundation components (Connection, Device, FileSystem) - these work well
- Simple upload logic from simple_file_uploader.py - no complex retry/state management
- V1 proven patterns: 512-byte chunks, proper timing, no retries during upload
- Fail fast and clean - no complex connection recovery during operations
"""

import asyncio
import os
import time
from pathlib import Path


class UploadManagerV2Simple:
    """
    Simple Upload Manager using V2 foundation + simple upload patterns
    Best of both worlds: V2 architecture + simple upload logic
    """
    
    def __init__(self, connection, device, filesystem):
        # Use proven V2 foundation components
        self.connection = connection
        self.device = device
        self.filesystem = filesystem
        
        # V1 proven constants for upload operations
        self.chunk_size = 512  # Proven for SD card compatibility
        self.sd_card_prep_delay = 0.5  # V1 proven delay before file data
        self.regular_delay = 0.005  # V1 proven regular delay
        self.sd_card_pause_delay = 0.1  # V1 proven longer pause every 64KB
        self.progress_report_interval = 500 * 1024  # V1 proven 500KB intervals
    
    def log_progress(self, message: str):
        """Simple progress logging"""
        print(f"[UploadV2Simple] {message}")
    
    def log_error(self, message: str):
        """Simple error logging"""
        print(f"[UploadV2Simple] ERROR: {message}")
    
    async def upload_file(self, local_path: str, remote_path: str) -> bool:
        """
        Simple file upload using V2 foundation + simple upload patterns
        
        This method combines:
        - V2 foundation: Use connection/device managers for setup
        - Simple upload: Direct file upload with V1 proven patterns
        - No complex retry logic: Fail fast and clean
        
        Args:
            local_path: Full path to local file
            remote_path: Full remote path including filename
            
        Returns:
            bool: True if upload succeeded, False otherwise
        """
        try:
            # Validate inputs
            if not os.path.exists(local_path):
                self.log_error(f"Local file not found: {local_path}")
                return False
            
            # Use V2 foundation: Ensure connection and device are ready
            if not self.connection.is_connected():
                self.log_error("Connection not available")
                return False
                
            if not self.device.is_attached():
                self.log_error("Device not attached")
                return False
            
            # Get file info
            file_size = os.path.getsize(local_path)
            filename = os.path.basename(local_path)
            
            self.log_progress(f"📤 Uploading {filename} ({file_size:,} bytes) to {remote_path}")
            
            # Step 1: Send PutFile command (simple approach - no retries)
            size_hex = format(file_size, 'X')
            response = await self.connection.send_command(
                "PutFile", 
                operands=[remote_path, size_hex],
                expect_response=False  # PutFile is no-reply command
            )
            
            if response is None:
                self.log_error(f"PutFile command failed for {remote_path}")
                return False
            
            # Step 2: V1 proven delay for SD card preparation
            await asyncio.sleep(self.sd_card_prep_delay)
            
            # Step 3: Send file data using simple approach (no complex retry logic)
            bytes_sent = 0
            last_progress_report = 0
            
            with open(local_path, "rb") as f:
                while bytes_sent < file_size:
                    # Read chunk
                    chunk = f.read(min(self.chunk_size, file_size - bytes_sent))
                    if not chunk:
                        break
                    
                    # Send chunk directly through connection's websocket
                    # This is the simple approach - direct websocket usage
                    try:
                        await self.connection.websocket.send(chunk)
                        bytes_sent += len(chunk)
                    except Exception as e:
                        self.log_error(f"Failed to send chunk at byte {bytes_sent}: {e}")
                        return False
                    
                    # Progress reporting (V1 pattern)
                    if bytes_sent - last_progress_report >= self.progress_report_interval or bytes_sent == file_size:
                        percent = (bytes_sent / file_size) * 100
                        self.log_progress(f"📊 Progress: {percent:.1f}% ({bytes_sent:,}/{file_size:,} bytes)")
                        last_progress_report = bytes_sent
                    
                    # V1 proven timing delays for SD card compatibility
                    if bytes_sent % (64 * 1024) == 0:
                        # V1 pattern: Longer pause every 64KB for SD card
                        await asyncio.sleep(self.sd_card_pause_delay)
                    else:
                        # V1 pattern: Regular tiny delay
                        await asyncio.sleep(self.regular_delay)
            
            # Step 4: Wait for SD card processing (V1 proven timing)
            if file_size <= 1024*1024:  # <= 1MB
                wait_time = 1.0
            elif file_size <= 4*1024*1024:  # <= 4MB
                wait_time = 2.0
            else:  # > 4MB
                wait_time = 3.0
            
            self.log_progress(f"⏳ Waiting {wait_time}s for SD card processing...")
            await asyncio.sleep(wait_time)
            
            self.log_progress(f"✅ Upload completed: {filename}")
            return True
            
        except Exception as e:
            self.log_error(f"Upload failed: {e}")
            return False
    
    async def upload_multiple_files(self, file_pairs: list) -> dict:
        """
        Upload multiple files using V2 foundation with simple upload logic
        
        Args:
            file_pairs: List of (local_path, remote_path) tuples
            
        Returns:
            dict: Results with success count and failures
        """
        results = {
            "uploaded": 0,
            "failed": 0,
            "failures": []
        }
        
        self.log_progress(f"📤 Starting upload of {len(file_pairs)} files")
        
        for i, (local_path, remote_path) in enumerate(file_pairs, 1):
            self.log_progress(f"📁 [{i}/{len(file_pairs)}] Processing: {os.path.basename(local_path)}")
            
            success = await self.upload_file(local_path, remote_path)
            
            if success:
                results["uploaded"] += 1
            else:
                results["failed"] += 1
                results["failures"].append({
                    "local_path": local_path,
                    "remote_path": remote_path
                })
        
        # Summary
        total = len(file_pairs)
        success_rate = (results["uploaded"] / total) * 100 if total > 0 else 0
        
        self.log_progress(f"📊 Upload complete: {results['uploaded']}/{total} succeeded ({success_rate:.1f}%)")
        
        if results["failed"] > 0:
            self.log_error(f"❌ {results['failed']} uploads failed")
            for failure in results["failures"][:3]:  # Show first 3 failures
                self.log_error(f"   • {failure['local_path']} -> {failure['remote_path']}")
        
        return results