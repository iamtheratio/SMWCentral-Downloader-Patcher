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
The QUSB2SNES feature follows the project's standard integration pattern:

#### Core Integration Files
- **Protocol Layer**: WebSocket communication with QUSB2SNES server
- **Sync Logic**: Directory comparison and file transfer operations
- **UI Integration**: Settings page configuration and progress display
- **Testing Suite**: Comprehensive protocol and integration tests

#### Standard QUSB2SNES Workflow
1. **Settings Configuration**: User sets local ROM folder and remote SD card directory
2. **Connection Phase**: WebSocket connect → Device discovery → Device attachment
3. **Sync Analysis**: Compare local vs remote directories → Identify changes
4. **Safe Operations**: Create remote folders → Upload new files → Clean obsolete files
5. **Progress Feedback**: Real-time status updates with emoji indicators

#### Safety Constraints for QUSB2SNES
- **Directory Scope Limitation**: Only operate within user-configured SD card directory
- **Connection Lifecycle**: Single connection per sync operation - no connection reuse
- **Error Recovery**: Graceful handling of device disconnection or WebSocket failures
- **User Confirmation**: Destructive operations require explicit user consent
- **Logging All Operations**: File transfers, directory changes, errors for audit trail

#### Testing Requirements
- Protocol correctness with `test_qusb2snes_protocol.py`
- Connection patterns with `test_connection_*.py`
- File operations with `test_*_sync.py`
- UI integration with `test_qusb2snes_ui.py`

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