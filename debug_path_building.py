#!/usr/bin/env python3
"""
Debug the folder tree path building logic
"""

from pathlib import PurePosixPath

def debug_path_building(target_path: str):
    """Debug how path segments are built"""
    print(f"Target path: {target_path}")
    
    # Normalize path
    normalized_path = str(PurePosixPath(target_path))
    print(f"Normalized path: {normalized_path}")
    
    # Build list of path segments to create (folder tree approach)
    path_segments = []
    current_path = normalized_path
    
    while current_path != "/" and current_path != "":
        path_obj = PurePosixPath(current_path)
        path_segments.append(current_path)
        current_path = str(path_obj.parent)
        print(f"  Added segment: {path_segments[-1]}, parent: {current_path}")
    
    # Reverse to create from root down (level by level)
    path_segments.reverse()
    
    print(f"Final path segments (in creation order):")
    for i, segment in enumerate(path_segments):
        print(f"  {i+1}. {segment}")
    
    return path_segments

if __name__ == "__main__":
    print("=== Testing path building logic ===")
    print()
    
    test_paths = [
        "/test_qusb_sync_v2",
        "/test_qusb_sync_v2/nested/deep/structure"
    ]
    
    for test_path in test_paths:
        debug_path_building(test_path)
        print()