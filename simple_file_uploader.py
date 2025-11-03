#!/usr/bin/env python3
"""
Simple File Uploader - Just Upload Files!

API:
    uploader = SimpleFileUploader()
    success = await uploader.upload_file("/path/to/local/file.smc", "/ROMS/remote/file.smc")

That's it! No complex state management, no microservices, no over-engineering.
Uses proven V1 patterns from qusb2snes_sync.py that actually work.
"""

import asyncio
import json
import os
import websockets
from pathlib import Path


class SimpleFileUploader:
    """
    Dead simple file uploader using proven V1 patterns.
    No complex state management - just upload files!
    """
    
    def __init__(self, host="localhost", port=23074, device=None):
        self.host = host
        self.port = port
        self.device = device
        self.websocket = None
        self.connected = False
        
        # V1 proven constants that actually work
        self.chunk_size = 512  # SD card compatibility
        self.sd_prep_delay = 0.5  # Wait for SD card before sending data
        self.regular_delay = 0.005  # Tiny delay between chunks
        self.large_chunk_delay = 0.1  # Longer delay every 64KB for SD card
        self.progress_interval = 500 * 1024  # Report progress every 500KB
    
    def log(self, message: str):
        """Simple logging"""
        print(f"[Uploader] {message}")
    
    async def connect(self) -> bool:
        """Simple connection - no complex state management"""
        try:
            if self.connected:
                return True
            
            uri = f"ws://{self.host}:{self.port}"
            self.log(f"Connecting to {uri}")
            
            self.websocket = await asyncio.wait_for(
                websockets.connect(uri), 
                timeout=5.0
            )
            
            # Send Name command
            name_cmd = {"Opcode": "Name", "Operands": ["Simple File Uploader"]}
            await self.websocket.send(json.dumps(name_cmd))
            await asyncio.sleep(0.5)  # Let server process
            
            self.connected = True
            self.log("✅ Connected")
            return True
            
        except Exception as e:
            self.log(f"❌ Connection failed: {e}")
            return False
    
    async def attach_device(self, device_name: str = None) -> bool:
        """Simple device attachment"""
        try:
            device = device_name or self.device
            if not device:
                self.log("❌ No device specified")
                return False
            
            if not self.connected:
                if not await self.connect():
                    return False
            
            # Send Attach command  
            attach_cmd = {"Opcode": "Attach", "Operands": [device]}
            await self.websocket.send(json.dumps(attach_cmd))
            await asyncio.sleep(0.5)  # Wait for attachment
            
            self.log(f"✅ Attached to {device}")
            return True
            
        except Exception as e:
            self.log(f"❌ Device attachment failed: {e}")
            return False
    
    async def upload_file(self, local_path: str, remote_path: str, device_name: str = None) -> bool:
        """
        Upload a single file. That's it!
        
        Args:
            local_path: Full path to local file
            remote_path: Full remote path including filename
            device_name: Optional device name (uses self.device if not provided)
        
        Returns:
            bool: True if upload succeeded, False otherwise
        """
        try:
            # Validate inputs
            if not os.path.exists(local_path):
                self.log(f"❌ Local file not found: {local_path}")
                return False
            
            # Connect and attach device if needed
            if not self.connected:
                if not await self.connect():
                    return False
            
            if device_name or self.device:
                if not await self.attach_device(device_name):
                    return False
            
            # Get file info
            file_size = os.path.getsize(local_path)
            filename = os.path.basename(local_path)
            
            self.log(f"📤 Uploading {filename} ({file_size:,} bytes) to {remote_path}")
            
            # Step 1: Send PutFile command (V1 proven pattern)
            size_hex = format(file_size, 'X')
            put_cmd = {"Opcode": "PutFile", "Operands": [remote_path, size_hex]}
            await self.websocket.send(json.dumps(put_cmd))
            
            # Step 2: V1 proven delay for SD card preparation  
            await asyncio.sleep(self.sd_prep_delay)
            
            # Step 3: Send file data in V1 proven chunks
            bytes_sent = 0
            last_progress_report = 0
            
            with open(local_path, "rb") as f:
                while bytes_sent < file_size:
                    # Read chunk
                    chunk = f.read(min(self.chunk_size, file_size - bytes_sent))
                    if not chunk:
                        break
                    
                    # Send chunk
                    await self.websocket.send(chunk)
                    bytes_sent += len(chunk)
                    
                    # Progress reporting (V1 pattern)
                    if bytes_sent - last_progress_report >= self.progress_interval or bytes_sent == file_size:
                        percent = (bytes_sent / file_size) * 100
                        self.log(f"📊 Progress: {percent:.1f}% ({bytes_sent:,}/{file_size:,} bytes)")
                        last_progress_report = bytes_sent
                    
                    # V1 proven timing delays for SD card compatibility
                    if bytes_sent % (64 * 1024) == 0:
                        # Longer pause every 64KB for SD card
                        await asyncio.sleep(self.large_chunk_delay)
                    else:
                        # Regular tiny delay
                        await asyncio.sleep(self.regular_delay)
            
            # Step 4: Wait for SD card to finish writing
            if file_size <= 1024*1024:  # <= 1MB
                wait_time = 1.0
            elif file_size <= 4*1024*1024:  # <= 4MB
                wait_time = 2.0
            else:  # > 4MB
                wait_time = 3.0
            
            self.log(f"⏳ Waiting {wait_time}s for SD card processing...")
            await asyncio.sleep(wait_time)
            
            self.log(f"✅ Upload completed: {filename}")
            return True
            
        except Exception as e:
            self.log(f"❌ Upload failed: {e}")
            return False
    
    async def disconnect(self):
        """Clean disconnect"""
        if self.websocket:
            try:
                await self.websocket.close(code=1000, reason="Upload complete")
                self.log("👋 Disconnected")
            except:
                pass
            finally:
                self.websocket = None
                self.connected = False
    
    async def __aenter__(self):
        """Context manager entry"""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - always clean up"""
        await self.disconnect()


# Simple usage examples
async def upload_single_file():
    """Example: Upload a single file"""
    uploader = SimpleFileUploader(device="SD2SNES COM3")
    
    success = await uploader.upload_file(
        local_path="C:/ROMs/MyHack.smc",
        remote_path="/ROMS/MyHack.smc"
    )
    
    await uploader.disconnect()
    return success


async def upload_multiple_files():
    """Example: Upload multiple files with single connection"""
    async with SimpleFileUploader(device="SD2SNES COM3") as uploader:
        files = [
            ("C:/ROMs/Hack1.smc", "/ROMS/Kaizo/Hack1.smc"),
            ("C:/ROMs/Hack2.smc", "/ROMS/Traditional/Hack2.smc"),
        ]
        
        results = []
        for local_path, remote_path in files:
            success = await uploader.upload_file(local_path, remote_path)
            results.append(success)
        
        return all(results)


if __name__ == "__main__":
    # Simple test
    async def test():
        print("Testing simple file uploader...")
        # await upload_single_file()
        print("Done!")
    
    asyncio.run(test())