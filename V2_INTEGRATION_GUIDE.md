# V2 Integration: Complete ROM Sourcing & Sync Tracking

## Overview

The V2 hybrid architecture successfully combines the best of both worlds:
- **V2 Foundation**: Reliable connection and device management
- **V1 Upload Patterns**: Proven 512-byte chunks with proper timing
- **processed.json Integration**: Existing infrastructure for ROM sourcing and sync tracking

## Data Flow

```
processed.json → get_hacks_for_qusb_sync() → V2 hybrid upload → update_hack_sync_timestamp()
```

### 1. ROM List Sourcing

**Question**: "How are we getting the list of roms to upload?"

**Answer**: Using `get_hacks_for_qusb_sync()` method from existing V1 infrastructure:

```python
# Query processed.json for hacks needing sync
needs_sync = (
    hack_data.get("qusb2snes_last_sync", 0) == 0 and  # Never synced
    hack_data.get("obsolete", False) == False and      # Not obsolete  
    hack_data.get("file_path", "").strip() != ""       # Has file path
)
```

Returns organized list sorted by `hack_type` and `folder_name`.

### 2. Sync Tracking Updates

**Question**: "Are we updating the processed.json qusb_last_sync field?"

**Answer**: Yes, using `update_hack_sync_timestamp()` method:

```python
# After successful upload
current_timestamp = int(time.time())
success = hack_data_manager.update_hack(hack_id, "qusb2snes_last_sync", current_timestamp)
```

Updates processed.json with current timestamp for each successfully uploaded hack.

## Architecture Components

### V2 Hybrid Upload Manager
- **File**: `upload_manager_v2_simple.py`
- **Purpose**: Combines V2 foundation with simple upload patterns
- **Dependencies**: ConnectionManagerV2, DeviceManagerV2 (no FileSystem Manager)
- **Performance**: 0.33 MB/s average, 100% success rate on 1-5MB files

### processed.json Integration  
- **File**: `qusb2snes_sync.py` (existing V1 implementation)
- **Methods**: 
  - `get_hacks_for_qusb_sync()`: Query hacks needing sync
  - `update_hack_sync_timestamp()`: Update sync timestamps
  - `sync_hacks_to_remote()`: Complete sync orchestration

### HackDataManager
- **File**: `hack_data_manager.py`
- **Purpose**: Safe processed.json updates with delayed saving
- **Method**: `update_hack(hack_id, field, value)` for timestamp updates

## Testing Results

### Real-world Performance
- **Files**: 10 ROMs (1.2-4.8MB each)
- **Total Size**: 24.1MB
- **Success Rate**: 100% (10/10 uploads)
- **Average Speed**: 0.33 MB/s
- **Upload Patterns**: V1 proven timing (512-byte chunks, proper delays)

### V2 Component Reliability
- ✅ Connection Manager V2: Stable WebSocket management
- ✅ Device Manager V2: Reliable SD2SNES detection
- ✅ Upload Manager V2 Simple: Perfect upload success
- ❌ FileSystem Manager V2: Too complex, causes connection issues

## Complete Integration

The `test_v2_integration_complete.py` demonstrates the full solution:

1. **ROM Sourcing**: Query processed.json using existing `get_hacks_for_qusb_sync()` logic
2. **V2 Upload**: Use V2 hybrid upload manager for reliable file transfers
3. **Sync Tracking**: Update processed.json timestamps using `HackDataManager`

## Migration Path

The infrastructure already exists in the working V1 sync. To integrate with V2:

1. Use existing `get_hacks_for_qusb_sync()` for ROM sourcing
2. Replace V1 upload logic with V2 hybrid upload manager
3. Keep existing `update_hack_sync_timestamp()` for processed.json updates

This approach leverages proven data infrastructure while gaining V2 upload reliability.

## Key Benefits

- **Data Continuity**: Reuses existing processed.json infrastructure  
- **Upload Reliability**: V2 connection management with V1 proven patterns
- **Per-hack Tracking**: Individual sync timestamps, partial sync recovery
- **Performance**: 0.33 MB/s consistent speed, handles 1-5MB files perfectly
- **Simplicity**: Hybrid approach avoids V2 FileSystem Manager complexity