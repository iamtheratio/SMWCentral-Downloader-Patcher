# SMWCentral Downloader & Patcher - Context Engineer Document

## 📌 Project Overview

**SMWCentral Downloader & Patcher** is a cross-platform desktop application that automates downloading, patching, and organizing Super Mario World ROM hacks from SMWCentral. Built with Python/Tkinter and packaged with PyInstaller, it serves retro gaming enthusiasts who want to streamline hack discovery and play without manual file management.

**Target Users**: Retro gaming enthusiasts, ROM hack players, Super Mario World fans
**Primary Use Case**: One-click download, patch, and organize ROM hacks with clean folder structure
**Cross-Platform**: Windows, macOS, Linux with native file manager integration

---

## 🎯 Feature Intent & Development Philosophy

### Core Value Proposition
- **Simplicity First**: Complex operations behind simple interfaces
- **One-Click Workflow**: Download → Patch → Organize → Play
- **Smart Organization**: Automatic folder structure by difficulty/type
- **Cross-Platform Native**: Platform-specific integrations where beneficial

### Feature Development Guidelines
- **User-Centric Design**: Every feature should solve a real user friction point
- **Progressive Enhancement**: Core functionality works, advanced features add value
- **Error Resilience**: Graceful degradation when services/dependencies fail
- **Transparent Progress**: Users always know what's happening and why

---

## 🧭 UI/UX Flow Patterns

### Navigation Structure
```
Dashboard (Landing) → Download Page → Collection Page → Settings Page
```

### Standard User Flows
1. **First-Time Setup**: Settings → Set ROM Path → Set Output Directory → Download
2. **Regular Usage**: Dashboard → Download (Filters) → Download Selected → View Collection
3. **Management**: Collection → Filter/Search → Open Files → Manage Downloads

### UI Component Hierarchy
- **MainLayout**: Overall app structure and navigation
- **PageManager**: Handles page switching and state
- **NavigationBar**: Persistent navigation with theme controls
- **Pages**: Dashboard, Download, Collection, Settings (self-contained)
- **Components**: Reusable sections (Setup, Filter, Difficulty)

---

## ⚙️ Technical Architecture & Patterns

### Core Module Structure
```
main.py              # Entry point, theme management, app lifecycle
api_pipeline.py      # SMWCentral API integration and download logic
utils.py             # Shared utilities, file operations, mappings
config_manager.py    # Configuration persistence and validation
logging_system.py    # Centralized logging with theme support
patch_handler.py     # ROM patching (IPS/BPS) with file validation
```

### UI Architecture
```
ui/
├── layout.py           # Main application layout
├── page_manager.py     # Page switching logic
├── navigation.py       # Top navigation bar
├── theme_controls.py   # Theme switching UI
├── pages/              # Individual page implementations
├── components/         # Reusable UI components
└── constants/          # UI styling constants
```

### Data Flow Patterns
1. **Configuration**: ConfigManager ↔ UI Components ↔ Persistent Storage
2. **Downloads**: API Pipeline → Temp Files → Patch Handler → Output Organization
3. **Logging**: All Components → LoggingSystem → UI Display with Filtering
4. **Theme**: Theme Controls → Root Application → All UI Components

### Essential Technical Practices

#### Version Management
- **Single Source of Truth**: Only update `VERSION` constant in `main.py`
- **Automated Propagation**: All builds, packages, and metadata derive from this
- **Update Script**: Use `python update_version.py v4.9` for version changes

#### Error Handling Patterns
```python
try:
    # Operation that might fail
    result = risky_operation()
    self.logger.log("✅ Operation succeeded", "Information")
    return result
except Exception as e:
    self.logger.log(f"❌ Operation failed: {str(e)}", "Error")
    return None  # or appropriate fallback
```

#### Async Pattern for Network Operations
```python
async def network_operation():
    try:
        # Async operation with timeout
        result = await asyncio.wait_for(operation(), timeout=10.0)
        return result
    except asyncio.TimeoutError:
        self.logger.log("⚠️ Operation timed out", "Warning")
        return None
```

#### Configuration Pattern
```python
# Reading config
value = self.config.get("setting_name", default_value)

# Writing config (auto-saves)
self.config.set("setting_name", new_value)

# UI binding pattern
self.setting_var = tk.StringVar(value=self.config.get("setting_name", ""))
self.setting_var.trace_add("write", self._on_setting_changed)
```

---

## 🛡️ Constraints & Safeguards

### File System Safety
- **Never overwrite existing files** without explicit user confirmation
- **Validate all paths** before operations - check existence, permissions
- **Atomic operations** where possible - temp files → final location
- **Backup critical files** before modifications (like existing ROMs)

### Network Safety
- **Respect API rate limits** - configurable delays between requests
- **Timeout all network operations** - prevent hanging downloads
- **Validate downloaded content** - file size, headers, integrity checks
- **Graceful fallbacks** - continue operation when non-critical services fail

### Cross-Platform Safety
- **Use pathlib/os.path** for all file operations - never hardcode separators
- **Platform-specific integrations** with fallbacks (e.g., file managers)
- **Icon/asset fallbacks** - PNG for Linux, ICO for Windows, graceful degradation
- **Font safety** - specify fonts with fallbacks, handle missing fonts

### UI/Threading Safety
- **Never block UI thread** - use threading for I/O operations
- **Update UI from main thread only** - use thread-safe callbacks
- **Progress feedback required** - long operations must show progress
- **Cancellation support** - users can cancel long-running operations

### Data Integrity
- **Validate API responses** before processing - check structure and required fields
- **Sanitize file names** - remove/replace invalid characters for filesystem
- **Verify patch integrity** - validate ROM and patch before applying
- **Consistent state** - rollback incomplete operations on failure

---

## 🔬 Test-Driven Development (TDD) Requirements

### MANDATORY: Test-First Development Practice

**CRITICAL RULE**: All code changes MUST follow strict test-first methodology before any implementation in the application.

#### TDD Workflow (NON-NEGOTIABLE)
1. **Write Test First**: Create test scripts to validate the intended functionality
2. **Verify Test Methods**: Determine which methods and functions work through testing
3. **Implementation Only After Tests Pass**: Implement into working application only after tests validate approach
4. **No Assumptions**: Never assume functionality works - always validate with tests
5. **Preserve Existing Code**: Do not change code, layout, UI unless explicitly requested

#### Test Script Development Pattern
```python
# Example test script pattern
#!/usr/bin/env python3
"""
Test script for [FEATURE_NAME] - ALWAYS CREATE BEFORE IMPLEMENTATION
Validates functionality before integrating into main application
"""

import asyncio
import tempfile
import os
import sys

# Add project path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_specific_functionality():
    """Test the specific feature in isolation"""
    print("🧪 Testing [FEATURE_NAME] in isolation...")
    
    # Create isolated test environment
    with tempfile.TemporaryDirectory() as temp_dir:
        # Set up test conditions
        # Test the functionality
        # Validate results
        # Report success/failure
    
    print("✅ Test completed - ready for implementation")

if __name__ == "__main__":
    asyncio.run(test_specific_functionality())
```

#### Required Test Coverage Before Implementation
- **Protocol Tests**: Network/API functionality works as expected
- **Edge Case Tests**: Error conditions, network failures, invalid inputs
- **Integration Tests**: Components work together correctly
- **Cross-Platform Tests**: Functionality works on target platforms
- **UI Tests**: Interface components respond correctly (if UI changes involved)

### Git Workflow Requirements

#### MANDATORY: Commit After Every Implementation

**CRITICAL RULE**: After every implementation to the application, commit code locally for easy rollback capability.

#### Required Commit Pattern
```bash
# After each feature implementation
git add .
git commit -m "feat: [descriptive commit message]

- Implemented [specific functionality]
- Tests validated: [list of test files run]
- Affects: [list of files modified]
- Rollback point for: [feature name]"
```

#### Commit Frequency Requirements
- **After Each Feature**: Individual feature implementations get their own commit
- **After Each UI Change**: Any UI modifications committed separately
- **After Each Bug Fix**: Bug fixes committed individually
- **Before Major Changes**: Commit current state before starting significant modifications

#### Rollback Strategy
- **Individual Feature Rollback**: `git reset --hard HEAD~1` for last feature
- **Selective Rollback**: `git revert [commit-hash]` for specific changes
- **Branch Protection**: Keep working branch clean with atomic commits

---

## 🧪 Testing & Validation

### Testing Categories

#### Unit Tests (File Pattern: `test_*.py`)
- **Protocol Tests**: `test_qusb2snes_protocol.py` - WebSocket protocol validation
- **Connection Tests**: `test_connection_*.py` - Network reliability patterns
- **Sync Tests**: `test_*_sync.py` - File synchronization logic
- **UI Tests**: `test_*_ui.py` - Component isolation testing

#### Integration Testing Patterns
```python
async def test_feature_integration():
    """Test complete feature workflow"""
    # Setup test environment
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create test data
        create_test_files(temp_dir)
        
        # Test the complete workflow
        result = await complete_operation(temp_dir)
        
        # Validate results
        assert_expected_state(result)
        
        # Cleanup handled by context manager
```

#### Cross-Platform Testing
- **Test on all target platforms** - Windows, macOS, Linux
- **Test with different file managers** - platform-specific integrations
- **Test edge cases** - missing dependencies, network failures, permission issues
- **Test theme switching** - ensure UI remains functional in both themes

### Validation Requirements

#### Before Release
- [ ] All existing tests pass on target platforms
- [ ] New features have corresponding tests
- [ ] Manual testing of complete user workflows
- [ ] Error scenarios tested (network failure, missing files, etc.)
- [ ] Theme switching works correctly
- [ ] Cross-platform file operations work
- [ ] Version management system functions

#### Feature Completion Criteria
- [ ] Feature works end-to-end in real scenarios
- [ ] Error handling covers expected failure modes
- [ ] Progress feedback provided for long operations
- [ ] Cross-platform compatibility verified
- [ ] UI integrates cleanly with existing theme system
- [ ] Configuration persisted correctly
- [ ] Logging provides useful information for debugging

---

## 🗣️ Tone & Style Guidelines

### User-Facing Messages
- **Friendly but Direct**: "✅ Download complete!" not "Operation successful"
- **Emoji for Context**: Use emojis to convey meaning quickly (📁 📡 ⚠️ ❌ ✅)
- **Avoid Technical Jargon**: "Connection failed" not "WebSocket handshake error"
- **Actionable Information**: Tell users what to do next when something fails

### Code Comments
- **Explain Why, Not What**: Focus on business logic and edge cases
- **Document Constraints**: Why certain patterns exist, what they prevent
- **Cross-Reference Related Code**: Point to files that interact with current code

### Logging Levels
- **Error**: Operations that failed and impact user experience
- **Warning**: Operations that succeeded but with issues
- **Information**: Normal operation progress and completion
- **Debug**: Technical details for troubleshooting
- **Verbose**: Detailed operation traces

---

## 📎 QUSB2SNES Integration Reference

### Implementation Pattern
The QUSB2SNES feature follows the project's standard integration pattern with specific protocol requirements:

#### Core Integration Files
- **Protocol Layer**: WebSocket communication with QUSB2SNES server (default port 23074)
- **Sync Logic**: Directory comparison and file transfer operations
- **UI Integration**: Settings page configuration and progress display
- **Testing Suite**: Comprehensive protocol and integration tests

#### QUSB2SNES Protocol Documentation
Based on research from [QUSB2SNES GitHub](https://github.com/Skarsnik/QUsb2snes):

**WebSocket Connection**:
- Default endpoint: `ws://localhost:23074` (or legacy `ws://localhost:8080`)
- JSON command format: `{"Opcode": "command", "Space": "SNES", "Operands": ["arg1", "arg2"]}`
- Binary data sent in separate binary messages after command

**Essential Commands**:
- `DeviceList`: Get available devices → `{"Results": ["SD2SNES COM3", "SNES Classic"]}`
- `Attach`: Connect to device → `{"Opcode": "Attach", "Operands": ["SD2SNES COM3"]}`
- `List`: Directory listing → `{"Opcode": "List", "Operands": ["/path"]}`
- `PutFile`: Upload file → `{"Opcode": "PutFile", "Operands": ["/path/file.smc", "A00"]}` + binary data
- `MakeDir`: Create directory → `{"Opcode": "MakeDir", "Operands": ["/new_folder"]}`
- `Remove`: Delete file/folder → `{"Opcode": "Remove", "Operands": ["/path/file"]}`
- `Rename`: Rename file → `{"Opcode": "Rename", "Operands": ["/old", "/new"]}`
- `Info`: Device information → Returns firmware version and capabilities

**File Upload Protocol**:
1. Send `PutFile` command with path and size in hex
2. Send binary data in chunks ≤1024 bytes
3. No response expected for successful uploads

**Error Handling**: Server closes connection on errors

#### ⚠️ CRITICAL SD2SNES CONNECTION CLOSURE RULES ⚠️
**SD2SNES WILL IMMEDIATELY CLOSE THE WEBSOCKET CONNECTION IF:**
1. **Trying to create a directory that already exists** (use List first to check)
2. **Trying to list a directory that doesn't exist** (create directory first)
3. **Trying to upload files to a directory that doesn't exist** (create directory first)
4. **Sending commands too rapidly without delays** (add 0.2-0.5s delays between operations)

**MANDATORY DEFENSIVE APPROACH:**
- **Always List Before Create**: Check if directory exists before creating
- **Always Create Before Upload**: Ensure target directory exists before file operations  
- **Always List After Operations**: Verify success by listing parent directory
- **Use Proper Delays**: 0.2s before List, 0.3s after List, 1.0s after MakeDir
- **Expect Connection Drops**: Implement reconnection logic for any operation failure

**Working Pattern from Successful Implementation:**
```
1. List parent directory → check if subdirectory exists
2. If doesn't exist: Create subdirectory → wait 1.0s → List parent to verify
3. Upload files → wait based on size → List parent directory to verify
4. Progress logging: "QUSB2SNES: Command sent successfully", chunk progress, verification
```

#### Standard QUSB2SNES Workflow
1. **Settings Configuration**: User sets local ROM folder and remote SD card directory
2. **Connection Phase**: WebSocket connect → Device discovery → Device attachment
3. **Sync Analysis**: Compare local vs remote directories → Identify changes
4. **Safe Operations**: Create remote folders → Upload new files → Clean obsolete files
5. **Progress Feedback**: Real-time status updates with emoji indicators

#### Safety Constraints for QUSB2SNES
- **Directory Scope Limitation**: Only operate within user-configured SD card directory
- **Forbidden Directories**: Never allow operations in root `/`, `/sd2snes`, `/saves` or system folders
- **Connection Lifecycle**: Single connection per sync operation - no connection reuse
- **Error Recovery**: Graceful handling of device disconnection or WebSocket failures
- **User Confirmation**: Destructive operations require explicit user consent
- **Logging All Operations**: File transfers, directory changes, errors for audit trail
- **Chunk Size Limits**: File uploads in 1024-byte chunks maximum
- **Timeout Protection**: All network operations must have reasonable timeouts

#### Testing Requirements for QUSB2SNES
**MANDATORY Test Scripts (must pass before implementation)**:
- `test_qusb2snes_basic_connection.py`: Protocol correctness, connection patterns
- `test_qusb2snes_file_operations.py`: File CRUD operations
- `test_qusb2snes_directory_sync.py`: Full sync workflow validation
- `test_qusb2snes_safety.py`: Directory restriction enforcement
- `test_qusb2snes_config.py`: Settings persistence
- `test_qusb2snes_full_integration.py`: Complete feature integration

**Validation Criteria**:
- All WebSocket commands work correctly
- File operations handle large files and nested directories
- Safety restrictions prevent dangerous operations
- Error conditions handled gracefully
- Configuration persists between sessions
- No memory leaks or connection issues

#### UI Integration Guidelines
**Settings Page Layout**:
```
QUSB2SNES Sync Section (between first row and log window)
┌─────────────────────────────────────────────────────────────────┐
│ [✓] Enable QUSB2SNES Sync                                      │
│                                                                 │
│ Host: [localhost     ] Port: [23074] [CONNECT] Device: [dropdown] [REFRESH] │
│ SD Card Folder: [/ROMS                                        ] │
│                                                                 │
│                              [SYNC]                            │
└─────────────────────────────────────────────────────────────────┘
```

**Required UI Components**:
- Enable/disable checkbox with immediate config save
- Host/port text fields with validation
- Connect button with connection status feedback
- Device dropdown populated from DeviceList command
- Refresh button to re-scan devices
- SD Card folder path with validation (no dangerous paths)
- Sync button that triggers complete sync operation
- All status updates logged to existing log window

#### Configuration Requirements
**Settings to Persist**:
```json
{
  "qusb2snes_enabled": false,
  "qusb2snes_host": "localhost", 
  "qusb2snes_port": 23074,
  "qusb2snes_device": "",
  "qusb2snes_remote_folder": "/ROMS"
}
```

**Validation Rules**:
- Host must be valid hostname/IP
- Port must be 1-65535
- Remote folder must not be root, sd2snes, saves
- Remote folder must start with `/`
- Device must be from available device list

---

## 📋 Development Checklist Template

### For New Features
```markdown
## Feature: [Feature Name]

### MANDATORY: Test-First Development
- [ ] Test scripts written BEFORE any implementation
- [ ] Test environment isolated from main application
- [ ] Core functionality validated in test scripts
- [ ] Edge cases and error conditions tested
- [ ] Cross-platform compatibility verified in tests
- [ ] All tests pass before proceeding to implementation

### Planning
- [ ] User workflow defined and documented
- [ ] UI mockups or wireframes created (if UI changes needed)
- [ ] Technical approach planned and validated with tests
- [ ] Error scenarios identified and tested
- [ ] Cross-platform considerations noted and tested

### Implementation (ONLY AFTER TESTS PASS)
- [ ] Core functionality implemented from validated test approach
- [ ] UI integration completed (only if explicitly requested)
- [ ] Error handling implemented based on test findings
- [ ] Progress feedback added
- [ ] Configuration persistence added
- [ ] Logging added with appropriate levels
- [ ] **MANDATORY**: Local commit after implementation

### Validation
- [ ] Original test scripts still pass with implemented code
- [ ] Integration tests cover main workflows
- [ ] Manual testing of complete user workflows
- [ ] No existing functionality broken (regression testing)
- [ ] Theme switching still works (if UI touched)

### Git Workflow
- [ ] **MANDATORY**: Committed locally after implementation
- [ ] Commit message follows required pattern
- [ ] Rollback capability verified
- [ ] Branch state clean and atomic

### Documentation
- [ ] Code comments explain complex logic
- [ ] User-facing changes documented (if any)
- [ ] Test scripts documented for future reference
- [ ] Known limitations from testing documented

### Release Preparation
- [ ] Version updated in main.py if needed
- [ ] Changelog updated
- [ ] All test scripts included in release
- [ ] Build process verified on all platforms
```

## 🚫 Critical "DO NOT" Rules

### Code Modification Restrictions
- **DO NOT** change existing code layout unless explicitly requested
- **DO NOT** modify UI components unless specifically asked
- **DO NOT** alter existing functionality without explicit requirement
- **DO NOT** make assumptions about what "might be better"
- **DO NOT** implement before testing validates the approach
- **DO NOT** skip the test-first methodology under any circumstances

### Implementation Restrictions
- **DO NOT** proceed to implementation if tests fail
- **DO NOT** modify working code without test coverage
- **DO NOT** commit untested changes
- **DO NOT** change file structure without explicit request
- **DO NOT** alter existing workflows unless specifically requested

This context-engineer document serves as the comprehensive guide for maintaining consistency, quality, and user experience across all development activities in the SMWCentral Downloader & Patcher project. **All development must follow the Test-First methodology and git workflow requirements outlined above.**