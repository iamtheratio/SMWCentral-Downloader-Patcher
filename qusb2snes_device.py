#!/usr/bin/env python3
"""
QUSB2SNES Device Manager V2
Smart device discovery, attachment, and conflict resolution

Key Features:
- Intelligent device discovery with caching
- One-time attachment per session with state persistence
- Advanced conflict detection and resolution
- Device capability detection and validation
- Comprehensive error recovery strategies
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from enum import Enum

from qusb2snes_connection import QUSB2SNESConnection


class DeviceState(Enum):
    """Device attachment states"""
    UNKNOWN = "unknown"
    AVAILABLE = "available"
    ATTACHED = "attached"
    BUSY = "busy"
    ERROR = "error"


@dataclass
class DeviceInfo:
    """Device information and capabilities"""
    name: str
    state: DeviceState
    firmware_version: str = ""
    device_type: str = ""
    current_file: str = ""
    features: List[str] = None
    last_seen: float = 0
    attach_time: float = 0
    
    def __post_init__(self):
        if self.features is None:
            self.features = []
        if self.last_seen == 0:
            self.last_seen = time.time()


class QUSB2SNESDevice:
    """
    High-performance device manager for QUSB2SNES
    
    Handles device discovery, attachment lifecycle, and conflict resolution
    with intelligent caching and state management.
    """
    
    def __init__(self, connection: QUSB2SNESConnection):
        self.connection = connection
        self.attached_device: Optional[DeviceInfo] = None
        self.discovered_devices: Dict[str, DeviceInfo] = {}
        
        # Caching configuration
        self.device_cache_ttl = 30.0  # Cache devices for 30 seconds
        self.last_discovery = 0
        
        # Attachment configuration
        self.attach_timeout = 10.0
        self.attach_wait_time = 1.0  # Wait after attach before verification
        self.max_attach_retries = 3
        
        # Conflict resolution configuration
        self.conflict_retry_delay = 2.0
        self.max_conflict_retries = 3
        
        # Callbacks
        self.on_device_attached: Optional[Callable[[DeviceInfo], None]] = None
        self.on_device_detached: Optional[Callable[[], None]] = None
        self.on_conflict_detected: Optional[Callable[[str], None]] = None
        
        # Logging
        self.logger = logging.getLogger("QUSB2SNES.Device")
    
    def _log_info(self, message: str):
        """Log info message"""
        self.logger.info(f"[Device] {message}")
        
    def _log_error(self, message: str):
        """Log error message"""
        self.logger.error(f"[Device] {message}")
        
    def _log_debug(self, message: str):
        """Log debug message"""
        self.logger.debug(f"[Device] {message}")
    
    async def discover_devices(self, use_cache: bool = True) -> List[DeviceInfo]:
        """
        Discover available devices with intelligent caching
        
        Args:
            use_cache: Whether to use cached results if available
            
        Returns:
            List of discovered devices with their information
        """
        # Check cache validity
        cache_age = time.time() - self.last_discovery
        if use_cache and cache_age < self.device_cache_ttl and self.discovered_devices:
            self._log_debug(f"Using cached device list ({cache_age:.1f}s old)")
            return list(self.discovered_devices.values())
        
        self._log_info("Discovering devices...")
        
        try:
            # Get device list from QUSB2SNES
            response = await self.connection.send_command("DeviceList", timeout=5.0)
            
            if not response or "Results" not in response:
                self._log_error("Failed to get device list")
                return []
            
            device_names = response["Results"]
            self._log_info(f"Found {len(device_names)} devices: {device_names}")
            
            # Update device information
            current_devices = {}
            for name in device_names:
                if name in self.discovered_devices:
                    # Update existing device
                    device = self.discovered_devices[name]
                    device.last_seen = time.time()
                    device.state = DeviceState.AVAILABLE
                else:
                    # Create new device entry
                    device = DeviceInfo(
                        name=name,
                        state=DeviceState.AVAILABLE,
                        last_seen=time.time()
                    )
                
                current_devices[name] = device
            
            # Update cache
            self.discovered_devices = current_devices
            self.last_discovery = time.time()
            
            return list(current_devices.values())
            
        except Exception as e:
            self._log_error(f"Device discovery failed: {str(e)}")
            return []
    
    async def get_device_info(self, device_name: Optional[str] = None) -> Optional[DeviceInfo]:
        """
        Get detailed device information using Info command
        
        Args:
            device_name: Device to get info for (uses attached device if None)
            
        Returns:
            DeviceInfo with detailed information, or None if failed
        """
        target_device = device_name or (self.attached_device.name if self.attached_device else None)
        
        if not target_device:
            self._log_error("No device specified or attached for Info command")
            return None
        
        try:
            self._log_debug(f"Getting info for device: {target_device}")
            response = await self.connection.send_command("Info", timeout=8.0)
            
            if not response or "Results" not in response:
                self._log_error(f"Failed to get info for device {target_device}")
                return None
            
            info = response["Results"]
            
            # Parse device info
            device_info = DeviceInfo(
                name=target_device,
                state=DeviceState.ATTACHED,
                firmware_version=info[0] if len(info) > 0 else "",
                device_type=info[1] if len(info) > 1 else "",
                current_file=info[2] if len(info) > 2 else "",
                features=info[3:] if len(info) > 3 else [],
                last_seen=time.time()
            )
            
            # Update cache
            self.discovered_devices[target_device] = device_info
            if self.attached_device and self.attached_device.name == target_device:
                self.attached_device = device_info
            
            self._log_info(f"Device info: {device_info.device_type} v{device_info.firmware_version}, "
                          f"{len(device_info.features)} features")
            
            return device_info
            
        except Exception as e:
            self._log_error(f"Failed to get device info: {str(e)}")
            return None
    
    async def attach_device(self, device_name: str) -> bool:
        """
        Attach to specific device with smart retry and conflict resolution
        
        Args:
            device_name: Name of device to attach to
            
        Returns:
            bool: True if attachment successful
        """
        # Check if already attached to this device
        if self.is_attached(device_name):
            self._log_debug(f"Already attached to {device_name}")
            return True
        
        # Check if attached to different device
        if self.attached_device:
            self._log_info(f"Detaching from {self.attached_device.name} before attaching to {device_name}")
            await self.detach_device()
        
        self._log_info(f"Attaching to device: {device_name}")
        
        for attempt in range(self.max_attach_retries):
            try:
                # Send attach command
                attach_result = await self.connection.send_command(
                    "Attach", 
                    operands=[device_name], 
                    expect_response=False,
                    timeout=self.attach_timeout
                )
                
                if not attach_result or attach_result.get("status") != "ok":
                    self._log_error(f"Attach command failed for {device_name}")
                    continue
                
                # Wait for device to be ready
                self._log_debug(f"Waiting {self.attach_wait_time}s for device readiness...")
                await asyncio.sleep(self.attach_wait_time)
                
                # Verify attachment with Info command
                device_info = await self.get_device_info(device_name)
                
                if device_info:
                    # Success!
                    device_info.state = DeviceState.ATTACHED
                    device_info.attach_time = time.time()
                    self.attached_device = device_info
                    
                    self._log_info(f"✅ Successfully attached to {device_name}")
                    
                    if self.on_device_attached:
                        self.on_device_attached(device_info)
                    
                    return True
                else:
                    # Attachment failed - likely device conflict
                    conflict_handled = await self._handle_device_conflict(device_name, attempt + 1)
                    if not conflict_handled:
                        continue
                
            except Exception as e:
                self._log_error(f"Attach attempt {attempt + 1} failed: {str(e)}")
                
                if attempt < self.max_attach_retries - 1:
                    await asyncio.sleep(self.conflict_retry_delay)
        
        self._log_error(f"❌ Failed to attach to {device_name} after {self.max_attach_retries} attempts")
        return False
    
    async def detach_device(self) -> bool:
        """
        Detach from currently attached device
        
        Returns:
            bool: True if detachment successful
        """
        if not self.attached_device:
            self._log_debug("No device attached")
            return True
        
        device_name = self.attached_device.name
        self._log_info(f"Detaching from device: {device_name}")
        
        try:
            # Update device state
            self.attached_device.state = DeviceState.AVAILABLE
            old_device = self.attached_device
            self.attached_device = None
            
            # Note: QUSB2SNES doesn't have explicit detach command
            # Device is automatically detached when connection closes or new device attaches
            
            self._log_info(f"✅ Detached from {device_name}")
            
            if self.on_device_detached:
                self.on_device_detached()
            
            return True
            
        except Exception as e:
            self._log_error(f"Detach failed: {str(e)}")
            return False
    
    async def _handle_device_conflict(self, device_name: str, attempt: int) -> bool:
        """
        Handle device conflicts with intelligent strategies
        
        Args:
            device_name: Device that had conflict
            attempt: Current attempt number
            
        Returns:
            bool: True if conflict was resolved
        """
        self._log_error(f"Device conflict detected for {device_name} (attempt {attempt})")
        
        if self.on_conflict_detected:
            self.on_conflict_detected(device_name)
        
        # Strategy 1: Wait for other application to release device
        if attempt <= 2:
            wait_time = self.conflict_retry_delay * attempt
            self._log_info(f"Waiting {wait_time}s for device to become available...")
            await asyncio.sleep(wait_time)
            return True
        
        # Strategy 2: Force refresh device list
        if attempt == 3:
            self._log_info("Refreshing device list...")
            await self.discover_devices(use_cache=False)
            return True
        
        return False
    
    def is_attached(self, device_name: Optional[str] = None) -> bool:
        """
        Check if device is attached
        
        Args:
            device_name: Device to check (checks any attachment if None)
            
        Returns:
            bool: True if specified device (or any device) is attached
        """
        if not self.attached_device:
            return False
        
        if device_name is None:
            return True
        
        return self.attached_device.name == device_name
    
    def get_attached_device(self) -> Optional[DeviceInfo]:
        """Get currently attached device info"""
        return self.attached_device
    
    def get_device_capabilities(self, device_name: Optional[str] = None) -> List[str]:
        """
        Get device capabilities/features
        
        Args:
            device_name: Device to check (uses attached device if None)
            
        Returns:
            List of device capabilities
        """
        target_device = device_name or (self.attached_device.name if self.attached_device else None)
        
        if not target_device or target_device not in self.discovered_devices:
            return []
        
        return self.discovered_devices[target_device].features
    
    def has_capability(self, capability: str, device_name: Optional[str] = None) -> bool:
        """
        Check if device has specific capability
        
        Args:
            capability: Capability to check for
            device_name: Device to check (uses attached device if None)
            
        Returns:
            bool: True if device has the capability
        """
        capabilities = self.get_device_capabilities(device_name)
        return capability in capabilities
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get device management performance metrics"""
        return {
            "attached_device": self.attached_device.name if self.attached_device else None,
            "discovered_devices": len(self.discovered_devices),
            "cache_age": time.time() - self.last_discovery,
            "attach_time": self.attached_device.attach_time if self.attached_device else 0,
            "session_duration": time.time() - self.attached_device.attach_time if self.attached_device else 0
        }
    
    def __repr__(self):
        attached = self.attached_device.name if self.attached_device else "None"
        return f"QUSB2SNESDevice(attached={attached}, discovered={len(self.discovered_devices)})"