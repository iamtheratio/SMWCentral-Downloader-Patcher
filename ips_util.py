class Patch:
    def __init__(self, patch_data):
        self.patch_data = patch_data
        self.records = []
        self._parse_patch()
    
    @classmethod
    def load(cls, filepath):
        """Load an IPS patch from file"""
        with open(filepath, 'rb') as f:
            return cls(f.read())
    
    def _parse_patch(self):
        """Parse the IPS patch data"""
        if not self.patch_data.startswith(b'PATCH'):
            raise ValueError("Invalid IPS file - no PATCH header")
        
        offset = 5  # Skip "PATCH"
        
        while offset < len(self.patch_data):
            # Check for EOF marker
            if self.patch_data[offset:offset+3] == b'EOF':
                break
            
            if offset + 5 > len(self.patch_data):
                break
            
            # Get address (3 bytes, big endian)
            address = (self.patch_data[offset] << 16) | (self.patch_data[offset+1] << 8) | self.patch_data[offset+2]
            offset += 3
            
            # Get length (2 bytes, big endian)
            length = (self.patch_data[offset] << 8) | self.patch_data[offset+1]
            offset += 2
            
            if length == 0:
                # RLE record
                if offset + 3 > len(self.patch_data):
                    break
                
                rle_length = (self.patch_data[offset] << 8) | self.patch_data[offset+1]
                rle_value = self.patch_data[offset+2]
                offset += 3
                
                self.records.append({
                    'type': 'rle',
                    'address': address,
                    'length': rle_length,
                    'value': rle_value
                })
            else:
                # Normal record
                if offset + length > len(self.patch_data):
                    break
                
                data = self.patch_data[offset:offset+length]
                offset += length
                
                self.records.append({
                    'type': 'normal',
                    'address': address,
                    'length': length,
                    'data': data
                })
    
    def apply(self, source_data):
        """Apply the patch to source data and return patched data"""
        # Convert to bytearray for modification
        result = bytearray(source_data)
        
        # Remove header if present
        if len(result) == 524800:  # 512KB header + 512KB ROM
            result = result[512:]
        
        # Find maximum address needed
        max_address = len(result)
        for record in self.records:
            if record['type'] == 'rle':
                max_address = max(max_address, record['address'] + record['length'])
            else:
                max_address = max(max_address, record['address'] + record['length'])
        
        # Expand ROM if needed
        if max_address > len(result):
            result.extend(bytearray(max_address - len(result)))
        
        # Apply patches
        for record in self.records:
            if record['type'] == 'rle':
                # RLE record
                for i in range(record['length']):
                    result[record['address'] + i] = record['value']
            else:
                # Normal record
                result[record['address']:record['address'] + record['length']] = record['data']
        
        # Fix SNES checksum
        self._fix_checksum(result)
        
        return bytes(result)
    
    def _fix_checksum(self, rom_data):
        """Fix the SNES ROM internal checksum"""
        checksum_offset = 0x7FDC
        
        if len(rom_data) <= checksum_offset + 3:
            return
        
        # Calculate checksum of entire ROM
        checksum = 0
        for i, byte in enumerate(rom_data):
            if i < checksum_offset or i > checksum_offset + 3:  # Skip checksum area
                checksum += byte
        
        # Handle overflow
        checksum = checksum & 0xFFFF
        complement = checksum ^ 0xFFFF
        
        # Write new checksums (little endian)
        rom_data[checksum_offset] = complement & 0xFF
        rom_data[checksum_offset + 1] = (complement >> 8) & 0xFF
        rom_data[checksum_offset + 2] = checksum & 0xFF
        rom_data[checksum_offset + 3] = (checksum >> 8) & 0xFF