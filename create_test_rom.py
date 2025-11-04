#!/usr/bin/env python3
"""
Create a small test ROM for upload testing
"""

import os

def create_test_rom():
    """Create a small test ROM file"""
    rom_data = b"SMW_TEST_ROM" + b"\x00" * (1024 - 12)  # 1KB test file
    
    with open("test_rom.smc", "wb") as f:
        f.write(rom_data)
    
    print(f"✅ Created test_rom.smc ({len(rom_data)} bytes)")
    return "test_rom.smc"

if __name__ == "__main__":
    create_test_rom()