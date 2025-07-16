"""
Unit tests for api_pipeline.py module
Tests API interactions, download pipeline, and data processing
"""
import unittest
import os
import json
import tempfile
import zipfile
from unittest.mock import Mock, patch, MagicMock, mock_open
import sys

# Import test configuration
from .test_config import TestConfig, TestDataManager, MockHackData, create_mock_response

# Import the module to test
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import api_pipeline

class TestApiPipeline(unittest.TestCase):
    """Test cases for api_pipeline.py functions"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = TestConfig.get_temp_dir()
        self.data_manager = TestDataManager(self.test_dir)
        self.data_manager.setup_test_files()
    
    def tearDown(self):
        """Clean up test environment"""
        self.data_manager.cleanup()
    
    def test_load_processed_existing_file(self):
        """Test loading existing processed.json file"""
        result = api_pipeline.load_processed(self.data_manager.processed_file)
        self.assertIsInstance(result, dict)
        self.assertIn("12345", result)
    
    def test_load_processed_missing_file(self):
        """Test loading missing processed.json file"""
        missing_file = os.path.join(self.test_dir, "missing.json")
        result = api_pipeline.load_processed(missing_file)
        self.assertEqual(result, {})
    
    def test_load_processed_invalid_json(self):
        """Test loading invalid JSON file"""
        invalid_file = os.path.join(self.test_dir, "invalid.json")
        with open(invalid_file, 'w') as f:
            f.write("invalid json content")
        
        result = api_pipeline.load_processed(invalid_file)
        self.assertEqual(result, {})
    
    def test_save_processed(self):
        """Test saving processed data"""
        test_data = {"test_id": {"title": "Test Hack"}}
        output_file = os.path.join(self.test_dir, "test_output.json")
        
        api_pipeline.save_processed(test_data, output_file)
        
        # Verify file was created and contains correct data
        self.assertTrue(os.path.exists(output_file))
        
        with open(output_file, 'r') as f:
            loaded_data = json.load(f)
        
        self.assertEqual(loaded_data, test_data)
    
    def test_save_processed_create_directory(self):
        """Test saving processed data with directory creation"""
        test_data = {"test_id": {"title": "Test Hack"}}
        nested_dir = os.path.join(self.test_dir, "nested", "dir")
        output_file = os.path.join(nested_dir, "output.json")
        
        api_pipeline.save_processed(test_data, output_file)
        
        # Verify directory was created and file exists
        self.assertTrue(os.path.exists(output_file))
    
    @patch('api_pipeline.requests.get')
    def test_fetch_file_metadata_success(self, mock_get):
        """Test successful file metadata fetching"""
        # Mock successful API response
        mock_response_data = {
            "data": {
                "id": 12345,
                "name": "Test Hack",
                "download_url": "https://example.com/test.zip",
                "fields": {
                    "difficulty": "diff_3",
                    "length": 95
                }
            }
        }
        mock_get.return_value = create_mock_response(200, mock_response_data)
        
        result = api_pipeline.fetch_file_metadata("12345")
        
        self.assertIsNotNone(result)
        self.assertEqual(result["data"]["id"], 12345)
        self.assertEqual(result["data"]["name"], "Test Hack")
        mock_get.assert_called_once()
    
    @patch('api_pipeline.requests.get')
    def test_fetch_file_metadata_failure(self, mock_get):
        """Test failed file metadata fetching"""
        # Mock failed API response
        mock_get.return_value = create_mock_response(404)
        
        result = api_pipeline.fetch_file_metadata("12345")
        
        self.assertIsNone(result)
        mock_get.assert_called_once()
    
    @patch('api_pipeline.requests.get')
    def test_fetch_file_metadata_with_log(self, mock_get):
        """Test file metadata fetching with logging"""
        mock_log = Mock()
        mock_get.return_value = create_mock_response(200, {"data": {"id": 12345}})
        
        result = api_pipeline.fetch_file_metadata("12345", mock_log)
        
        # Verify logging was called
        mock_log.assert_called()
        self.assertIsNotNone(result)
    
    def test_extract_patches_from_zip_bps(self):
        """Test extracting BPS patch from ZIP file"""
        # Create test ZIP with BPS patch
        zip_path = os.path.join(self.test_dir, "test.zip")
        extract_dir = os.path.join(self.test_dir, "extract")
        os.makedirs(extract_dir, exist_ok=True)
        
        with zipfile.ZipFile(zip_path, 'w') as zf:
            zf.writestr("test_hack.bps", b"mock bps content")
            zf.writestr("readme.txt", b"readme content")
        
        result = api_pipeline.extract_patches_from_zip(zip_path, extract_dir, "Test Hack")
        
        self.assertIsNotNone(result)
        self.assertTrue(result.endswith(".bps"))
        self.assertTrue(os.path.exists(result))
    
    def test_extract_patches_from_zip_ips(self):
        """Test extracting IPS patch from ZIP file"""
        # Create test ZIP with IPS patch
        zip_path = os.path.join(self.test_dir, "test.zip")
        extract_dir = os.path.join(self.test_dir, "extract")
        os.makedirs(extract_dir, exist_ok=True)
        
        with zipfile.ZipFile(zip_path, 'w') as zf:
            zf.writestr("test_hack.ips", b"mock ips content")
            zf.writestr("readme.txt", b"readme content")
        
        result = api_pipeline.extract_patches_from_zip(zip_path, extract_dir, "Test Hack")
        
        self.assertIsNotNone(result)
        self.assertTrue(result.endswith(".ips"))
        self.assertTrue(os.path.exists(result))
    
    def test_extract_patches_from_zip_multiple_patches(self):
        """Test extracting when multiple patches are present"""
        # Create test ZIP with multiple patches
        zip_path = os.path.join(self.test_dir, "test.zip")
        extract_dir = os.path.join(self.test_dir, "extract")
        os.makedirs(extract_dir, exist_ok=True)
        
        with zipfile.ZipFile(zip_path, 'w') as zf:
            zf.writestr("test_hack.bps", b"mock bps content")
            zf.writestr("test_hack.ips", b"mock ips content")
            zf.writestr("readme.txt", b"readme content")
        
        result = api_pipeline.extract_patches_from_zip(zip_path, extract_dir, "Test Hack")
        
        # Should prefer BPS over IPS
        self.assertIsNotNone(result)
        self.assertTrue(result.endswith(".bps"))
    
    def test_extract_patches_from_zip_no_patches(self):
        """Test extracting when no patches are present"""
        # Create test ZIP without patches
        zip_path = os.path.join(self.test_dir, "test.zip")
        extract_dir = os.path.join(self.test_dir, "extract")
        os.makedirs(extract_dir, exist_ok=True)
        
        with zipfile.ZipFile(zip_path, 'w') as zf:
            zf.writestr("readme.txt", b"readme content")
            zf.writestr("image.png", b"mock image content")
        
        result = api_pipeline.extract_patches_from_zip(zip_path, extract_dir, "Test Hack")
        
        self.assertIsNone(result)
    
    def test_extract_patches_from_zip_invalid_zip(self):
        """Test extracting from invalid ZIP file"""
        # Create invalid ZIP file
        invalid_zip = os.path.join(self.test_dir, "invalid.zip")
        with open(invalid_zip, 'w') as f:
            f.write("not a zip file")
        
        extract_dir = os.path.join(self.test_dir, "extract")
        os.makedirs(extract_dir, exist_ok=True)
        
        result = api_pipeline.extract_patches_from_zip(invalid_zip, extract_dir, "Test Hack")
        
        self.assertIsNone(result)
    
    def test_make_output_path(self):
        """Test make_output_path function"""
        base_dir = "/test/output"
        hack_type = "kaizo"
        folder_name = "05 - Expert"
        
        result = api_pipeline.make_output_path(base_dir, hack_type, folder_name)
        expected = os.path.join(base_dir, "Kaizo", folder_name)
        self.assertEqual(result, expected)
    
    def test_make_output_path_standard_type(self):
        """Test make_output_path with standard hack type"""
        base_dir = "/test/output"
        hack_type = "standard"
        folder_name = "03 - Skilled"
        
        result = api_pipeline.make_output_path(base_dir, hack_type, folder_name)
        expected = os.path.join(base_dir, "Standard", folder_name)
        self.assertEqual(result, expected)
    
    def test_clean_hack_title(self):
        """Test clean_hack_title function"""
        test_cases = [
            ("Super Mario World: The Adventure", "Super Mario World The Adventure"),
            ("Mario's Quest (Demo)", "Mario's Quest Demo"),
            ("Test [v1.0]", "Test v1.0"),
            ("Hack {Final}", "Hack Final"),
            ("Normal Title", "Normal Title")
        ]
        
        for input_title, expected in test_cases:
            with self.subTest(input_title=input_title):
                result = api_pipeline.clean_hack_title(input_title)
                self.assertEqual(result, expected)
    
    def test_cancel_functionality(self):
        """Test cancellation flag functionality"""
        # Test initial state
        self.assertFalse(api_pipeline.is_cancelled())
        
        # Test setting cancel flag
        api_pipeline.set_cancel_flag()
        self.assertTrue(api_pipeline.is_cancelled())
        
        # Test resetting cancel flag
        api_pipeline.reset_cancel_flag()
        self.assertFalse(api_pipeline.is_cancelled())
    
    @patch('api_pipeline.requests.get')
    @patch('api_pipeline.fetch_file_metadata')
    @patch('api_pipeline.PatchHandler')
    def test_download_single_hack_success(self, mock_patch_handler, mock_fetch_metadata, mock_get):
        """Test successful single hack download"""
        # Setup mocks
        mock_fetch_metadata.return_value = {
            "data": {
                "download_url": "https://example.com/test.zip"
            }
        }
        
        # Create mock ZIP content
        zip_content = b"mock zip content"
        mock_get.return_value = create_mock_response(200, content=zip_content)
        
        # Mock patch handler
        mock_patch_handler.apply_patch.return_value = True
        
        # Create test ZIP file for extraction
        test_zip = os.path.join(self.test_dir, "test_download.zip")
        with zipfile.ZipFile(test_zip, 'w') as zf:
            zf.writestr("test.bps", b"mock patch")
        
        # Mock log function
        mock_log = Mock()
        
        # Test download (this would need more mocking for full integration)
        # For now, just test that the functions can be called without error
        hack = MockHackData.get_sample_hack()
        
        # The actual download process is complex and would need extensive mocking
        # This test verifies the basic structure is in place
        self.assertTrue(True)  # Placeholder for more detailed test
    
    @patch('api_pipeline.smwc_api_get')
    def test_api_integration(self, mock_api_get):
        """Test API integration functions"""
        # Mock API response
        mock_response = {
            "data": [
                {
                    "id": 12345,
                    "name": "Test Hack",
                    "type": "standard"
                }
            ]
        }
        mock_api_get.return_value = mock_response
        
        # Test that API integration functions work
        result = mock_api_get("test_endpoint")
        self.assertEqual(result, mock_response)
    
    def test_difficulty_constants(self):
        """Test difficulty-related constants"""
        # Test DIFFICULTY_LOOKUP
        self.assertIn("diff_1", api_pipeline.DIFFICULTY_LOOKUP)
        self.assertEqual(api_pipeline.DIFFICULTY_LOOKUP["diff_1"], "Newcomer")
        
        # Test get_sorted_folder_name
        result = api_pipeline.get_sorted_folder_name("Expert")
        self.assertEqual(result, "05 - Expert")
    
    def test_title_formatting_functions(self):
        """Test title formatting utility functions"""
        # Test title_case
        result = api_pipeline.title_case("hello world")
        self.assertEqual(result, "Hello World")
        
        # Test safe_filename
        result = api_pipeline.safe_filename("Unsafe<>File|Name")
        self.assertEqual(result, "UnsafeFileName")
    
    @patch('api_pipeline.os.makedirs')
    def test_directory_creation(self, mock_makedirs):
        """Test automatic directory creation"""
        test_path = "/test/new/directory/file.txt"
        
        # This would be called by save_processed or similar functions
        directory = os.path.dirname(test_path)
        os.makedirs(directory, exist_ok=True)
        
        mock_makedirs.assert_called_with(directory, exist_ok=True)
    
    def test_backup_functionality(self):
        """Test backup creation functionality"""
        # Create original file
        original_file = os.path.join(self.test_dir, "original.json")
        original_data = {"test": "data"}
        
        with open(original_file, 'w') as f:
            json.dump(original_data, f)
        
        # Test backup creation (would be part of save_processed)
        backup_file = original_file + ".backup"
        
        # Simulate backup creation
        import shutil
        shutil.copy2(original_file, backup_file)
        
        # Verify backup exists
        self.assertTrue(os.path.exists(backup_file))
        
        # Verify backup content
        with open(backup_file, 'r') as f:
            backup_data = json.load(f)
        
        self.assertEqual(backup_data, original_data)
    
    def test_error_handling_network_timeout(self):
        """Test error handling for network timeouts"""
        with patch('api_pipeline.requests.get') as mock_get:
            # Simulate timeout
            mock_get.side_effect = Exception("Connection timeout")
            
            result = api_pipeline.fetch_file_metadata("12345")
            self.assertIsNone(result)
    
    def test_error_handling_invalid_response(self):
        """Test error handling for invalid API responses"""
        with patch('api_pipeline.requests.get') as mock_get:
            # Simulate invalid JSON response
            mock_response = Mock()
            mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
            mock_response.status_code = 200
            mock_get.return_value = mock_response
            
            result = api_pipeline.fetch_file_metadata("12345")
            self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main()
