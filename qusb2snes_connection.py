#!/usr/bin/env python3
"""
QUSB2SNES Connection Manager V2
High-performance WebSocket connection management with health monitoring

Key Features:
- Persistent connection with automatic health checks
- Exponential backoff reconnection
- Command queue management
- Resource cleanup and proper disconnect handling
- Performance metrics integration
"""

import asyncio
import json
import logging
import time
from typing import Dict, Optional, Any, Callable
import websockets
from websockets.exceptions import ConnectionClosed, WebSocketException


class ConnectionState:
    """Connection state enumeration"""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting" 
    CONNECTED = "connected"
    RECONNECTING = "reconnecting"
    FAILED = "failed"


class QUSB2SNESConnection:
    """
    High-performance WebSocket connection manager for QUSB2SNES
    
    Handles connection lifecycle, health monitoring, and command execution
    with automatic reconnection and proper error handling.
    """
    
    def __init__(self, host: str = "localhost", port: int = 23074, app_name: str = "SMWCentral-Sync-V2"):
        self.host = host
        self.port = port
        self.app_name = app_name
        self.uri = f"ws://{host}:{port}"
        
        # Connection state
        self.websocket: Optional[websockets.WebSocketServerProtocol] = None
        self.state = ConnectionState.DISCONNECTED
        self.last_ping = 0
        self.connection_id = 0  # Incremental ID for connection tracking
        
        # Command queue for serializing concurrent requests
        self._command_lock = asyncio.Lock()
        
        # Performance tracking
        self.connect_time = 0
        self.command_count = 0
        self.total_command_time = 0
        self.last_command_time = 0
        
        # Configuration
        self.ping_interval = 30.0  # Ping every 30 seconds
        self.command_timeout = 10.0  # Default command timeout
        self.connect_timeout = 5.0  # Connection timeout
        self.max_retries = 3
        self.base_retry_delay = 1.0  # Base delay for exponential backoff
        
        # Callbacks
        self.on_connected: Optional[Callable] = None
        self.on_disconnected: Optional[Callable] = None
        self.on_error: Optional[Callable[[str], None]] = None
        self.on_reconnecting: Optional[Callable] = None
        
        # Logging
        self.logger = logging.getLogger(f"QUSB2SNES.Connection.{self.connection_id}")
        
    def _log_info(self, message: str):
        """Log info message with connection context"""
        self.logger.info(f"[Conn-{self.connection_id}] {message}")
        
    def _log_error(self, message: str):
        """Log error message with connection context"""
        self.logger.error(f"[Conn-{self.connection_id}] {message}")
        if self.on_error:
            self.on_error(message)
            
    def _log_debug(self, message: str):
        """Log debug message with connection context"""
        self.logger.debug(f"[Conn-{self.connection_id}] {message}")
    
    async def connect(self) -> bool:
        """
        Establish connection to QUSB2SNES with proper initialization
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        if self.state == ConnectionState.CONNECTED:
            self._log_debug("Already connected")
            return True
            
        self.state = ConnectionState.CONNECTING
        self.connection_id += 1
        start_time = time.time()
        
        try:
            self._log_info(f"Connecting to QUSB2SNES at {self.uri}")
            
            # Establish WebSocket connection
            self.websocket = await asyncio.wait_for(
                websockets.connect(self.uri),
                timeout=self.connect_timeout
            )
            
            # Send application name for identification
            await self._send_name_command()
            
            # Update state and metrics
            self.state = ConnectionState.CONNECTED
            self.connect_time = time.time() - start_time
            self.last_ping = time.time()
            
            self._log_info(f"Connected successfully in {self.connect_time:.2f}s")
            
            # Start health monitoring
            asyncio.create_task(self._health_monitor())
            
            if self.on_connected:
                self.on_connected()
                
            return True
            
        except asyncio.TimeoutError:
            self._log_error(f"Connection timeout after {self.connect_timeout}s")
            self.state = ConnectionState.FAILED
            return False
            
        except Exception as e:
            self._log_error(f"Connection failed: {str(e)}")
            self.state = ConnectionState.FAILED
            return False
    
    async def _send_name_command(self):
        """Send Name command to identify this client to QUSB2SNES"""
        name_command = {
            "Opcode": "Name", 
            "Operands": [self.app_name]
        }
        
        await self.websocket.send(json.dumps(name_command))
        self._log_debug(f"Sent Name command: {self.app_name}")
        
        # Brief pause to allow server to process
        await asyncio.sleep(0.1)
    
    async def disconnect(self):
        """
        Properly disconnect from QUSB2SNES with cleanup
        """
        if self.state == ConnectionState.DISCONNECTED:
            return
            
        self._log_info("Disconnecting from QUSB2SNES")
        
        try:
            if self.websocket and not self.websocket.closed:
                await self.websocket.close(code=1000, reason="Normal closure")
                
            # Brief wait for cleanup
            await asyncio.sleep(0.1)
            
        except Exception as e:
            self._log_error(f"Disconnect error: {str(e)}")
        finally:
            self.websocket = None
            self.state = ConnectionState.DISCONNECTED
            
            if self.on_disconnected:
                self.on_disconnected()
                
            self._log_info("Disconnected successfully")
    
    async def send_command(self, opcode: str, space: str = "SNES", 
                          operands: Optional[list] = None, 
                          timeout: Optional[float] = None,
                          expect_response: bool = True) -> Optional[Dict[str, Any]]:
        """
        Send command to QUSB2SNES with proper error handling and metrics
        Uses command lock to serialize concurrent requests safely
        
        Args:
            opcode: QUSB2SNES command opcode
            space: Command space (default: "SNES")
            operands: Command operands list
            timeout: Command timeout (uses default if None)
            expect_response: Whether to wait for response
            
        Returns:
            dict: Response data if expect_response=True, status dict otherwise
            None: If command failed
        """
        if not self.is_connected():
            self._log_error("Cannot send command - not connected")
            return None
        
        # Use lock to serialize commands and prevent concurrent recv() calls
        async with self._command_lock:
            return await self._execute_command(opcode, space, operands, timeout, expect_response)
    
    async def _execute_command(self, opcode: str, space: str = "SNES", 
                              operands: Optional[list] = None, 
                              timeout: Optional[float] = None,
                              expect_response: bool = True) -> Optional[Dict[str, Any]]:
        """Internal command execution (called within lock)"""
            
        command = {"Opcode": opcode, "Space": space}
        if operands:
            command["Operands"] = operands
            
        start_time = time.time()
        self.command_count += 1
        
        try:
            # Send command
            await self.websocket.send(json.dumps(command))
            self._log_debug(f"Sent command: {opcode} {operands or ''}")
            
            if not expect_response:
                # Commands like Attach, Name, MakeDir don't send responses
                duration = time.time() - start_time
                self._update_command_metrics(duration)
                return {"status": "ok", "duration": duration}
            
            # Wait for response
            if timeout is None:
                timeout = self.command_timeout
                
            response_text = await asyncio.wait_for(
                self.websocket.recv(), 
                timeout=timeout
            )
            
            # Parse response
            try:
                response = json.loads(response_text)
                duration = time.time() - start_time
                self._update_command_metrics(duration)
                
                self._log_debug(f"Received response for {opcode}: {response}")
                return response
                
            except json.JSONDecodeError as e:
                self._log_error(f"Failed to parse response for {opcode}: {e}")
                # Don't update metrics for failed commands
                self.command_count -= 1
                return None
                
        except asyncio.TimeoutError:
            self._log_error(f"Command {opcode} timeout after {timeout}s")
            # Don't update metrics for failed commands
            self.command_count -= 1
            return None
            
        except ConnectionClosed:
            self._log_error(f"Connection closed during {opcode} command")
            self.state = ConnectionState.DISCONNECTED
            # Don't update metrics for failed commands
            self.command_count -= 1
            return None
            
        except Exception as e:
            self._log_error(f"Command {opcode} failed: {str(e)}")
            # Don't update metrics for failed commands
            self.command_count -= 1
            return None
    
    def is_connected(self) -> bool:
        """Check if connection is healthy and ready for commands"""
        return (self.state == ConnectionState.CONNECTED and 
                self.websocket is not None and 
                not self.websocket.closed)
    
    async def health_check(self) -> bool:
        """
        Perform health check using DeviceList command
        
        Returns:
            bool: True if connection is healthy
        """
        if not self.is_connected():
            return False
            
        try:
            response = await self.send_command("DeviceList", timeout=5.0)
            return response is not None
            
        except Exception:
            return False
    
    async def _health_monitor(self):
        """Background task to monitor connection health"""
        while self.state == ConnectionState.CONNECTED:
            try:
                await asyncio.sleep(self.ping_interval)
                
                if self.state != ConnectionState.CONNECTED:
                    break
                    
                # Check if we need a health check
                time_since_last_command = time.time() - self.last_command_time
                if time_since_last_command > self.ping_interval:
                    
                    if not await self.health_check():
                        self._log_error("Health check failed - connection unhealthy")
                        await self._attempt_reconnect()
                        break
                    else:
                        self._log_debug("Health check passed")
                        
            except asyncio.CancelledError:
                break
            except Exception as e:
                self._log_error(f"Health monitor error: {str(e)}")
    
    async def _attempt_reconnect(self):
        """Attempt to reconnect with exponential backoff"""
        if self.state == ConnectionState.RECONNECTING:
            return  # Already reconnecting
            
        self.state = ConnectionState.RECONNECTING
        
        if self.on_reconnecting:
            self.on_reconnecting()
            
        for attempt in range(self.max_retries):
            delay = self.base_retry_delay * (2 ** attempt)
            self._log_info(f"Reconnection attempt {attempt + 1}/{self.max_retries} in {delay}s")
            
            await asyncio.sleep(delay)
            
            # Clean up old connection
            if self.websocket:
                try:
                    await self.websocket.close()
                except:
                    pass
                self.websocket = None
                
            # Attempt reconnection
            if await self.connect():
                self._log_info("Reconnection successful")
                return
                
        self._log_error("All reconnection attempts failed")
        self.state = ConnectionState.FAILED
    
    def _update_command_metrics(self, duration: float):
        """Update command performance metrics"""
        self.total_command_time += duration
        self.last_command_time = time.time()
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get connection performance metrics"""
        avg_command_time = (self.total_command_time / self.command_count 
                           if self.command_count > 0 else 0)
                           
        return {
            "connection_id": self.connection_id,
            "state": self.state,
            "connect_time": self.connect_time,
            "command_count": self.command_count,
            "total_command_time": self.total_command_time,
            "avg_command_time": avg_command_time,
            "uptime": time.time() - self.last_ping if self.last_ping > 0 else 0
        }
    
    def __repr__(self):
        return f"QUSB2SNESConnection(state={self.state}, commands={self.command_count})"