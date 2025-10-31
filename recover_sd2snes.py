#!/usr/bin/env python3
"""
SD2SNES Recovery Tool
Helps recover an unresponsive SD2SNES device
"""

print("🔧 SD2SNES DEVICE RECOVERY TOOL")
print("=" * 50)
print()
print("Your SD2SNES firmware is unresponsive. This typically happens when:")
print("• A USB2SNES application didn't disconnect properly")
print("• Multiple connections were attempted simultaneously")
print("• The device is in a locked/hung state")
print()
print("🔄 RECOVERY STEPS:")
print()
print("1. IMMEDIATE RECOVERY:")
print("   • Unplug the USB cable from your FXPAK Pro for 10 seconds")
print("   • Plug it back in")
print("   • Power cycle your SuperNT (turn off/on)")
print()
print("2. SOFTWARE CLEANUP:")
print("   • Close ALL USB2SNES applications (QUsb2Snes, RetroAchievements, etc.)")
print("   • Kill any hanging processes in Task Manager")
print("   • Restart QUsb2Snes")
print()
print("3. IF STILL UNRESPONSIVE:")
print("   • Try a different USB cable")
print("   • Try a different USB port (preferably USB 2.0)")
print("   • Remove and reinsert the FXPAK Pro from the SuperNT")
print()
print("4. VERIFY RECOVERY:")
print("   • Open QUsb2Snes and check if device appears")
print("   • Test with a simple application like QFile2Snes")
print()
print("⚠️  IMPORTANT: Once recovered, use our FIXED sync code to prevent this!")
print()
print("Press Enter after you've tried the recovery steps...")
input()

# Test if device is responsive after recovery
import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from qusb2snes_sync import QUSB2SNESSync
    
    async def test_recovery():
        print("\n🧪 Testing device recovery...")
        client = None
        try:
            client = QUSB2SNESSync()
            if await client.connect():
                devices = await client.get_devices()
                if devices:
                    print(f"✅ Device recovered! Found: {devices}")
                    device = devices[0]
                    if await client.attach_device(device):
                        print("✅ Device attachment successful")
                        files = await asyncio.wait_for(client.list_directory("/"), timeout=10.0)
                        print(f"✅ Device fully functional - {len(files)} items accessible")
                        return True
                    else:
                        print("❌ Device still unresponsive - try recovery steps again")
                        return False
                else:
                    print("❌ No devices found - check USB connection")
                    return False
            else:
                print("❌ Cannot connect to QUsb2Snes - is it running?")
                return False
        except Exception as e:
            print(f"❌ Recovery test failed: {e}")
            return False
        finally:
            if client:
                try:
                    await client.disconnect()
                except:
                    pass
    
    result = asyncio.run(test_recovery())
    if result:
        print("\n🎉 DEVICE RECOVERY: SUCCESS")
        print("Your SD2SNES is now responsive and ready for sync operations")
    else:
        print("\n⚠️  DEVICE RECOVERY: INCOMPLETE")
        print("Try the recovery steps again or contact support")

except ImportError:
    print("\n⚠️  Cannot test recovery - missing dependencies")
    print("Manual recovery steps above should still work")