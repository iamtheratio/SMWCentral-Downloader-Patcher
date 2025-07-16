"""
BPS Patching functionality for SMWCentral Downloader & Patcher
"""
import io
import os
import time
from typing import Tuple, Optional
import bps

class Patch:
    def __init__(self, patch_data):
        self.patch_data = patch_data
        self.patch_file_path = None
    
    @classmethod
    def load(cls, filepath):
        """Load a BPS patch from file"""
        patch = cls(None)
        patch.patch_file_path = filepath
        with open(filepath, 'rb') as f:
            patch.patch_data = f.read()
        return patch
    
    def apply(self, source_data):
        """Apply the BPS patch to source data and return patched data"""
        # Remove header if present
        if len(source_data) == 524800:  # 512KB header + 512KB ROM
            source_data = source_data[512:]
        
        # Compatibility fix for Python 3.8+ where time.clock was removed
        if not hasattr(time, 'clock'):
            time.clock = time.perf_counter
        
        try:
            # Import BPS module
            from bps import apply
            
            # Create temporary files for the BPS library
            import tempfile
            
            with tempfile.NamedTemporaryFile(delete=False) as temp_source:
                temp_source.write(source_data)
                temp_source_path = temp_source.name
            
            with tempfile.NamedTemporaryFile(delete=False) as temp_output:
                temp_output_path = temp_output.name
            
            try:
                # Apply patch using file method (most reliable)
                with open(self.patch_file_path, 'rb') as patch_f, \
                     open(temp_source_path, 'rb') as source_f, \
                     open(temp_output_path, 'wb') as target_f:
                    
                    apply.apply_to_files(patch_f, source_f, target_f)
                
                # Read the result
                with open(temp_output_path, 'rb') as f:
                    result = f.read()
                
                return result
                
            except Exception as e:
                # Fallback to bytearrays method
                try:
                    patch_file_obj = io.BytesIO(self.patch_data)
                    patch_operations = apply.read_bps(patch_file_obj)
                    source_data_array = bytearray(source_data)
                    target_data_array = bytearray()
                    
                    apply.apply_to_bytearrays(patch_operations, source_data_array, target_data_array)
                    
                    return bytes(target_data_array)
                    
                except Exception as e2:
                    raise Exception(f"All BPS patching methods failed. Primary error: {e}, Fallback error: {e2}")
            
            finally:
                # Clean up temporary files
                if os.path.exists(temp_source_path):
                    os.remove(temp_source_path)
                if os.path.exists(temp_output_path):
                    os.remove(temp_output_path)
        
        except ImportError:
            raise Exception("BPS library not installed. Install with: pip install python-bps")
        except Exception as e:
            raise Exception(f"BPS patching failed: {e}")

def detect_and_remove_header(source_data: bytes, filename: str, log=None) -> Tuple[bytes, str]:
    """
    Detect and remove headers from ROM files.
    
    Args:
        source_data: Raw ROM file data
        filename: Original filename for context
        log: Logging function
        
    Returns:
        Tuple of (processed_data, header_info_message)
    """
    original_size = len(source_data)
    file_ext = filename.lower().split('.')[-1]
    
    if log:
        log(f"[DEBUG] File extension: {file_ext}", level="Debug")
        log(f"[DEBUG] Original file size: {original_size:,} bytes", level="Debug")
    
    # Common ROM sizes without headers (256KB to 8MB)
    valid_sizes = [262144, 524288, 1048576, 2097152, 4194304, 8388608]
    
    # Check if file is already headerless
    if original_size in valid_sizes:
        if log:
            log(f"[DEBUG] File appears to be headerless (standard ROM size)", level="Debug")
        return source_data, "No header detected"
    
    # Check for 512-byte header (SMC/SFC - most common)
    if original_size - 512 in valid_sizes:
        if log:
            log(f"[DEBUG] Detected 512-byte header (SMC/SFC), removing it...", level="Debug")
        return source_data[512:], f"Removed 512-byte header from {file_ext.upper()} file"
    
    # Check for 200-byte header (less common)
    if original_size - 200 in valid_sizes:
        if log:
            log(f"[DEBUG] Detected 200-byte header, removing it...", level="Debug")
        return source_data[200:], "Removed 200-byte header"
    
    # Check for other common header sizes
    for header_size in [1024, 16]:  # Other known header sizes
        if (original_size - header_size) in valid_sizes:
            if log:
                log(f"[DEBUG] Detected {header_size}-byte header, removing it...", level="Debug")
            return source_data[header_size:], f"Removed {header_size}-byte header"
    
    # If no standard size found, assume headerless
    if log:
        log(f"[DEBUG] WARNING: Non-standard ROM size, assuming headerless", level="Debug")
    return source_data, "Assumed headerless (non-standard size)"
