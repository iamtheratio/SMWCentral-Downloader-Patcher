import bps
import io

def test_bps_patching():
    # Configure these paths for your specific files
    sourcefile = "C:\\Users\\georg\\Desktop\\SMWCentralDownloader\\clean.smc"  # Original ROM file
    patchfile = "C:\\Users\\georg\\Desktop\\SMWCentralDownloader\\Romhacks\\Kaizo\\02 - Casual\\Oops! All Fortresses.bps"   # BPS patch file
    outputfile = "C:\\Users\\georg\\Desktop\\SMWCentralDownloader\\Romhacks\\Kaizo\\02 - Casual\\Oops! All Fortresses Patched.smc" # Patched ROM output

    try:
        # Read the source file
        with open(sourcefile, 'rb') as f:
            source_data = f.read()
        
        # Read the BPS patch
        with open(patchfile, 'rb') as f:
            patch_data = f.read()
        
        # Create BytesIO objects
        source_io = io.BytesIO(source_data)
        target_io = io.BytesIO()
        
        # Apply the patch
        bps.apply_to_bytesio(io.BytesIO(patch_data), source_io, target_io)
        
        # Write the patched data to output file
        with open(outputfile, 'wb') as f:
            f.write(target_io.getvalue())
        
        print(f"Successfully patched {sourcefile} with {patchfile}")
        print(f"Output written to {outputfile}")
        
    except Exception as e:
        print(f"Error during patching: {e}")

if __name__ == "__main__":
    test_bps_patching()