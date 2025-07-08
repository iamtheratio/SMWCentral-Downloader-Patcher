import unittest
import io
import os
import time
from unittest.mock import patch, mock_open

def detect_and_remove_header(source_data, filename):
    """
    Detect and remove headers from ROM files
    Returns: (processed_data, header_info)
    """
    original_size = len(source_data)
    file_ext = filename.lower().split('.')[-1]
    
    print(f"File extension: {file_ext}")
    print(f"Original file size: {original_size} bytes")
    
    # Common ROM sizes without headers
    valid_sizes = [262144, 524288, 1048576, 2097152, 4194304, 8388608]  # 256KB to 8MB
    
    # Check if file is already headerless
    if original_size in valid_sizes:
        print("File appears to be headerless (standard ROM size)")
        return source_data, "No header detected"
    
    # Check for 512-byte header (SMC/SFC)
    if original_size - 512 in valid_sizes:
        print("Detected 512-byte header (SMC/SFC), removing it...")
        return source_data[512:], f"Removed 512-byte header from {file_ext.upper()} file"
    
    # Check for 200-byte header (less common)
    if original_size - 200 in valid_sizes:
        print("Detected 200-byte header, removing it...")
        return source_data[200:], "Removed 200-byte header"
    
    # Check for other common header sizes
    for header_size in [512, 200, 1024]:
        if (original_size - header_size) in valid_sizes:
            print(f"Detected {header_size}-byte header, removing it...")
            return source_data[header_size:], f"Removed {header_size}-byte header"
    
    # If no standard size found, assume headerless
    print("WARNING: Non-standard ROM size, assuming headerless")
    return source_data, "Assumed headerless (non-standard size)"

def test_bps_patching():
    print("=== Function started ===")
    
    # Configure these paths for your specific files - using raw strings
    sourcefile = r"C:\Users\georg\Desktop\SMWCentralDownloader\clean.sfc"  # Original ROM file
    patchfile = r"C:\Users\georg\Desktop\SMWCentralDownloader\SuperRatioWorld.bps"   # BPS patch file
    outputfile = r"C:\Users\georg\Desktop\SMWCentralDownloader\SuperRatioWorld Patched.sfc" # Patched ROM output

    print("=== BPS Patching Test ===")
    print(f"Looking for source file: {sourcefile}")
    print(f"Source file exists: {os.path.exists(sourcefile)}")
    
    print(f"Looking for patch file: {patchfile}")
    print(f"Patch file exists: {os.path.exists(patchfile)}")
    
    # Workaround for the time.clock issue
    if not hasattr(time, 'clock'):
        time.clock = time.perf_counter
        print("Applied time.clock compatibility fix")
    
    # Now try to import the BPS apply module
    try:
        from bps import apply
        print("Successfully imported bps.apply module")
        print(f"Available functions in apply: {[attr for attr in dir(apply) if not attr.startswith('_')]}")
        
        # Check if files exist before proceeding
        if not os.path.exists(sourcefile):
            print(f"\nERROR: Source file not found: {sourcefile}")
            return
        
        if not os.path.exists(patchfile):
            print(f"\nERROR: Patch file not found: {patchfile}")
            return
        
        # Create output directory if it doesn't exist
        output_dir = os.path.dirname(outputfile)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            print(f"Created output directory: {output_dir}")

        print("\n=== Starting patching process ===")
        
        # Read the source file and detect header
        with open(sourcefile, 'rb') as f:
            source_data = f.read()
        
        # Detect and remove header
        processed_data, header_info = detect_and_remove_header(source_data, sourcefile)
        print(f"Header processing: {header_info}")
        print(f"Final ROM size: {len(processed_data)} bytes")
        
        # Method 1: Try apply_to_files with processed ROM
        try:
            print("Trying apply_to_files with processed ROM...")
            
            # Create temporary file with processed data
            temp_source = sourcefile + ".temp"
            with open(temp_source, 'wb') as f:
                f.write(processed_data)
            
            with open(patchfile, 'rb') as patch_file, \
                 open(temp_source, 'rb') as source_file, \
                 open(outputfile, 'wb') as target_file:
                
                apply.apply_to_files(patch_file, source_file, target_file)
                print("Successfully patched using apply_to_files!")
            
            # Clean up temp file
            os.remove(temp_source)
            
        except Exception as e1:
            print(f"apply_to_files failed: {e1}")
            
            # Method 2: Try apply_to_bytearrays with proper generator
            try:
                print("Trying apply_to_bytearrays with proper generator...")
                
                # Read patch file and get operations
                with open(patchfile, 'rb') as f:
                    patch_file_obj = io.BytesIO(f.read())
                
                # Get patch operations using read_bps
                patch_operations = apply.read_bps(patch_file_obj)
                
                # Convert source data to bytearray
                source_data_array = bytearray(processed_data)
                target_data_array = bytearray()
                
                # Apply patch with generator
                apply.apply_to_bytearrays(patch_operations, source_data_array, target_data_array)
                print(f"Successfully patched using apply_to_bytearrays! Output: {len(target_data_array)} bytes")
                
                # Write the patched data to output file
                with open(outputfile, 'wb') as f:
                    f.write(target_data_array)
                print(f"Output written to {outputfile}")
                
            except Exception as e2:
                print(f"apply_to_bytearrays failed: {e2}")
                print("All methods failed")
                import traceback
                traceback.print_exc()
                return
        
        # Check if output file was created
        if os.path.exists(outputfile):
            output_size = os.path.getsize(outputfile)
            print(f"Final output file: {outputfile} ({output_size} bytes)")
        else:
            print("Warning: Output file not found after patching")
            return
        
        print(f"Successfully patched {sourcefile} with {patchfile}")
        
    except Exception as e:
        print(f"Error during patching: {e}")
        import traceback
        traceback.print_exc()
    
    print("=== Function completed ===")

# Make sure the function is called
print("Starting test...")
test_bps_patching()
print("Test finished.")