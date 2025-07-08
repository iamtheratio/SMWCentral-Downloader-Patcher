"""
BPS Patching functionality for SMWCentral Downloader & Patcher
"""
import io
import os
import time
from typing import Tuple, Optional

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

def patch_bps(source_file: str, patch_file: str, output_file: str, log=None) -> bool:
    """
    Apply a BPS patch to a ROM file.
    
    Args:
        source_file: Path to the source ROM file
        patch_file: Path to the BPS patch file
        output_file: Path where the patched ROM will be saved
        log: Logging function
        
    Returns:
        True if patching was successful, False otherwise
        
    Raises:
        FileNotFoundError: If source or patch file doesn't exist
        Exception: If patching fails
    """
    # Validate input files
    if not os.path.exists(source_file):
        raise FileNotFoundError(f"Source file not found: {source_file}")
    
    if not os.path.exists(patch_file):
        raise FileNotFoundError(f"Patch file not found: {patch_file}")
    
    # Create output directory if needed
    output_dir = os.path.dirname(output_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
        if log:
            log(f"[DEBUG] Created output directory: {output_dir}", level="Debug")
    
    # Compatibility fix for Python 3.8+ where time.clock was removed
    if not hasattr(time, 'clock'):
        time.clock = time.perf_counter
        if log:
            log(f"[DEBUG] Applied time.clock compatibility fix", level="Debug")
    
    try:
        # Import BPS module
        from bps import apply
        if log:
            log(f"[DEBUG] Successfully imported bps.apply module", level="Debug")
        
        # Read and process source file
        with open(source_file, 'rb') as f:
            source_data = f.read()
        
        # Remove header if present
        processed_data, header_info = detect_and_remove_header(source_data, source_file, log)
        if log:
            log(f"[DEBUG] Header processing: {header_info}", level="Debug")
            log(f"[DEBUG] Final ROM size: {len(processed_data):,} bytes", level="Debug")
        
        # Apply patch using temporary file approach (most reliable)
        temp_source = source_file + ".temp"
        try:
            # Create temporary headerless file
            with open(temp_source, 'wb') as f:
                f.write(processed_data)
            
            # Apply patch
            with open(patch_file, 'rb') as patch_f, \
                 open(temp_source, 'rb') as source_f, \
                 open(output_file, 'wb') as target_f:
                
                apply.apply_to_files(patch_f, source_f, target_f)
            
            if log:
                log(f"[DEBUG] Successfully patched using apply_to_files", level="Debug")
            return True
            
        except Exception as e:
            if log:
                log(f"[DEBUG] apply_to_files failed: {e}, trying fallback method", level="Debug")
            
            # Fallback to bytearrays method
            try:
                with open(patch_file, 'rb') as f:
                    patch_file_obj = io.BytesIO(f.read())
                
                patch_operations = apply.read_bps(patch_file_obj)
                source_data_array = bytearray(processed_data)
                target_data_array = bytearray()
                
                apply.apply_to_bytearrays(patch_operations, source_data_array, target_data_array)
                
                with open(output_file, 'wb') as f:
                    f.write(target_data_array)
                
                if log:
                    log(f"[DEBUG] Successfully patched using apply_to_bytearrays fallback", level="Debug")
                return True
                
            except Exception as e2:
                raise Exception(f"All patching methods failed. Primary error: {e}, Fallback error: {e2}")
        
        finally:
            # Clean up temporary file
            if os.path.exists(temp_source):
                os.remove(temp_source)
                if log:
                    log(f"[DEBUG] Cleaned up temporary file", level="Debug")
    
    except ImportError:
        raise Exception("BPS library not installed. Install with: pip install python-bps")
    except Exception as e:
        raise Exception(f"BPS patching failed: {e}")

def patch_bps_safe(source_file: str, patch_file: str, output_file: str, 
                   log=None, verbose: bool = False) -> Tuple[bool, str]:
    """
    Safe wrapper for patch_bps that handles all exceptions.
    
    Args:
        source_file: Path to the source ROM file
        patch_file: Path to the BPS patch file  
        output_file: Path where the patched ROM will be saved
        log: Logging function
        verbose: Whether to return detailed error messages
        
    Returns:
        Tuple of (success: bool, message: str)
    """
    try:
        success = patch_bps(source_file, patch_file, output_file, log)
        if success:
            output_size = os.path.getsize(output_file) if os.path.exists(output_file) else 0
            return True, f"Successfully patched ROM ({output_size:,} bytes)"
        else:
            return False, "BPS patching failed for unknown reason"
            
    except FileNotFoundError as e:
        return False, str(e)
    except Exception as e:
        error_msg = str(e) if verbose else "BPS patching failed"
        return False, error_msg