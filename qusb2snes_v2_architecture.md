# QUSB2SNES V2 - High-Performance Modular Architecture

## Design Principles
- **Microservice-style modules**: Each component handles one responsibility
- **High performance**: Minimize round trips, persistent connections, batch operations
- **Fault isolation**: Failures in one module don't cascade to others
- **Easy testing**: Each module can be unit tested independently
- **Extensibility**: New features add new modules without touching existing ones

## Core Modules

### 1. Connection Manager (`qusb2snes_connection.py`)
**Responsibility**: WebSocket lifecycle and connection pooling
- Persistent connection management
- Connection health monitoring
- Automatic reconnection with exponential backoff
- Connection state validation
- Proper cleanup and resource management

```python
class QUSB2SNESConnection:
    async def connect() -> bool
    async def disconnect() -> None
    async def send_command(command: dict) -> dict
    async def is_healthy() -> bool
    async def reset_connection() -> bool
```

### 2. Device Manager (`qusb2snes_device.py`) 
**Responsibility**: Device discovery, attachment, and conflict resolution
- Smart device discovery with caching
- One-time attachment per session
- Device conflict detection and resolution
- Device capability detection
- Attachment state management

```python
class QUSB2SNESDevice:
    async def discover_devices() -> List[str]
    async def attach_device(name: str) -> bool
    async def verify_attachment() -> dict
    async def handle_conflicts() -> bool
    async def get_device_info() -> dict
```

### 3. File System Manager (`qusb2snes_filesystem.py`)
**Responsibility**: Remote file operations with intelligent caching
- Directory listing with smart caching
- Batch directory operations
- File existence checking
- Path validation and normalization
- Directory creation with parent handling

```python
class QUSB2SNESFileSystem:
    async def list_directory(path: str, use_cache: bool = True) -> List[str]
    async def ensure_directory(path: str) -> bool
    async def file_exists(path: str) -> bool
    async def batch_check_files(paths: List[str]) -> dict
    def clear_cache(path: str = None) -> None
```

### 4. Upload Manager (`qusb2snes_upload.py`)
**Responsibility**: High-performance file uploads
- Concurrent upload queue management
- Upload progress tracking
- File integrity verification
- Resume capability for failed uploads
- Bandwidth optimization

```python
class QUSB2SNESUpload:
    async def upload_file(local_path: str, remote_path: str) -> bool
    async def upload_batch(file_pairs: List[Tuple[str, str]]) -> dict
    async def verify_upload(remote_path: str, expected_size: int) -> bool
    def get_upload_stats() -> dict
    async def resume_failed_uploads() -> None
```

### 5. Sync Orchestrator (`qusb2snes_sync_v2.py`)
**Responsibility**: High-level sync coordination and strategy
- Sync strategy planning and optimization
- Progress reporting and statistics
- Error recovery and retry logic
- Timestamp management
- User cancellation handling

```python
class QUSB2SNESSync:
    async def sync_hacks() -> dict
    async def plan_sync_strategy(hacks: List[dict]) -> dict
    async def execute_sync_plan(plan: dict) -> dict
    def get_sync_statistics() -> dict
    async def cancel_sync() -> None
```

### 6. Performance Monitor (`qusb2snes_metrics.py`)
**Responsibility**: Performance tracking and optimization
- Upload speed monitoring
- Connection health metrics
- Error rate tracking
- Performance optimization suggestions
- Detailed timing analysis

```python
class QUSB2SNESMetrics:
    def start_timer(operation: str) -> str
    def end_timer(timer_id: str) -> float
    def record_upload(size: int, duration: float) -> None
    def get_performance_report() -> dict
    def suggest_optimizations() -> List[str]
```

## Performance Optimizations

### Connection Strategy
- **Single persistent connection** per sync session
- **Connection health checks** before critical operations
- **Automatic reconnection** with exponential backoff
- **Connection reuse** across multiple operations

### Batch Operations
- **Directory listing caching** to avoid repeated List commands
- **Batch file existence checks** using cached directory data
- **Bulk directory creation** for nested paths
- **Upload queue optimization** for maximum throughput

### Smart Caching
- **Directory structure cache** with TTL and invalidation
- **Device info caching** for session duration
- **Path normalization cache** to avoid recomputation
- **Upload verification cache** to skip re-verification

### Error Handling Strategy
- **Isolated error domains** - filesystem errors don't affect connection
- **Progressive retry** with different strategies per error type
- **Graceful degradation** - continue sync with warnings
- **Error aggregation** - collect and report errors efficiently

## Module Dependencies

```
Sync Orchestrator
├── Connection Manager (core dependency)
├── Device Manager (requires Connection)
├── File System Manager (requires Connection + Device)
├── Upload Manager (requires Connection + Device + FileSystem)
├── Performance Monitor (observes all modules)
└── Config Manager (shared dependency)
```

## Testing Strategy

### Unit Tests
- Each module tested in isolation with mocks
- Performance benchmarks for critical operations
- Error injection testing for fault tolerance
- Cache behavior validation

### Integration Tests
- Module interaction testing
- End-to-end sync workflows
- Performance regression testing
- Real device testing with various scenarios

## Implementation Plan

1. **Connection Manager** - Foundation for all operations
2. **Device Manager** - Build on stable connection
3. **File System Manager** - Enable remote operations
4. **Upload Manager** - Core sync functionality
5. **Performance Monitor** - Observability layer
6. **Sync Orchestrator** - High-level coordination
7. **Integration & Performance Testing** - Validation
8. **Migration from V1** - Replace existing system

## Benefits of This Architecture

### Performance
- **5-10x faster syncs** through connection reuse and batching
- **Reduced network round trips** via intelligent caching
- **Concurrent operations** where protocol allows
- **Optimized upload patterns** for different file sizes

### Reliability
- **Isolated failure domains** - one module failure doesn't cascade
- **Robust error recovery** with module-specific strategies
- **Connection health monitoring** prevents mysterious failures
- **Comprehensive logging** for debugging

### Maintainability
- **Clear separation of concerns** - each module has one job
- **Easy to add features** - new modules don't affect existing ones
- **Simple unit testing** - mock dependencies cleanly
- **Gradual migration** - can replace modules incrementally

### Extensibility
- **Plugin architecture** - new upload strategies, caching policies
- **Configurable behaviors** - different strategies for different use cases
- **Monitoring hooks** - easy to add new metrics and alerts
- **Future protocol support** - can add new device types easily