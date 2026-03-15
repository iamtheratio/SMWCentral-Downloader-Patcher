"""
Patch Handler
Handles IPS and BPS patch application for ROM hacks

Copyright (c) 2025 iamtheratio
Licensed under the MIT License - see LICENSE file for details
"""

import os
import glob
from pathlib import Path
from patcher_ips import Patch as IPSPatch
from patcher_bps import Patch as BPSPatch

class PatchHandler:
    @staticmethod
    def find_patches(directory):
        """Find all patch files in directory"""
        patches = []
        
        # Find IPS files
        ips_files = glob.glob(os.path.join(directory, "*.ips"))
        for ips_file in ips_files:
            patches.append({
                'type': 'ips',
                'path': ips_file,
                'name': os.path.basename(ips_file)
            })
        
        # Find BPS files
        bps_files = glob.glob(os.path.join(directory, "*.bps"))
        for bps_file in bps_files:
            patches.append({
                'type': 'bps',
                'path': bps_file,
                'name': os.path.basename(bps_file)
            })
        
        return patches
    
    # Magic bytes for supported patch formats
    _MAGIC = {
        '.bps': b'BPS1',
        '.ips': b'PATCH',
    }

    @staticmethod
    def _validate_magic(patch_path, patch_ext):
        """Return True if the file starts with the expected magic bytes."""
        expected = PatchHandler._MAGIC.get(patch_ext)
        if expected is None:
            return False
        try:
            with open(patch_path, 'rb') as f:
                header = f.read(len(expected))
            return header == expected
        except OSError:
            return False

    @staticmethod
    def apply_patch(patch_path, source_rom_path, output_path, log=None):
        """Apply a patch (IPS or BPS) to a ROM"""
        patch_ext = Path(patch_path).suffix.lower()

        # Reject files that don't carry the correct magic bytes — this blocks
        # executables or other non-patch files masquerading as .bps/.ips.
        if not PatchHandler._validate_magic(patch_path, patch_ext):
            if log:
                log(f"❌ Rejected '{os.path.basename(patch_path)}': invalid {patch_ext.upper()} header (not a real patch file)", "Error")
            return False

        if log:
            log(f"🔧 Applying {patch_ext.upper()} patch: {os.path.basename(patch_path)}", "applying")

        try:
            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            if patch_ext == '.ips':
                # Apply IPS patch
                patch = IPSPatch.load(patch_path)
                
                with open(source_rom_path, 'rb') as f_in:
                    with open(output_path, 'wb') as f_out:
                        patched_data = patch.apply(f_in.read())
                        f_out.write(patched_data)
                
                # No success message for IPS - let api_pipeline handle it
                
            elif patch_ext == '.bps':
                # Apply BPS patch
                patch = BPSPatch.load(patch_path)
                
                with open(source_rom_path, 'rb') as f_in:
                    with open(output_path, 'wb') as f_out:
                        patched_data = patch.apply(f_in.read())
                        f_out.write(patched_data)
                
                # No success message for BPS - let api_pipeline handle it
                
            else:
                raise ValueError(f"Unsupported patch format: {patch_ext}")
            
            return True
            
        except Exception as e:
            if log:
                log(f"❌ Error applying {patch_ext.upper()} patch: {str(e)}", "Error")
            return False
    
    @staticmethod
    def auto_patch(download_directory, source_rom_path, output_directory=None, log=None):
        """Automatically detect and apply patches in download directory"""
        if output_directory is None:
            output_directory = download_directory
        
        patches = PatchHandler.find_patches(download_directory)
        
        if not patches:
            if log:
                log("❌ No patches found in download directory", "Error")
            return False
        
        if len(patches) > 1:
            if log:
                log(f"⚠️  Multiple patches found: {[p['name'] for p in patches]}")
                log("Using first patch found")
        
        patch_info = patches[0]
        patch_path = patch_info['path']
        patch_name = Path(patch_info['name']).stem
        
        # Create output filename
        output_filename = f"{patch_name}_patched.smc"
        output_path = os.path.join(output_directory, output_filename)
        
        if log:
            log(f"🎯 Auto-patching with: {patch_info['name']}")
        
        success = PatchHandler.apply_patch(patch_path, source_rom_path, output_path, log)
        
        if success:
            if log:
                log(f"✅ Patched ROM saved to: {output_path}")
            return output_path
        else:
            return False
