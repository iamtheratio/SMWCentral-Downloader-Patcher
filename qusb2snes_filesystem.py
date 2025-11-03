#!/usr/bin/env python3
"""
QUSB2SNES File System Manager V2
Intelligent remote file system operations with caching and batch processing

Key Features:
- Smart directory listing with TTL-based caching
- Batch file existence checking to minimize round trips
- Hierarchical directory creation with parent handling
- Path normalization and validation
- Performance-optimized file operations
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass
from pathlib import PurePosixPath

from qusb2snes_connection import QUSB2SNESConnection


@dataclass
class DirectoryEntry:
    """Remote directory entry information"""
    name: str
    is_directory: bool
    size: Optional[int] = None
    last_seen: float = 0
    
    def __post_init__(self):
        if self.last_seen == 0:
            self.last_seen = time.time()


@dataclass
class CachedDirectory:
    """Cached directory listing with metadata"""
    path: str
    entries: Dict[str, DirectoryEntry]
    cached_at: float
    ttl: float = 60.0  # Default 60 second TTL
    
    def is_expired(self) -> bool:
        """Check if cache entry has expired"""
        return time.time() - self.cached_at > self.ttl
    
    def get_entry(self, name: str) -> Optional[DirectoryEntry]:
        """Get specific entry from cache"""
        return self.entries.get(name)
    
    def has_file(self, name: str) -> bool:
        """Check if file exists in cached directory"""
        entry = self.entries.get(name)
        return entry is not None and not entry.is_directory
    
    def has_directory(self, name: str) -> bool:
        """Check if directory exists in cached directory"""
        entry = self.entries.get(name)
        return entry is not None and entry.is_directory


class QUSB2SNESFileSystem:
    """
    High-performance file system manager for QUSB2SNES
    
    Provides intelligent caching, batch operations, and optimized
    directory management for remote file systems.
    """
    
    def __init__(self, connection: QUSB2SNESConnection):
        self.connection = connection
        
        # Directory cache
        self.directory_cache: Dict[str, CachedDirectory] = {}
        self.default_cache_ttl = 60.0  # 60 seconds default TTL
        
        # Path normalization cache
        self.normalized_paths: Dict[str, str] = {}
        
        # Performance tracking
        self.cache_hits = 0
        self.cache_misses = 0
        self.operations_count = 0
        self.total_operation_time = 0
        
        # Configuration
        self.list_timeout = 15.0
        self.batch_size = 50  # Maximum items per batch operation
        
        # Logging
        self.logger = logging.getLogger("QUSB2SNES.FileSystem")
    
    def _log_info(self, message: str):
        """Log info message"""
        self.logger.info(f"[FileSystem] {message}")
        
    def _log_error(self, message: str):
        """Log error message"""
        self.logger.error(f"[FileSystem] {message}")
        
    def _log_debug(self, message: str):
        """Log debug message"""
        self.logger.debug(f"[FileSystem] {message}")
    
    def _normalize_path(self, path: str) -> str:
        """
        Normalize path for consistent caching and operations
        
        Args:
            path: Raw path string
            
        Returns:
            Normalized path string
        """
        if path in self.normalized_paths:
            return self.normalized_paths[path]
        
        # Use PurePosixPath for consistent path handling
        normalized = str(PurePosixPath(path))
        
        # Ensure root path consistency
        if normalized == ".":
            normalized = "/"
        elif not normalized.startswith("/"):
            normalized = "/" + normalized
            
        # Cache normalized path
        self.normalized_paths[path] = normalized
        return normalized
    
    async def list_directory(self, path: str, use_cache: bool = True, 
                           cache_ttl: Optional[float] = None) -> Optional[List[DirectoryEntry]]:
        """
        List directory contents with intelligent caching
        
        Args:
            path: Directory path to list
            use_cache: Whether to use cached results if available
            cache_ttl: Custom TTL for this cache entry
            
        Returns:
            List of directory entries, or None if failed
        """
        normalized_path = self._normalize_path(path)
        start_time = time.time()
        self.operations_count += 1
        
        # Check cache first
        if use_cache and normalized_path in self.directory_cache:
            cached_dir = self.directory_cache[normalized_path]
            if not cached_dir.is_expired():
                self.cache_hits += 1
                duration = time.time() - start_time
                self.total_operation_time += duration
                
                self._log_debug(f"Cache hit for directory: {normalized_path} "
                               f"({len(cached_dir.entries)} entries)")
                return list(cached_dir.entries.values())
        
        # Cache miss - fetch from remote
        self.cache_misses += 1
        self._log_debug(f"Listing directory: {normalized_path}")
        
        try:
            response = await self.connection.send_command(
                "List", 
                operands=[normalized_path], 
                timeout=self.list_timeout
            )
            
            if not response or "Results" not in response:
                self._log_error(f"Failed to list directory: {normalized_path}")
                return None
            
            # Parse directory listing
            results = response["Results"]
            entries = {}
            
            # QUSB2SNES List format: [type, name, type, name, ...]
            # type: "0" = file, "1" = directory
            for i in range(0, len(results), 2):
                if i + 1 < len(results):
                    entry_type = results[i]
                    entry_name = results[i + 1]
                    
                    is_directory = entry_type == "1"
                    
                    entries[entry_name] = DirectoryEntry(
                        name=entry_name,
                        is_directory=is_directory,
                        last_seen=time.time()
                    )
            
            # Cache the results
            ttl = cache_ttl or self.default_cache_ttl
            self.directory_cache[normalized_path] = CachedDirectory(
                path=normalized_path,
                entries=entries,
                cached_at=time.time(),
                ttl=ttl
            )
            
            duration = time.time() - start_time
            self.total_operation_time += duration
            
            self._log_info(f"Listed directory {normalized_path}: {len(entries)} entries in {duration:.3f}s")
            return list(entries.values())
            
        except Exception as e:
            self._log_error(f"List directory failed for {normalized_path}: {str(e)}")
            return None
    
    async def file_exists(self, file_path: str, use_cache: bool = True) -> bool:
        """
        Check if file exists using cached directory data when possible
        
        Args:
            file_path: Full file path to check
            use_cache: Whether to use cached directory data
            
        Returns:
            bool: True if file exists
        """
        normalized_path = self._normalize_path(file_path)
        
        # Split path into directory and filename
        path_obj = PurePosixPath(normalized_path)
        directory = str(path_obj.parent)
        filename = path_obj.name
        
        # Try to use cached directory listing
        if use_cache and directory in self.directory_cache:
            cached_dir = self.directory_cache[directory]
            if not cached_dir.is_expired():
                return cached_dir.has_file(filename)
        
        # Fall back to listing the directory
        entries = await self.list_directory(directory, use_cache=use_cache)
        if entries is None:
            return False
        
        # Check if file exists in the listing
        for entry in entries:
            if entry.name == filename and not entry.is_directory:
                return True
        
        return False
    
    async def directory_exists(self, dir_path: str, use_cache: bool = True) -> bool:
        """
        Check if directory exists using cached data when possible
        
        Args:
            dir_path: Directory path to check
            use_cache: Whether to use cached directory data
            
        Returns:
            bool: True if directory exists
        """
        normalized_path = self._normalize_path(dir_path)
        
        # Root directory always exists
        if normalized_path == "/":
            return True
        
        # Split path into parent directory and directory name
        path_obj = PurePosixPath(normalized_path)
        parent_dir = str(path_obj.parent)
        dir_name = path_obj.name
        
        # Try to use cached parent directory listing
        if use_cache and parent_dir in self.directory_cache:
            cached_dir = self.directory_cache[parent_dir]
            if not cached_dir.is_expired():
                return cached_dir.has_directory(dir_name)
        
        # Fall back to listing the parent directory
        entries = await self.list_directory(parent_dir, use_cache=use_cache)
        if entries is None:
            return False
        
        # Check if directory exists in the listing
        for entry in entries:
            if entry.name == dir_name and entry.is_directory:
                return True
        
        return False
    
    async def ensure_directory(self, dir_path: str) -> bool:
        """
        Ensure directory exists, creating it and parents if necessary
        
        Args:
            dir_path: Directory path to ensure exists
            
        Returns:
            bool: True if directory exists or was created successfully
        """
        normalized_path = self._normalize_path(dir_path)
        
        # Check if directory already exists
        if await self.directory_exists(normalized_path):
            self._log_debug(f"Directory already exists: {normalized_path}")
            return True
        
        # Create parent directories first
        path_obj = PurePosixPath(normalized_path)
        parent_dir = str(path_obj.parent)
        
        if parent_dir != "/" and parent_dir != normalized_path:
            parent_created = await self.ensure_directory(parent_dir)
            if not parent_created:
                self._log_error(f"Failed to create parent directory: {parent_dir}")
                return False
        
        # Create the directory
        try:
            self._log_info(f"Creating directory: {normalized_path}")
            
            result = await self.connection.send_command(
                "MakeDir",
                operands=[normalized_path],
                expect_response=False
            )
            
            if result and result.get("status") == "ok":
                # Invalidate parent directory cache to reflect new directory
                parent_dir = str(PurePosixPath(normalized_path).parent)
                if parent_dir in self.directory_cache:
                    del self.directory_cache[parent_dir]
                
                self._log_info(f"✅ Created directory: {normalized_path}")
                return True
            else:
                self._log_error(f"❌ Failed to create directory: {normalized_path}")
                return False
                
        except Exception as e:
            self._log_error(f"Create directory failed for {normalized_path}: {str(e)}")
            return False
    
    async def batch_check_files(self, file_paths: List[str]) -> Dict[str, bool]:
        """
        Check existence of multiple files efficiently using cached data
        
        Args:
            file_paths: List of file paths to check
            
        Returns:
            Dictionary mapping file paths to existence status
        """
        results = {}
        directories_to_list = set()
        
        # Group files by directory to minimize List operations
        file_groups: Dict[str, List[str]] = {}
        
        for file_path in file_paths:
            normalized_path = self._normalize_path(file_path)
            path_obj = PurePosixPath(normalized_path)
            directory = str(path_obj.parent)
            filename = path_obj.name
            
            if directory not in file_groups:
                file_groups[directory] = []
            file_groups[directory].append((normalized_path, filename))
        
        # Process each directory group
        for directory, files in file_groups.items():
            # List directory once for all files in it
            entries = await self.list_directory(directory, use_cache=True)
            
            if entries is None:
                # Directory listing failed - mark all files as not found
                for file_path, _ in files:
                    results[file_path] = False
                continue
            
            # Create lookup set for efficient checking
            file_names = {entry.name for entry in entries if not entry.is_directory}
            
            # Check each file in this directory
            for file_path, filename in files:
                results[file_path] = filename in file_names
        
        self._log_info(f"Batch checked {len(file_paths)} files across {len(file_groups)} directories")
        return results
    
    def clear_cache(self, path: Optional[str] = None):
        """
        Clear directory cache
        
        Args:
            path: Specific path to clear (clears all if None)
        """
        if path is None:
            cache_size = len(self.directory_cache)
            self.directory_cache.clear()
            self.normalized_paths.clear()
            self._log_info(f"Cleared entire cache ({cache_size} entries)")
        else:
            normalized_path = self._normalize_path(path)
            if normalized_path in self.directory_cache:
                del self.directory_cache[normalized_path]
                self._log_debug(f"Cleared cache for: {normalized_path}")
    
    def invalidate_path(self, path: str):
        """
        Invalidate cache for specific path and its parents
        
        Args:
            path: Path to invalidate
        """
        normalized_path = self._normalize_path(path)
        
        # Invalidate the path itself
        if normalized_path in self.directory_cache:
            del self.directory_cache[normalized_path]
        
        # Invalidate parent directory (since it now contains new/changed item)
        parent_path = str(PurePosixPath(normalized_path).parent)
        if parent_path in self.directory_cache:
            del self.directory_cache[parent_path]
        
        self._log_debug(f"Invalidated cache for: {normalized_path}")
    
    def get_cache_stats(self) -> Dict[str, any]:
        """Get cache performance statistics"""
        total_requests = self.cache_hits + self.cache_misses
        hit_rate = (self.cache_hits / total_requests * 100) if total_requests > 0 else 0
        
        avg_operation_time = (self.total_operation_time / self.operations_count 
                             if self.operations_count > 0 else 0)
        
        return {
            "cache_entries": len(self.directory_cache),
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "hit_rate_percent": hit_rate,
            "operations_count": self.operations_count,
            "avg_operation_time": avg_operation_time,
            "total_operation_time": self.total_operation_time
        }
    
    def get_performance_metrics(self) -> Dict[str, any]:
        """Get comprehensive performance metrics"""
        stats = self.get_cache_stats()
        
        # Add cache efficiency metrics
        expired_entries = sum(1 for cache in self.directory_cache.values() if cache.is_expired())
        
        stats.update({
            "expired_cache_entries": expired_entries,
            "normalized_paths_cached": len(self.normalized_paths),
            "cache_efficiency": stats["hit_rate_percent"],
            "avg_entries_per_directory": (
                sum(len(cache.entries) for cache in self.directory_cache.values()) /
                len(self.directory_cache) if self.directory_cache else 0
            )
        })
        
        return stats
    
    def __repr__(self):
        cache_count = len(self.directory_cache)
        hit_rate = (self.cache_hits / (self.cache_hits + self.cache_misses) * 100 
                   if (self.cache_hits + self.cache_misses) > 0 else 0)
        return f"QUSB2SNESFileSystem(cache_entries={cache_count}, hit_rate={hit_rate:.1f}%)"