# V2 Integration & Cleanup Plan

## Phase 1: V2 Integration Testing ✅

### Current Status
- ✅ Output directory ROM sync with timestamp comparison
- ✅ V2 upload architecture (Connection + Device + Upload Manager) 
- ✅ processed.json integration for smart syncing
- ✅ Small-scale integration test (8 files with various scenarios)

### Test Command
```bash
python test_v2_integration_small.py
```

**Test Coverage:**
- Directory scanning (8 test ROMs with different scenarios)
- Timestamp comparison logic (old, new, modified, synced, obsolete)
- V2 connection and upload pipeline
- processed.json updates for tracked files
- Mixed scenarios (files in/not in processed.json)

---

## Phase 2: V2 Component Validation

### Core V2 Components Status
| Component | Status | File | Notes |
|-----------|--------|------|-------|
| Connection Manager | ✅ Working | `qusb2snes_connection.py` | Stable WebSocket management |
| Device Manager | ✅ Working | `qusb2snes_device.py` | Device discovery & attachment |
| FileSystem Manager | ✅ Working | `qusb2snes_filesystem.py` | Directory operations, caching |
| Upload Manager V2 Simple | ✅ Working | `upload_manager_v2_simple.py` | Hybrid V2+V1 patterns |
| Output Directory Sync | ✅ Working | `output_directory_rom_sync.py` | Complete integration |

### Individual Tests to Run
```bash
# Test each component
python test_filesystem_manager_v2.py
python test_upload_manager_v2_simple.py  
python test_device_verification.py
```

---

## Phase 3: File Cleanup & V1 Removal

### Files to REMOVE (V1 Legacy)
```
🗑️ V1 Legacy Files:
- qusb2snes_sync.py                    # Old V1 sync (replace with V2)
- simple_file_uploader.py             # Superseded by upload_manager_v2_simple
- simple_rom_uploader_working.py      # Test file, no longer needed
- qusb2snes_rom_uploader.py          # Old microservice approach
- test_simple_upload.py              # V1 test
- test_simple_rom_uploader.py        # V1 test
- test_qusb2snes_protocol.py         # Low-level protocol test
- test_qusb2snes_ui.py               # UI-specific test
- test_qusb2snes.py                  # Generic test
- test_simple_qusb2snes.py           # Simple test
- test_sync_*.py                     # Various old sync tests
- test_upload_debug.py               # Debug test
- test_connection_*.py               # Connection tests superseded
- test_single_upload.py              # Single upload test
- test_minimal_upload.py             # Minimal test
```

### Files to KEEP & UPDATE
```
✅ Core V2 Architecture:
- qusb2snes_connection.py            # V2 Connection Manager
- qusb2snes_device.py               # V2 Device Manager  
- qusb2snes_filesystem.py           # V2 FileSystem Manager
- upload_manager_v2_simple.py       # V2 Upload Manager
- output_directory_rom_sync.py      # V2 Complete Integration

✅ Tests to KEEP:
- test_v2_integration_small.py      # Main integration test
- test_filesystem_manager_v2.py     # FileSystem tests
- test_upload_manager_v2_simple.py  # Upload manager tests
- test_device_verification.py       # Device verification

🔄 Files to UPDATE:
- qusb2snes_ui.py                   # Update to use V2 sync
- main.py                           # Update QUSB sync integration
```

---

## Phase 4: UI Integration Update

### Update `qusb2snes_ui.py`
**Current:** Uses old `QUSB2SNESSyncManager` from `qusb2snes_sync.py`
**Update to:** Use `OutputDirectoryROMSync` from `output_directory_rom_sync.py`

### Key Changes Needed:
1. **Import change:**
   ```python
   # OLD
   from qusb2snes_sync import QUSB2SNESSyncManager
   
   # NEW  
   from output_directory_rom_sync import OutputDirectoryROMSync
   ```

2. **Sync method change:**
   ```python
   # OLD
   sync_manager.sync_hacks_to_remote()
   
   # NEW
   sync_manager.sync_rom_files()
   ```

3. **Progress handling:** Adapt to new logging interface

---

## Phase 5: Main Application Integration

### Update `main.py` 
**Integration points:**
- QUSB sync button functionality
- Progress reporting
- Error handling
- Settings integration

### Configuration Updates
**Ensure `config.json` includes:**
- `output_dir` (for ROM scanning)
- QUSB2SNES connection settings
- Sync preferences

---

## Phase 6: Final Testing & Validation

### Test Sequence:
1. **Small integration test:** `python test_v2_integration_small.py`
2. **Component tests:** Run all V2 component tests
3. **UI integration test:** Test sync button in main application
4. **End-to-end test:** Full download → patch → sync workflow

### Success Criteria:
- ✅ All V2 components working independently
- ✅ Small-scale integration test passes
- ✅ UI integration works
- ✅ End-to-end workflow successful
- ✅ No V1 legacy code remaining

---

## Deployment Steps

### Step 1: Validate Current V2
```bash
python test_v2_integration_small.py
```

### Step 2: Update UI Integration
- Modify `qusb2snes_ui.py` to use V2 components
- Test sync button functionality

### Step 3: Clean Up Legacy Files
- Remove V1 files listed above
- Update imports throughout project

### Step 4: Final Integration Test
- Test complete workflow: download → sync
- Validate all functionality preserved

### Step 5: Documentation Update
- Update README.md with V2 features
- Update any user documentation

---

## Risk Mitigation

### Backup Strategy:
- Keep V1 files in separate branch before deletion
- Test V2 thoroughly before removing V1
- Maintain rollback capability

### Testing Priority:
1. **Critical Path:** Connection → Device → Upload
2. **Data Safety:** processed.json updates
3. **User Experience:** Progress reporting, error handling
4. **Edge Cases:** File not found, connection loss, device conflicts

---

## Next Actions

1. **Run small integration test** to validate current V2 state
2. **Update UI integration** to use V2 components  
3. **Begin selective file cleanup** (remove obviously unused files)
4. **Test updated UI** with V2 backend
5. **Complete file cleanup** once V2 proven stable