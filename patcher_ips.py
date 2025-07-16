from ips_util import Patch as IPSUtilPatch

class Patch:
    def __init__(self, patch_data=None):
        if patch_data:
            # Create temporary file for ips_util to load
            import tempfile
            import os
            
            self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.ips')
            self.temp_file.write(patch_data)
            self.temp_file.close()
            
            # Load using ips_util
            self.ips_patch = IPSUtilPatch.load(self.temp_file.name)
        else:
            self.ips_patch = IPSUtilPatch()
            self.temp_file = None
    
    @classmethod
    def load(cls, filepath):
        """Load an IPS patch from file using ips_util"""
        patch = cls()
        patch.ips_patch = IPSUtilPatch.load(filepath)
        return patch
    
    def apply(self, source_data):
        """Apply the patch to source data and return patched data"""
        # DON'T remove header - let ips_util handle it
        # The ips_util library expects the full ROM data including any header
        return self.ips_patch.apply(source_data)
    
    def __del__(self):
        """Clean up temporary file"""
        if hasattr(self, 'temp_file') and self.temp_file:
            import os
            try:
                os.unlink(self.temp_file.name)
            except:
                pass
