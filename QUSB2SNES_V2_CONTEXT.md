# QUSB2SNES V2 - Critical Context Reference
**ALWAYS REFERENCE THIS FILE TO AVOID RECURRING FAILURES**

## Correct Class Names (STOP GETTING THESE WRONG!)
```python
from qusb2snes_connection import QUSB2SNESConnection
from qusb2snes_device import QUSB2SNESDevice  # NOT QUSB2SNESDeviceManager!
from qusb2snes_filesystem import QUSB2SNESFileSystem  # NOT QUSB2SNESFileSystemManager!
from qusb2snes_upload import QUSB2SNESUploadManager  # This one IS correct
```

## Manager Initialization Pattern (Use This Every Time)
```python
# CORRECT initialization order and parameters:
connection = QUSB2SNESConnection()
await connection.connect()

device = QUSB2SNESDevice(connection)  # Takes connection as parameter
devices = await device.discover_devices()
await device.attach_device(devices[0].name)

filesystem = QUSB2SNESFileSystem(connection)  # Only takes connection!

upload_manager = QUSB2SNESUploadManager(
    connection=connection,
    device_manager=device, 
    filesystem_manager=filesystem
)
```

## Critical Fixes That Must NOT Be Forgotten

### 1. PutFile Command MUST Be Validated (But Not Expected to Respond)
```python
# WRONG (causes connection to close):
response = await self.connection.send_command("PutFile", operands=[path, size], expect_response=True)

# CORRECT (working implementation):
response = await self.connection.send_command("PutFile", operands=[path, size], expect_response=False)
if response is None:
    raise Exception(f"PutFile command failed for {path}")

# NOTE: PutFile is a "no_reply_command" but connection manager still returns status
```

### 2. Directory Type Detection (Fixed Bug)
```python
# QUsb2snes protocol: enum class file_type { FILE = 1, DIRECTORY = 0 }
# 0 = directory, 1 = file (NOT the other way around!)
```

### 3. Working Upload Chunk Timing (From Proven Implementation)
```python
# From working qusb2snes_sync.py - DO NOT CHANGE THESE VALUES:
chunk_size = 512  # Reduced from 1024 for better SD card compatibility

# Progress reporting every 500KB (not arbitrary intervals):
if bytes_sent % (500 * 1024) == 0 or bytes_sent == file_size:
    # Report progress

# Timing delays that work:
if bytes_sent % (64 * 1024) == 0:
    await asyncio.sleep(0.1)  # Longer pause for SD card every 64KB
else:
    await asyncio.sleep(0.005)  # Regular delay from working implementation
```

### 4. Folder Tree Approach (Proven to Work)
- Create directories level by level, NOT recursively
- Check parent directory first before creating subdirectories  
- This prevents connection closure issues from rapid MakeDir operations
- Use `ensure_directory()` method which implements this correctly

### 5. Pre-Upload Directory Creation (Prevents Conflicts)
```python
# For batch uploads, pre-create ALL directories first:
directories = set()
for local_path, remote_path in file_pairs:
    remote_dir = str(Path(remote_path).parent)
    if remote_dir != "/" and remote_dir != ".":
        directories.add(remote_dir)

# Create each directory once, sequentially
for directory in sorted(directories):
    await filesystem_manager.ensure_directory(directory)
```

## Microservice Principles (KEEP IT SIMPLE!)

### Simple ROM Uploader Pattern:
1. `create_file_list()` - Generate list of (local_path, remote_path) tuples
2. `upload_rom_list()` - Foreach loop processing one ROM at a time
3. `upload_file_with_workflow()` - Ensure folder, upload file, update processed.json
4. `update_qusb_last_sync()` - Update timestamp in processed.json

### TDD Approach (Follow This Order):
1. Write simplest possible test with ONE file
2. Test basic workflow: setup → create file → upload → verify
3. Don't add complexity until basic case works
4. Use clear success/failure indicators

### Error Handling Philosophy:
- Return boolean success/failure for simple cases
- Log errors but don't over-complicate exception handling
- Fail fast and clearly indicate what went wrong

## Connection Recovery Patterns That Work

### Before Each Critical Operation:
```python
if not self.connection.is_connected():
    await self.connection.disconnect()
    await asyncio.sleep(1.0)
    await self.connection.connect()
```

### Between Upload Operations:
```python
await asyncio.sleep(0.2)  # Brief pause between files for stability
```

### After Directory Creation:
```python
await asyncio.sleep(0.1)  # Allow SD card to settle after MakeDir
```

## processed.json Integration (Keep Simple)
```python
def update_qusb_last_sync(self, filename: str) -> bool:
    try:
        if not os.path.exists(self.processed_json_path):
            return False
        
        with open(self.processed_json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Find matching entry and update
        for entry in data.values():
            if isinstance(entry, dict) and entry.get('filename') == filename:
                entry['qusb_last_sync'] = datetime.now().isoformat()
                break
        else:
            return False  # No matching entry found
        
        with open(self.processed_json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        return True
    except Exception:
        return False
```

## Recurring Failures to STOP Repeating

1. **Using wrong class names** - Check imports section above FIRST!
2. **Not validating PutFile responses** - Always check response is not None
3. **Overcomplicating simple workflows** - Stick to microservice principles
4. **Forgetting working timing patterns** - Use proven delays from working sync
5. **Not following TDD** - Write simple test first, then implement
6. **Wrong manager initialization** - Follow the pattern above exactly
7. **Batch upload conflicts** - Pre-create directories to avoid conflicts
8. **Not using asyncio.sleep()** - Connection needs brief pauses for stability

## Working Test Pattern (Use This Template)
```python
async def test_simple_workflow():
    # Step 1: Setup managers (use CORRECT class names from above!)
    connection = QUSB2SNESConnection()
    # ... follow initialization pattern
    
    # Step 2: Create ONE test file (keep it simple)
    temp_dir = tempfile.mkdtemp()
    test_file = os.path.join(temp_dir, "test.smc")
    with open(test_file, "wb") as f:
        f.write(b"SMC" + b"T" * 1021)  # 1KB test
    
    # Step 3: Test basic workflow
    file_list = rom_uploader.create_file_list(temp_dir, "/test")
    results = await rom_uploader.upload_rom_list(file_list)
    
    # Step 4: Verify success clearly
    success_count = sum(1 for success in results.values() if success)
    return success_count == len(results)
```

## Troubleshooting Common Issues

### Device Conflict (Most Common Issue)
```
[Device] Device conflict detected for SD2SNES COM3
[Device] ❌ Failed to attach to SD2SNES COM3 after 3 attempts
```
**Cause:** Device is already attached to another application or stuck in attached state

**Solutions (in order of preference):**
1. **Restart QUsb2snes application** - This clears all device attachments
2. Close the main SMWC Downloader application if running
3. Check QUsb2snes application for other attached clients
4. Use device reset utility (see below)
5. In worst case, restart the entire system

**Prevention:** Always ensure proper cleanup in tests and applications

**Device Reset Utility:** Use `python reset_qusb_device.py` to force device cleanup

### Proper Test Cleanup Pattern
```python
async def test_with_proper_cleanup():
    connection = None
    device = None
    try:
        # Test code here
        pass
    finally:
        # ALWAYS cleanup in finally block
        if device:
            try:
                await device.detach_current_device()
            except:
                pass
        if connection:
            try:
                await connection.disconnect()
            except:
                pass
```

### PutFile Command Timeout
```
[Conn-1] Command PutFile timeout after 10.0s
```
**Causes:**
1. QUsb2snes application not running
2. Device not properly connected to QUsb2snes
3. Device attached to wrong application
4. SD2SNES device not in correct mode

**Debug Steps:**
1. Check QUsb2snes application is running
2. Verify device appears in QUsb2snes device list
3. Check if device is attached to another application
4. Ensure SD2SNES is in the correct operating mode

**Quick Test:**
```python
# Add this debug check before upload:
devices = await device.discover_devices()
print(f"Available devices: {[d.name for d in devices]}")
attached = await device.attach_device(devices[0].name)
print(f"Device attachment result: {attached}")
```

### Connection Issues
- Always check `connection.is_connected()` before operations
- QUsb2snes may need to be restarted if connection fails repeatedly
- SD2SNES device may need to be power cycled

## Performance Expectations
- Directory creation: 4/4 directories should be created successfully
- File uploads: Should complete without connection losses
- Timing: ~1-2KB/s upload speed is normal for SD card writes
- Success rate: Should achieve 100% success for small test files

**REMEMBER: We have working V2 modules. The issue is usually:**
- Wrong class names (check imports section)
- Not validating PutFile command (check critical fixes)
- Overcomplicating instead of keeping it simple (follow microservice principles)
- Not using proven timing/recovery patterns (check timing section)

**ALWAYS CHECK THIS DOCUMENT BEFORE WRITING CODE!**
**IF YOU'RE MAKING THE SAME MISTAKE TWICE, UPDATE THIS DOCUMENT!**