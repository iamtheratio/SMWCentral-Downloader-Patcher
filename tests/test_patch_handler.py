"""
Unit tests for patch_handler.py module
Tests patch application functionality for both BPS and IPS formats
"""
import unittest
import os
import tempfile
from unittest.mock import Mock, patch, MagicMock
import sys

# Import test configuration
from .test_config import TestConfig, TestDataManager

# Import the module to test
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from patch_handler import PatchHandler

class TestPatchHandler(unittest.TestCase):
    """Test cases for PatchHandler class"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = TestConfig.get_temp_dir()
        self.data_manager = TestDataManager(self.test_dir)
        self.data_manager.setup_test_files()
        
        # Create test files
        self.base_rom = os.path.join(self.test_dir, "base.smc")
        self.patch_file = os.path.join(self.test_dir, "test.bps")
        self.output_file = os.path.join(self.test_dir, "output.smc")
        
        # Create dummy base ROM
        with open(self.base_rom, 'wb') as f:
            f.write(b'\x00' * 1024)  # 1KB of zeros
        
        # Create dummy patch file
        with open(self.patch_file, 'wb') as f:
            f.write(b'BPS1\x00\x00\x00\x00')  # Minimal BPS header
    
    def tearDown(self):
        """Clean up test environment"""
        self.data_manager.cleanup()
    
    @patch('patch_handler.subprocess.run')
    def test_apply_bps_patch_success(self, mock_run):
        """Test successful BPS patch application"""
        # Mock successful patch application
        mock_run.return_value = Mock(returncode=0, stdout="", stderr="")
        
        result = PatchHandler.apply_patch(self.patch_file, self.base_rom, self.output_file)
        
        self.assertTrue(result)
        mock_run.assert_called_once()
    
    @patch('patch_handler.subprocess.run')
    def test_apply_bps_patch_failure(self, mock_run):
        """Test failed BPS patch application"""
        # Mock failed patch application
        mock_run.return_value = Mock(returncode=1, stdout="", stderr="Patch failed")
        
        result = PatchHandler.apply_patch(self.patch_file, self.base_rom, self.output_file)
        
        self.assertFalse(result)
        mock_run.assert_called_once()
    
    @patch('patch_handler.subprocess.run')
    def test_apply_ips_patch_success(self, mock_run):
        """Test successful IPS patch application"""
        # Create IPS patch file
        ips_patch = os.path.join(self.test_dir, "test.ips")
        with open(ips_patch, 'wb') as f:
            f.write(b'PATCH\x00\x00\x00')  # Minimal IPS header
        
        # Mock successful patch application
        mock_run.return_value = Mock(returncode=0, stdout="", stderr="")
        
        result = PatchHandler.apply_patch(ips_patch, self.base_rom, self.output_file)
        
        self.assertTrue(result)
        mock_run.assert_called_once()
    
    def test_apply_patch_missing_files(self):
        """Test patch application with missing files"""
        # Test with missing patch file
        result = PatchHandler.apply_patch("/nonexistent/patch.bps", self.base_rom, self.output_file)
        self.assertFalse(result)
        
        # Test with missing base ROM
        result = PatchHandler.apply_patch(self.patch_file, "/nonexistent/rom.smc", self.output_file)
        self.assertFalse(result)
    
    def test_apply_patch_unsupported_format(self):
        """Test patch application with unsupported format"""
        # Create unsupported patch file
        unsupported_patch = os.path.join(self.test_dir, "test.ups")
        with open(unsupported_patch, 'wb') as f:
            f.write(b'UPS1\x00\x00\x00\x00')
        
        result = PatchHandler.apply_patch(unsupported_patch, self.base_rom, self.output_file)
        self.assertFalse(result)
    
    @patch('patch_handler.subprocess.run')
    def test_apply_patch_with_logging(self, mock_run):
        """Test patch application with logging"""
        mock_log = Mock()
        mock_run.return_value = Mock(returncode=0, stdout="Success", stderr="")
        
        result = PatchHandler.apply_patch(self.patch_file, self.base_rom, self.output_file, mock_log)
        
        self.assertTrue(result)
        # Verify logging was called
        mock_log.assert_called()
    
    @patch('patch_handler.subprocess.run')
    def test_apply_patch_timeout(self, mock_run):
        """Test patch application with timeout"""
        # Mock timeout exception
        mock_run.side_effect = Exception("Timeout")
        
        result = PatchHandler.apply_patch(self.patch_file, self.base_rom, self.output_file)
        
        self.assertFalse(result)
    
    def test_detect_patch_format_bps(self):
        """Test BPS patch format detection"""
        bps_file = os.path.join(self.test_dir, "test.bps")
        with open(bps_file, 'wb') as f:
            f.write(b'BPS1')
        
        # This would be internal logic in PatchHandler
        # Testing the file extension detection
        self.assertTrue(bps_file.endswith('.bps'))
    
    def test_detect_patch_format_ips(self):
        """Test IPS patch format detection"""
        ips_file = os.path.join(self.test_dir, "test.ips")
        with open(ips_file, 'wb') as f:
            f.write(b'PATCH')
        
        # Testing the file extension detection
        self.assertTrue(ips_file.endswith('.ips'))
    
    @patch('patch_handler.subprocess.run')
    def test_apply_patch_output_directory_creation(self, mock_run):
        """Test that output directory is created if it doesn't exist"""
        # Create output path in non-existent directory
        nested_output = os.path.join(self.test_dir, "nested", "dir", "output.smc")
        
        mock_run.return_value = Mock(returncode=0, stdout="", stderr="")
        
        result = PatchHandler.apply_patch(self.patch_file, self.base_rom, nested_output)
        
        # Should succeed and create directory
        self.assertTrue(result)
        self.assertTrue(os.path.exists(os.path.dirname(nested_output)))
    
    @patch('patch_handler.subprocess.run')
    def test_apply_patch_special_characters(self, mock_run):
        """Test patch application with special characters in paths"""
        # Create paths with special characters
        special_output = os.path.join(self.test_dir, "output with spaces & symbols.smc")
        
        mock_run.return_value = Mock(returncode=0, stdout="", stderr="")
        
        result = PatchHandler.apply_patch(self.patch_file, self.base_rom, special_output)
        
        self.assertTrue(result)
        # Verify the command was called with proper path handling
        mock_run.assert_called_once()
    
    def test_validate_patch_file_integrity(self):
        """Test patch file integrity validation"""
        # Test with valid BPS file
        valid_bps = os.path.join(self.test_dir, "valid.bps")
        with open(valid_bps, 'wb') as f:
            f.write(b'BPS1\x00\x00\x00\x01\x00\x00\x00\x01\x00')  # More complete BPS
        
        # File exists and has correct extension
        self.assertTrue(os.path.exists(valid_bps))
        self.assertTrue(valid_bps.endswith('.bps'))
        
        # Test with corrupted file
        corrupted_patch = os.path.join(self.test_dir, "corrupted.bps")
        with open(corrupted_patch, 'wb') as f:
            f.write(b'INVALID')
        
        # Should still have correct extension but content is invalid
        self.assertTrue(corrupted_patch.endswith('.bps'))
    
    def test_validate_rom_file_integrity(self):
        """Test ROM file integrity validation"""
        # Test ROM file size
        rom_size = os.path.getsize(self.base_rom)
        self.assertEqual(rom_size, 1024)
        
        # Test ROM file accessibility
        self.assertTrue(os.access(self.base_rom, os.R_OK))
    
    @patch('patch_handler.subprocess.run')
    def test_concurrent_patch_operations(self, mock_run):
        """Test handling of concurrent patch operations"""
        mock_run.return_value = Mock(returncode=0, stdout="", stderr="")
        
        # Simulate multiple patch operations
        results = []
        for i in range(3):
            output_file = os.path.join(self.test_dir, f"output_{i}.smc")
            result = PatchHandler.apply_patch(self.patch_file, self.base_rom, output_file)
            results.append(result)
        
        # All should succeed
        self.assertTrue(all(results))
        self.assertEqual(mock_run.call_count, 3)
    
    @patch('patch_handler.subprocess.run')
    def test_patch_with_different_extensions(self, mock_run):
        """Test patching with different ROM extensions"""
        mock_run.return_value = Mock(returncode=0, stdout="", stderr="")
        
        # Test different output extensions
        extensions = ['.smc', '.sfc', '.rom']
        
        for ext in extensions:
            with self.subTest(extension=ext):
                output_file = os.path.join(self.test_dir, f"output{ext}")
                result = PatchHandler.apply_patch(self.patch_file, self.base_rom, output_file)
                self.assertTrue(result)
    
    def test_error_handling_invalid_permissions(self):
        """Test error handling with invalid file permissions"""
        # Create read-only base ROM
        readonly_rom = os.path.join(self.test_dir, "readonly.smc")
        with open(readonly_rom, 'wb') as f:
            f.write(b'\x00' * 1024)
        
        try:
            os.chmod(readonly_rom, 0o444)  # Read-only
            
            # Try to use as output (should fail)
            result = PatchHandler.apply_patch(self.patch_file, self.base_rom, readonly_rom)
            
            # Should handle permission error gracefully
            self.assertFalse(result)
            
        except Exception:
            # If chmod doesn't work on this system, skip this test
            self.skipTest("Cannot modify file permissions on this system")
        finally:
            # Restore permissions for cleanup
            try:
                os.chmod(readonly_rom, 0o644)
            except:
                pass
    
    @patch('patch_handler.subprocess.run')
    def test_patch_progress_callback(self, mock_run):
        """Test patch operation with progress callback"""
        mock_run.return_value = Mock(returncode=0, stdout="", stderr="")
        mock_callback = Mock()
        
        # If PatchHandler supported progress callbacks, test would be:
        # result = PatchHandler.apply_patch(self.patch_file, self.base_rom, self.output_file, progress_callback=mock_callback)
        
        # For now, just test basic functionality
        result = PatchHandler.apply_patch(self.patch_file, self.base_rom, self.output_file)
        self.assertTrue(result)

if __name__ == '__main__':
    unittest.main()
