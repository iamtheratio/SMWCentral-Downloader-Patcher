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
        
        # V2 proven constants with minimal client optimizations  
        self.chunk_size = 1024  # Back to QFile2SNES standard
        self.progress_report_interval = 500 * 1024  # Report every 500KB
    
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
            
            # Step 1: Ensure target directory exists
            target_dir = os.path.dirname(remote_path).replace('\\', '/')
            if target_dir and target_dir != '/':
                self.log_progress(f"📁 Ensuring directory exists: {target_dir}")
                try:
                    success = await self.filesystem.ensure_directory(target_dir)
                    if not success:
                        self.log_error(f"Failed to create directory: {target_dir}")
                        return False
                    self.log_progress(f"✅ Directory ready: {target_dir}")
                except Exception as e:
                    self.log_error(f"Error creating directory {target_dir}: {e}")
                    return False
            
            # Step 2: Send PutFile command (simple approach - no retries)
            size_hex = format(file_size, 'X')
            response = await self.connection.send_command(
                "PutFile", 
                operands=[remote_path, size_hex],
                expect_response=False  # PutFile is no-reply command
            )
            
            # PutFile is a no-reply command, so response being None is expected and correct
            # We don't check the response for no-reply commands
            
            # Step 3: Send binary data immediately (minimal client proven pattern)
            # NO DELAY - this was the key insight from minimal client success!
            
            # Step 4: Load entire file into memory (QFile2SNES pattern)
            print(f"[UploadV2Simple] 📖 Loading file into memory...")
            with open(local_path, "rb") as f:
                file_data = f.read()
            
            if len(file_data) != file_size:
                self.log_error(f"File size mismatch: expected {file_size}, read {len(file_data)}")
                return False
            
            # Step 5: Send file data in chunks (QFile2SNES pattern)
            print(f"[UploadV2Simple] 📡 Starting binary data transfer...")
            print(f"[UploadV2Simple] File data size: {len(file_data)} bytes")
            print(f"[UploadV2Simple] Chunk size: {self.chunk_size} bytes")
            
            bytes_sent = 0
            last_progress_report = 0
            chunk_count = 0
            
            while bytes_sent < len(file_data):
                # Calculate chunk size
                chunk_size = min(self.chunk_size, len(file_data) - bytes_sent)
                chunk = file_data[bytes_sent:bytes_sent + chunk_size]
                chunk_count += 1
                
                print(f"[UploadV2Simple] Sending chunk {chunk_count}: {len(chunk)} bytes at offset {bytes_sent}")
                
                # Send chunk using websocket binary message (QFile2SNES pattern)
                # Python websockets: bytes = binary message, str = text message
                try:
                    await self.connection.websocket.send(chunk)
                    bytes_sent += len(chunk)
                    print(f"[UploadV2Simple] ✅ Chunk {chunk_count} sent successfully")
                    
                    # NO DELAYS - minimal client pattern works immediately
                except Exception as e:
                    self.log_error(f"Failed to send chunk at byte {bytes_sent}: {e}")
                    return False
                    
                    # Progress reporting
                    if bytes_sent - last_progress_report >= self.progress_report_interval or bytes_sent == file_size:
                        percent = (bytes_sent / file_size) * 100
                        self.log_progress(f"📊 Progress: {percent:.1f}% ({bytes_sent:,}/{file_size:,} bytes)")
                        last_progress_report = bytes_sent
                    
                    # V1 proven timing delays for SD card compatibility
                    if bytes_sent < file_size:
                        if bytes_sent % (64 * 1024) == 0:
                            # V1 pattern: Longer pause every 64KB for SD card
                            await asyncio.sleep(0.1)
                        else:
                            # V1 pattern: Regular tiny delay
                            await asyncio.sleep(0.005)
            
            # Step 5: Wait for SD card processing (V1 proven timing)
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