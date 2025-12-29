"""Check what path format exists on disk"""
import os

test_paths = [
    r"D:/SuperNT/Romhacks\Kaizo\03 - Intermediate",  # Mixed (from processed.json)
    r"D:\SuperNT\Romhacks\Kaizo\03 - Intermediate",  # All backslashes
    r"D:/SuperNT/Romhacks/Kaizo/03 - Intermediate",  # All forward slashes
]

print("Checking which path format exists:\n")
for path in test_paths:
    exists = os.path.exists(path)
    normalized = os.path.normpath(path)
    print(f"Path: {path}")
    print(f"  Normalized: {normalized}")
    print(f"  Exists: {'✅ YES' if exists else '❌ NO'}")
    
    if exists:
        # List files
        files = os.listdir(path)
        print(f"  Files found: {len(files)}")
        if files:
            print(f"  Example: {files[0]}")
    print()
