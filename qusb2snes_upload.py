#!/usr/bin/env python3
"""
QUSB2SNES Upload Manager V2
High-performance file upload with intelligent retry logic and connection recovery

Key Features:
- Chunk-based uploads with optimized chunk sizes for SD card compatibility
- Intelligent retry logic with exponential backoff
- Connection recovery and device re-attachment
- Progress tracking and performance metrics
- Memory-efficient streaming uploads
- Proper error handling and validation
"""

import asyncio
import logging
import os
import time
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from qusb2snes_connection import QUSB2SNESConnection
from qusb2snes_device import QUSB2SNESDevice
from qusb2snes_filesystem import QUSB2SNESFileSystem


class UploadState(Enum):
    """Upload operation states"""
    PENDING = "pending"
    UPLOADING = "uploading"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"


@dataclass
class UploadProgress:
    """Upload progress tracking"""
    bytes_sent: int = 0
    total_bytes: int = 0
    chunks_sent: int = 0
    total_chunks: int = 0
    start_time: float = 0
    last_update_time: float = 0
    
    @property
    def progress_percent(self) -> float:
        if self.total_bytes == 0:
            return 0.0
        return (self.bytes_sent / self.total_bytes) * 100
    
    @property
    def elapsed_time(self) -> float:
        if self.start_time == 0:
            return 0.0
        return time.time() - self.start_time
    
    @property
    def upload_speed_kbps(self) -> float:
        if self.elapsed_time == 0:
            return 0.0
        return (self.bytes_sent / 1024) / self.elapsed_time


@dataclass
class UploadJob:
    """Upload job definition"""
    local_path: str
    remote_path: str
    state: UploadState = UploadState.PENDING
    progress: UploadProgress = None
    attempt_count: int = 0
    last_error: str = ""
    created_time: float = 0
    
    def __post_init__(self):
        if self.progress is None:
            self.progress = UploadProgress()
        if self.created_time == 0:
            self.created_time = time.time()


class QUSB2SNESUploadManager:
    """
    High-performance upload manager for QUSB2SNES with intelligent retry logic
    
    Features:
    - Optimized chunk sizes for SD card compatibility
    - Connection recovery and device re-attachment
    - Progress tracking and performance metrics
    - Configurable retry strategies
    """
    
    def __init__(
        self,
        connection: QUSB2SNESConnection,
        device_manager: Optional[QUSB2SNESDevice] = None,
        filesystem_manager: Optional[QUSB2SNESFileSystem] = None
    ):
        self.connection = connection
        self.device_manager = device_manager
        self.filesystem_manager = filesystem_manager
        
        # Upload configuration
        self.chunk_size = 512  # Optimized for SD card compatibility
        self.max_retries = 3
        self.retry_delay_base = 1.5
        self.progress_report_interval = 500 * 1024  # Report every 500KB
        self.chunk_delay = 0.005  # Small delay between chunks
        self.large_chunk_delay = 0.1  # Longer delay every 64KB for SD card
        self.large_chunk_threshold = 64 * 1024  # Threshold for longer delays
        
        # Progress tracking
        self.active_uploads: Dict[str, UploadJob] = {}
        self.upload_history: List[UploadJob] = []
        self.total_bytes_uploaded = 0
        self.total_uploads_completed = 0
        self.total_uploads_failed = 0
        
        # Performance metrics
        self.start_time = time.time()
        self.total_upload_time = 0.0
        
        # Callbacks
        self.on_progress: Optional[Callable[[UploadJob], None]] = None
        self.on_completed: Optional[Callable[[UploadJob], None]] = None
        self.on_failed: Optional[Callable[[UploadJob], None]] = None
        
        # Logging
        self.logger = logging.getLogger("QUSB2SNESUploadManager")
    
    def _log_info(self, message: str):
        """Log info message"""
        if self.logger:
            self.logger.info(message)
        print(f"[UploadManager] {message}")
    
    def _log_error(self, message: str):
        """Log error message"""
        if self.logger:
            self.logger.error(message)
        print(f"[UploadManager] ERROR: {message}")
    
    def _log_debug(self, message: str):
        """Log debug message"""
        if self.logger:
            self.logger.debug(message)
    
    async def upload_file(
        self,
        local_path: str,
        remote_path: str,
        ensure_directory: bool = True
    ) -> bool:
        """
        Upload a single file with full error recovery
        
        Args:
            local_path: Local file path to upload
            remote_path: Remote file path destination
            ensure_directory: Whether to ensure remote directory exists
            
        Returns:
            bool: True if upload successful
        """
        # Validate local file
        if not os.path.exists(local_path):
            self._log_error(f"Local file not found: {local_path}")
            return False
        
        file_size = os.path.getsize(local_path)
        if file_size == 0:
            self._log_error(f"Cannot upload empty file: {local_path}")
            return False
        
        # Create upload job
        job = UploadJob(
            local_path=local_path,
            remote_path=remote_path
        )
        job.progress.total_bytes = file_size
        job.progress.total_chunks = (file_size + self.chunk_size - 1) // self.chunk_size
        
        self.active_uploads[remote_path] = job
        
        try:
            # Ensure remote directory exists if requested
            if ensure_directory and self.filesystem_manager:
                remote_dir = str(Path(remote_path).parent)
                if remote_dir != "/" and remote_dir != ".":
                    self._log_debug(f"Ensuring remote directory exists: {remote_dir}")
                    if not await self.filesystem_manager.ensure_directory(remote_dir):
                        raise Exception(f"Failed to ensure remote directory: {remote_dir}")
            
            # Attempt upload with retry logic
            success = await self._upload_with_retry(job)
            
            if success:
                job.state = UploadState.COMPLETED
                self.total_uploads_completed += 1
                self.total_bytes_uploaded += file_size
                self._log_info(f"✅ Upload completed: {os.path.basename(local_path)} ({file_size} bytes)")
                
                if self.on_completed:
                    self.on_completed(job)
            else:
                job.state = UploadState.FAILED
                self.total_uploads_failed += 1
                self._log_error(f"❌ Upload failed: {os.path.basename(local_path)}")
                
                if self.on_failed:
                    self.on_failed(job)
            
            return success
            
        finally:
            # Move to history and clean up
            self.upload_history.append(job)
            if remote_path in self.active_uploads:
                del self.active_uploads[remote_path]
    
    async def _upload_with_retry(self, job: UploadJob) -> bool:
        """
        Upload file with intelligent retry logic
        
        Args:
            job: Upload job to execute
            
        Returns:
            bool: True if upload successful
        """
        for attempt in range(self.max_retries + 1):
            try:
                job.attempt_count = attempt + 1
                job.state = UploadState.UPLOADING if attempt == 0 else UploadState.RETRYING
                
                self._log_info(f"📤 Upload attempt {attempt + 1}/{self.max_retries + 1}: {os.path.basename(job.local_path)}")
                
                # Reset progress for retry
                if attempt > 0:
                    job.progress = UploadProgress()
                    job.progress.total_bytes = os.path.getsize(job.local_path)
                    job.progress.total_chunks = (job.progress.total_bytes + self.chunk_size - 1) // self.chunk_size
                
                # Ensure robust connection
                await self._ensure_robust_connection(attempt)
                
                # Execute the upload
                success = await self._execute_upload(job)
                
                if success:
                    return True
                else:
                    raise Exception("Upload execution failed")
                    
            except Exception as e:
                job.last_error = str(e)
                self._log_error(f"Upload attempt {attempt + 1} failed: {str(e)}")
                
                if attempt < self.max_retries:
                    # Exponential backoff retry delay
                    retry_delay = self.retry_delay_base * (2 ** attempt)
                    self._log_info(f"Retrying in {retry_delay:.1f}s...")
                    await asyncio.sleep(retry_delay)
                else:
                    self._log_error(f"Upload failed after {self.max_retries + 1} attempts")
                    return False
        
        return False
    
    async def _ensure_robust_connection(self, attempt_number: int = 0):
        """
        Ensure robust connection before upload attempt
        
        Args:
            attempt_number: Current attempt number for escalating recovery
        """
        # Check connection status
        if not self.connection.is_connected():
            self._log_info(f"Connection lost, attempting recovery (attempt {attempt_number + 1})")
            
            # Active reconnection attempt
            try:
                # Try to reconnect
                await self.connection.disconnect()  # Clean disconnect first
                await asyncio.sleep(1.0)  # Brief pause
                
                await self.connection.connect()  # Reconnect
                self._log_info("✅ Connection successfully re-established")
                
            except Exception as e:
                self._log_error(f"Manual reconnection failed: {str(e)}")
                
                # Fall back to waiting for automatic recovery
                escalated_wait = 2.0 + (attempt_number * 1.0)
                self._log_info(f"Waiting {escalated_wait}s for automatic recovery...")
                await asyncio.sleep(escalated_wait)
                
                # Check if recovery worked
                if not self.connection.is_connected():
                    raise Exception("Connection recovery failed after manual and automatic attempts")
        
        # Re-attach device if needed
        if self.device_manager:
            try:
                # Always try to discover and attach fresh for uploads
                devices = await self.device_manager.discover_devices(use_cache=False)
                if not devices:
                    raise Exception("No devices available for upload")
                
                device_name = devices[0].name
                
                # Check if we need to attach
                if not self.device_manager.is_attached(device_name):
                    self._log_info(f"Attaching to device for upload: {device_name}")
                    if not await self.device_manager.attach_device(device_name):
                        raise Exception(f"Failed to attach device: {device_name}")
                else:
                    self._log_debug(f"Device already attached: {device_name}")
                    
            except Exception as e:
                self._log_error(f"Device management failed: {str(e)}")
                raise
    
    async def _execute_upload(self, job: UploadJob) -> bool:
        """
        Execute the actual file upload
        
        Args:
            job: Upload job to execute
            
        Returns:
            bool: True if upload successful
        """
        job.progress.start_time = time.time()
        
        try:
            # Send PutFile command with proper validation
            file_size = job.progress.total_bytes
            size_hex = format(file_size, 'X')
            
            self._log_debug(f"Sending PutFile command for {job.remote_path} ({file_size} bytes)")
            
            response = await self.connection.send_command(
                "PutFile",
                operands=[job.remote_path, size_hex],
                expect_response=False  # PutFile is a no-reply command
            )
            
            # Check if PutFile command succeeded (connection manager handles no-reply commands)
            if response is None:
                raise Exception(f"PutFile command failed for {job.remote_path}")
            
            # Enhanced delay for SD card preparation
            await asyncio.sleep(0.5)
            
            # Send file data in chunks
            success = await self._send_file_data(job)
            
            if success:
                # Enhanced post-upload stabilization
                await asyncio.sleep(0.2)
                self._log_info(f"✅ Upload data transmission completed: {os.path.basename(job.local_path)}")
                return True
            else:
                return False
                
        except Exception as e:
            self._log_error(f"Upload execution failed: {str(e)}")
            return False
    
    async def _send_file_data(self, job: UploadJob) -> bool:
        """
        Send file data in optimized chunks
        
        Args:
            job: Upload job with progress tracking
            
        Returns:
            bool: True if all data sent successfully
        """
        try:
            with open(job.local_path, "rb") as f:
                while job.progress.bytes_sent < job.progress.total_bytes:
                    # Enhanced connection check before each chunk
                    if not self.connection.is_connected() or not self.connection.websocket:
                        raise Exception("Connection lost during file transfer")
                    
                    # Read chunk efficiently
                    remaining_bytes = job.progress.total_bytes - job.progress.bytes_sent
                    chunk_size = min(self.chunk_size, remaining_bytes)
                    chunk = f.read(chunk_size)
                    
                    if not chunk:
                        break
                    
                    try:
                        # Send chunk via WebSocket
                        await self.connection.websocket.send(chunk)
                    except Exception as e:
                        raise Exception(f"Failed to send chunk at byte {job.progress.bytes_sent}: {str(e)}")
                    
                    # Update progress
                    job.progress.bytes_sent += len(chunk)
                    job.progress.chunks_sent += 1
                    job.progress.last_update_time = time.time()
                    
                    # Progress reporting every 500KB like working implementation
                    if (job.progress.bytes_sent % (500 * 1024) == 0 or 
                        job.progress.bytes_sent == job.progress.total_bytes):
                        await self._report_progress(job)
                    
                    # Intelligent chunk delays for SD card compatibility - match working implementation
                    if job.progress.bytes_sent < job.progress.total_bytes:
                        # Longer pause every 64KB to let SD card catch up
                        if job.progress.bytes_sent % (64 * 1024) == 0:
                            await asyncio.sleep(0.1)  # Longer pause for SD card
                        else:
                            await asyncio.sleep(0.005)  # Regular delay from working implementation
                    
                    # Callback for real-time progress updates
                    if self.on_progress:
                        self.on_progress(job)
            
            # Verify complete transmission
            if job.progress.bytes_sent != job.progress.total_bytes:
                raise Exception(f"Incomplete transfer: sent {job.progress.bytes_sent} of {job.progress.total_bytes} bytes")
            
            self._log_debug(f"Successfully sent {job.progress.bytes_sent} bytes in {job.progress.chunks_sent} chunks")
            return True
            
        except Exception as e:
            self._log_error(f"File data transmission failed: {str(e)}")
            return False
    
    async def _report_progress(self, job: UploadJob):
        """
        Report upload progress
        
        Args:
            job: Upload job to report on
        """
        progress_kb = job.progress.bytes_sent // 1024
        total_kb = job.progress.total_bytes // 1024
        speed_kbps = job.progress.upload_speed_kbps
        
        self._log_info(
            f"📤 Upload progress: {job.progress.progress_percent:.1f}% "
            f"({progress_kb}KB/{total_kb}KB) @ {speed_kbps:.1f}KB/s"
        )
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """
        Get comprehensive upload performance metrics
        
        Returns:
            Dict containing performance statistics
        """
        uptime = time.time() - self.start_time
        
        metrics = {
            "uptime_seconds": uptime,
            "total_uploads_completed": self.total_uploads_completed,
            "total_uploads_failed": self.total_uploads_failed,
            "total_bytes_uploaded": self.total_bytes_uploaded,
            "active_uploads": len(self.active_uploads),
            "average_upload_speed_kbps": 0.0,
            "success_rate_percent": 0.0,
            "total_upload_time": self.total_upload_time
        }
        
        # Calculate rates
        if self.total_upload_time > 0:
            metrics["average_upload_speed_kbps"] = (self.total_bytes_uploaded / 1024) / self.total_upload_time
        
        total_attempts = self.total_uploads_completed + self.total_uploads_failed
        if total_attempts > 0:
            metrics["success_rate_percent"] = (self.total_uploads_completed / total_attempts) * 100
        
        return metrics
    
    async def upload_files_batch(
        self,
        file_pairs: List[tuple],
        ensure_directories: bool = True,
        max_concurrent: int = 1
    ) -> Dict[str, bool]:
        """
        Upload multiple files with optional concurrency
        
        Args:
            file_pairs: List of (local_path, remote_path) tuples
            ensure_directories: Whether to ensure remote directories exist
            max_concurrent: Maximum concurrent uploads (default 1 for SD card safety)
            
        Returns:
            Dict mapping remote_path to success status
        """
        results = {}
        
        # Pre-create all needed directories once to avoid conflicts
        if ensure_directories and self.filesystem_manager:
            await self._pre_create_directories(file_pairs)
        
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def upload_single(local_path: str, remote_path: str) -> bool:
            async with semaphore:
                # Skip directory creation since we pre-created them
                return await self.upload_file(local_path, remote_path, ensure_directory=False)
        
        # Create upload tasks
        tasks = []
        for local_path, remote_path in file_pairs:
            task = asyncio.create_task(upload_single(local_path, remote_path))
            tasks.append((task, remote_path))
        
        # Wait for all uploads to complete
        for task, remote_path in tasks:
            try:
                success = await task
                results[remote_path] = success
            except Exception as e:
                self._log_error(f"Batch upload failed for {remote_path}: {str(e)}")
                results[remote_path] = False
        
        return results
    
    async def _pre_create_directories(self, file_pairs: List[tuple]):
        """
        Pre-create all needed directories to avoid conflicts during batch uploads
        
        Args:
            file_pairs: List of (local_path, remote_path) tuples
        """
        # Collect unique directories
        directories = set()
        for local_path, remote_path in file_pairs:
            remote_dir = str(Path(remote_path).parent)
            if remote_dir != "/" and remote_dir != ".":
                directories.add(remote_dir)
        
        if not directories:
            return
        
        self._log_info(f"Pre-creating {len(directories)} unique directories for batch upload...")
        
        # Create directories one by one to avoid connection conflicts
        for directory in sorted(directories):  # Sort for predictable order
            try:
                self._log_debug(f"Pre-creating directory: {directory}")
                if not await self.filesystem_manager.ensure_directory(directory):
                    self._log_error(f"Failed to pre-create directory: {directory}")
                else:
                    self._log_debug(f"✅ Pre-created directory: {directory}")
            except Exception as e:
                self._log_error(f"Error pre-creating directory {directory}: {str(e)}")
    
    
    def get_active_uploads(self) -> List[UploadJob]:
        """Get list of currently active uploads"""
        return list(self.active_uploads.values())
    
    def get_upload_history(self) -> List[UploadJob]:
        """Get upload history"""
        return list(self.upload_history)
    
    def clear_history(self):
        """Clear upload history"""
        self.upload_history.clear()
    
    async def cleanup(self):
        """Clean up upload manager resources"""
        # Cancel any active uploads
        for job in self.active_uploads.values():
            job.state = UploadState.FAILED
            job.last_error = "Upload manager cleanup"
        
        self.active_uploads.clear()
        self._log_info("Upload manager cleanup completed")