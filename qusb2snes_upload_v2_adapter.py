#!/usr/bin/env python3
"""
QUSB2SNES Upload Manager V2-to-V3 Compatibility Adapter
Maintains existing V2 interface while using proven V3 implementation

This adapter allows existing code to continue using the V2 interface
while benefiting from the reliable V3 two-phase upload strategy.
"""

import asyncio
import logging
import os
from typing import Optional, Callable, List, Dict, Any
from dataclasses import dataclass

from qusb2snes_upload_v3 import QUSB2SNESUploadManagerV3, UploadProgress
from qusb2snes_connection import QUSB2SNESConnection
from qusb2snes_device import QUSB2SNESDevice
from qusb2snes_filesystem import QUSB2SNESFileSystem


@dataclass
class UploadJob:
    """V2 compatibility UploadJob wrapper"""
    local_path: str
    remote_path: str
    progress: UploadProgress
    state: str = "pending"
    
    def __post_init__(self):
        if not hasattr(self, 'progress') or self.progress is None:
            self.progress = UploadProgress()


class QUSB2SNESUploadManagerV2Adapter:
    """
    V2 compatibility adapter that uses V3 implementation internally
    Maintains the same interface as the original V2 manager
    """
    
    def __init__(
        self,
        connection: Optional[QUSB2SNESConnection] = None,
        device_manager: Optional[QUSB2SNESDevice] = None,
        filesystem_manager: Optional[QUSB2SNESFileSystem] = None,
        config_manager: Optional[object] = None,
        websocket_url: str = "ws://localhost:8080"
    ):
        # V2 compatibility attributes (legacy interface)
        self.connection = connection
        self.device_manager = device_manager
        self.filesystem_manager = filesystem_manager
        
        # V3 implementation (actual workhorse)
        self.v3_manager = QUSB2SNESUploadManagerV3(
            websocket_url=websocket_url,
            config_manager=config_manager
        )
        
        # V2 compatibility settings
        self.chunk_size = 1024
        self.max_retries = 3
        self.retry_delay_base = 1.5
        self.progress_report_interval = 500 * 1024
        
        # Progress tracking for V2 compatibility
        self.active_uploads: Dict[str, UploadJob] = {}
        self.upload_history: List[UploadJob] = []
        self.total_bytes_uploaded = 0
        self.total_uploads_completed = 0
        self.total_uploads_failed = 0
        
        # Callbacks
        self.on_progress: Optional[Callable[[UploadJob], None]] = None
        self.on_completed: Optional[Callable[[UploadJob], None]] = None
        self.on_failed: Optional[Callable[[UploadJob], None]] = None
        
        # Logging
        self.logger = logging.getLogger("QUSB2SNESUploadV2Adapter")
    
    def _log_info(self, message: str):
        """Log info message"""
        if self.logger:
            self.logger.info(message)
        print(f"[UploadV2Adapter] {message}")
    
    def _log_error(self, message: str):
        """Log error message"""
        if self.logger:
            self.logger.error(message)
        print(f"[UploadV2Adapter] ERROR: {message}")
    
    def _create_upload_job(self, local_path: str, remote_path: str) -> UploadJob:
        """Create a V2-compatible UploadJob"""
        progress = UploadProgress()
        if os.path.exists(local_path):
            progress.total_bytes = os.path.getsize(local_path)
            progress.total_files = 1
        
        job = UploadJob(
            local_path=local_path,
            remote_path=remote_path,
            progress=progress
        )
        return job
    
    def _setup_v3_progress_callback(self, job: UploadJob):
        """Setup V3 progress callback that updates V2 job"""
        def v3_progress_callback(v3_progress: UploadProgress):
            # Update job progress
            job.progress.files_completed = v3_progress.files_completed
            job.progress.bytes_uploaded = v3_progress.bytes_uploaded
            job.state = "uploading"
            
            # Call V2 callback if set
            if self.on_progress:
                self.on_progress(job)
        
        return v3_progress_callback
    
    async def upload_file(
        self,
        local_path: str,
        remote_path: str,
        ensure_directory: bool = True
    ) -> bool:
        """
        V2 compatibility method - upload a single file
        
        Args:
            local_path: Local file path to upload
            remote_path: Remote file path destination
            ensure_directory: Whether to ensure remote directory exists (always True in V3)
            
        Returns:
            bool: True if upload successful
        """
        self._log_info(f"📤 Uploading file: {local_path} → {remote_path}")
        
        # Create V2-compatible job
        job = self._create_upload_job(local_path, remote_path)
        self.active_uploads[remote_path] = job
        
        try:
            # Setup progress callback
            self.v3_manager.on_progress = self._setup_v3_progress_callback(job)
            
            # Use V3 implementation
            file_mappings = [(local_path, remote_path)]
            success = await self.v3_manager.upload_files(file_mappings)
            
            if success:
                job.state = "completed"
                job.progress.files_completed = 1
                self.total_uploads_completed += 1
                self.total_bytes_uploaded += job.progress.total_bytes
                
                if self.on_completed:
                    self.on_completed(job)
                
                self._log_info(f"✅ Upload completed: {remote_path}")
            else:
                job.state = "failed"
                self.total_uploads_failed += 1
                
                if self.on_failed:
                    self.on_failed(job)
                
                self._log_error(f"❌ Upload failed: {remote_path}")
            
            # Move to history and remove from active
            self.upload_history.append(job)
            if remote_path in self.active_uploads:
                del self.active_uploads[remote_path]
            
            return success
            
        except Exception as e:
            self._log_error(f"Upload error: {e}")
            job.state = "failed"
            self.total_uploads_failed += 1
            
            if self.on_failed:
                self.on_failed(job)
            
            return False
    
    async def upload_files_batch(
        self,
        file_mappings: List[tuple],
        max_concurrent: int = 1
    ) -> Dict[str, bool]:
        """
        V2 compatibility method - upload multiple files
        
        Args:
            file_mappings: List of (local_path, remote_path) tuples
            max_concurrent: Max concurrent uploads (ignored - V3 uses single connection)
            
        Returns:
            Dict[str, bool]: Results keyed by remote_path
        """
        self._log_info(f"📤 Batch uploading {len(file_mappings)} files")
        
        results = {}
        
        # Create jobs for tracking
        for local_path, remote_path in file_mappings:
            job = self._create_upload_job(local_path, remote_path)
            self.active_uploads[remote_path] = job
        
        try:
            # Setup progress callback for overall progress
            def batch_progress_callback(v3_progress: UploadProgress):
                # Update all active jobs proportionally
                for job in self.active_uploads.values():
                    job.progress.files_completed = v3_progress.files_completed
                    job.progress.bytes_uploaded = v3_progress.bytes_uploaded
                    if self.on_progress:
                        self.on_progress(job)
            
            self.v3_manager.on_progress = batch_progress_callback
            
            # Use V3 implementation
            success = await self.v3_manager.upload_files(file_mappings)
            
            # Update all jobs based on overall result
            for local_path, remote_path in file_mappings:
                if remote_path in self.active_uploads:
                    job = self.active_uploads[remote_path]
                    
                    if success:
                        job.state = "completed"
                        job.progress.files_completed = 1
                        self.total_uploads_completed += 1
                        self.total_bytes_uploaded += job.progress.total_bytes
                        
                        if self.on_completed:
                            self.on_completed(job)
                        
                        results[remote_path] = True
                    else:
                        job.state = "failed"
                        self.total_uploads_failed += 1
                        
                        if self.on_failed:
                            self.on_failed(job)
                        
                        results[remote_path] = False
                    
                    # Move to history
                    self.upload_history.append(job)
                    del self.active_uploads[remote_path]
            
            return results
            
        except Exception as e:
            self._log_error(f"Batch upload error: {e}")
            
            # Mark all as failed
            for local_path, remote_path in file_mappings:
                if remote_path in self.active_uploads:
                    job = self.active_uploads[remote_path]
                    job.state = "failed"
                    self.total_uploads_failed += 1
                    
                    if self.on_failed:
                        self.on_failed(job)
                    
                    results[remote_path] = False
                    self.upload_history.append(job)
                    del self.active_uploads[remote_path]
            
            return results
    
    async def sync_directory(
        self,
        local_root: str,
        remote_root: str,
        file_filter: Optional[Callable[[str], bool]] = None
    ) -> bool:
        """
        Sync a local directory to remote (V2 compatibility method)
        
        Args:
            local_root: Local directory root
            remote_root: Remote directory root
            file_filter: Optional filter function for files
            
        Returns:
            bool: True if sync successful
        """
        return await self.v3_manager.upload_directory_sync(local_root, remote_root, file_filter)
    
    async def sync_from_config(self, file_filter: Optional[Callable[[str], bool]] = None) -> bool:
        """
        Sync using configuration paths (V2 compatibility method)
        """
        return await self.v3_manager.sync_from_config(file_filter)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get upload statistics (V2 compatibility method)"""
        return {
            "total_uploads_completed": self.total_uploads_completed,
            "total_uploads_failed": self.total_uploads_failed,
            "total_bytes_uploaded": self.total_bytes_uploaded,
            "active_uploads": len(self.active_uploads),
            "upload_history_count": len(self.upload_history)
        }


# Backward compatibility alias
QUSB2SNESUploadManager = QUSB2SNESUploadManagerV2Adapter