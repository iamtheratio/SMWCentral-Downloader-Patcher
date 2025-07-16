"""
Unit tests for utils.py module
Tests core utility functions including file operations, difficulty mappings, and ROM handling
"""
import unittest
import os
import tempfile
import shutil
from unittest.mock import Mock, patch, MagicMock
import sys

# Import test configuration
from .test_config import TestConfig, TestDataManager, MockHackData, run_with_mock_gui

# Import the module to test
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import utils

class TestUtils(unittest.TestCase):
    """Test cases for utils.py functions"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = TestConfig.get_temp_dir()
        self.data_manager = TestDataManager(self.test_dir)
        self.data_manager.setup_test_files()
    
    def tearDown(self):
        """Clean up test environment"""
        self.data_manager.cleanup()
    
    def test_resource_path_normal(self):
        """Test resource_path function with normal path"""
        # Test with a relative path
        result = utils.resource_path("assets/icon.ico")
        self.assertTrue(result.endswith("assets/icon.ico"))
        self.assertTrue(os.path.isabs(result))
    
    @patch('sys._MEIPASS', '/mocked/path')
    def test_resource_path_pyinstaller(self):
        """Test resource_path function in PyInstaller environment"""
        result = utils.resource_path("assets/icon.ico")
        self.assertEqual(result, "/mocked/path/assets/icon.ico")
    
    @run_with_mock_gui
    def test_set_window_icon_success(self):
        """Test set_window_icon with successful icon setting"""
        mock_window = Mock()
        mock_window.iconbitmap = Mock()
        
        utils.set_window_icon(mock_window)
        mock_window.iconbitmap.assert_called_once()
    
    @run_with_mock_gui
    def test_set_window_icon_failure(self):
        """Test set_window_icon with icon loading failure"""
        mock_window = Mock()
        mock_window.iconbitmap = Mock(side_effect=Exception("Icon not found"))
        
        # Should not raise exception
        utils.set_window_icon(mock_window)
        mock_window.iconbitmap.assert_called_once()
    
    def test_difficulty_lookup(self):
        """Test DIFFICULTY_LOOKUP mapping"""
        test_cases = [
            ("diff_1", "Newcomer"),
            ("diff_2", "Casual"),
            ("diff_3", "Skilled"),
            ("diff_4", "Advanced"),
            ("diff_5", "Expert"),
            ("diff_6", "Master"),
            ("diff_7", "Grandmaster"),
            ("", "No Difficulty"),
            ("invalid", "No Difficulty")  # Default case
        ]
        
        for input_diff, expected in test_cases:
            with self.subTest(input_diff=input_diff):
                result = utils.DIFFICULTY_LOOKUP.get(input_diff, "No Difficulty")
                self.assertEqual(result, expected)
    
    def test_difficulty_keymap(self):
        """Test DIFFICULTY_KEYMAP mapping"""
        test_cases = [
            ("newcomer", "1"),
            ("casual", "2"),
            ("skilled", "3"),
            ("advanced", "4"),
            ("expert", "5"),
            ("master", "6"),
            ("grandmaster", "7"),
            ("no difficulty", "")
        ]
        
        for input_name, expected in test_cases:
            with self.subTest(input_name=input_name):
                result = utils.DIFFICULTY_KEYMAP.get(input_name)
                self.assertEqual(result, expected)
    
    def test_difficulty_sorted(self):
        """Test DIFFICULTY_SORTED mapping"""
        expected_keys = ["Newcomer", "Casual", "Skilled", "Advanced", "Expert", "Master", "Grandmaster", "No Difficulty"]
        
        for key in expected_keys:
            with self.subTest(key=key):
                self.assertIn(key, utils.DIFFICULTY_SORTED)
                result = utils.DIFFICULTY_SORTED[key]
                self.assertTrue(result.startswith(("01", "02", "03", "04", "05", "06", "07", "08")))
    
    def test_get_hack_type_emoji(self):
        """Test get_hack_type_emoji function"""
        test_cases = [
            ("standard", "🎯"),
            ("kaizo", "🔥"),
            ("puzzle", "🧩"),
            ("music", "🎵"),
            ("tool_assisted", "🤖"),
            ("tool-assisted", "🤖"),  # Test hyphen variant
            ("misc", "📦"),
            ("miscellaneous", "📦"),
            ("unknown_type", "❓")  # Default case
        ]
        
        for hack_type, expected in test_cases:
            with self.subTest(hack_type=hack_type):
                result = utils.get_hack_type_emoji(hack_type)
                self.assertEqual(result, expected)
    
    def test_safe_filename(self):
        """Test safe_filename function"""
        test_cases = [
            ("Normal Filename", "Normal Filename"),
            ("File<>Name", "FileName"),
            ('File"Name', "FileName"),
            ("File/\\Name", "FileName"),
            ("File|Name", "FileName"),
            ("File?Name", "FileName"),
            ("File*Name", "FileName"),
            ("File:Name", "FileName"),
            ("  Spaced  ", "Spaced"),
            ("", ""),
            ("Multiple<>Bad**Chars", "MultipleBadChars")
        ]
        
        for input_name, expected in test_cases:
            with self.subTest(input_name=input_name):
                result = utils.safe_filename(input_name)
                self.assertEqual(result, expected)
    
    def test_title_case(self):
        """Test title_case function"""
        test_cases = [
            ("hello world", "Hello World"),
            ("HELLO WORLD", "Hello World"),
            ("hELLo WoRLd", "Hello World"),
            ("", ""),
            ("a", "A"),
            ("mario's adventure", "Mario's Adventure"),
            ("ROM hack", "ROM Hack"),
            ("someVeryLongCamelCase", "Some Very Long Camel Case")
        ]
        
        for input_text, expected in test_cases:
            with self.subTest(input_text=input_text):
                result = utils.title_case(input_text)
                self.assertEqual(result, expected)
    
    def test_clean_hack_title(self):
        """Test clean_hack_title function"""
        test_cases = [
            ("Super Mario World: The Adventure", "Super Mario World The Adventure"),
            ("Mario's Quest (Demo)", "Mario's Quest Demo"),
            ("Test [v1.0]", "Test v1.0"),
            ("Hack {Final}", "Hack Final"),
            ("Normal Title", "Normal Title"),
            ("", ""),
            ("Multiple (Parens) [And] {Brackets}", "Multiple Parens And Brackets")
        ]
        
        for input_title, expected in test_cases:
            with self.subTest(input_title=input_title):
                result = utils.clean_hack_title(input_title)
                self.assertEqual(result, expected)
    
    def test_format_hack_title_basic(self):
        """Test format_hack_title with basic input"""
        result = utils.format_hack_title("test hack")
        self.assertEqual(result, "Test Hack")
    
    def test_format_hack_title_with_version(self):
        """Test format_hack_title with version numbers"""
        test_cases = [
            ("hack v1.0", "Hack v1.0"),
            ("hack v2.1", "Hack v2.1"),
            ("hack version 1.0", "Hack v1.0"),
            ("hack ver 2.0", "Hack v2.0"),
            ("hack revision 1", "Hack v1"),
            ("hack rev 2", "Hack v2")
        ]
        
        for input_title, expected in test_cases:
            with self.subTest(input_title=input_title):
                result = utils.format_hack_title(input_title)
                self.assertEqual(result, expected)
    
    def test_format_hack_title_with_demo(self):
        """Test format_hack_title with demo markers"""
        test_cases = [
            ("hack (demo)", "Hack (Demo)"),
            ("hack [demo]", "Hack (Demo)"),
            ("hack {demo}", "Hack (Demo)"),
            ("hack - demo", "Hack (Demo)")
        ]
        
        for input_title, expected in test_cases:
            with self.subTest(input_title=input_title):
                result = utils.format_hack_title(input_title)
                self.assertEqual(result, expected)
    
    def test_get_sorted_folder_name(self):
        """Test get_sorted_folder_name function"""
        test_cases = [
            ("Newcomer", "01 - Newcomer"),
            ("Casual", "02 - Casual"),
            ("Skilled", "03 - Skilled"),
            ("Advanced", "04 - Advanced"),
            ("Expert", "05 - Expert"),
            ("Master", "06 - Master"),
            ("Grandmaster", "07 - Grandmaster"),
            ("No Difficulty", "08 - No Difficulty"),
            ("Unknown", "08 - No Difficulty")  # Default case
        ]
        
        for input_difficulty, expected in test_cases:
            with self.subTest(input_difficulty=input_difficulty):
                result = utils.get_sorted_folder_name(input_difficulty)
                self.assertEqual(result, expected)
    
    def test_make_output_path(self):
        """Test make_output_path function"""
        base_dir = "/test/output"
        hack_type = "kaizo"
        folder_name = "05 - Expert"
        
        result = utils.make_output_path(base_dir, hack_type, folder_name)
        expected = os.path.join(base_dir, "Kaizo", folder_name)
        self.assertEqual(result, expected)
    
    def test_rename_file_success(self):
        """Test rename_file with successful rename"""
        # Create test files
        old_path = os.path.join(self.test_dir, "old_file.txt")
        new_path = os.path.join(self.test_dir, "new_file.txt")
        
        with open(old_path, 'w') as f:
            f.write("test content")
        
        utils.rename_file(old_path, new_path)
        
        self.assertFalse(os.path.exists(old_path))
        self.assertTrue(os.path.exists(new_path))
    
    def test_rename_file_failure(self):
        """Test rename_file with failure case"""
        old_path = "/nonexistent/file.txt"
        new_path = "/nonexistent/new_file.txt"
        
        # Should not raise exception
        utils.rename_file(old_path, new_path)
    
    def test_rename_files_in_directory(self):
        """Test rename_files_in_directory function"""
        # Create test directory structure
        test_subdir = os.path.join(self.test_dir, "subdir")
        os.makedirs(test_subdir, exist_ok=True)
        
        # Create test files
        old_file1 = os.path.join(test_subdir, "Old File Name.smc")
        old_file2 = os.path.join(test_subdir, "Another Old Name.smc")
        
        with open(old_file1, 'w') as f:
            f.write("test1")
        with open(old_file2, 'w') as f:
            f.write("test2")
        
        # Rename files
        utils.rename_files_in_directory(test_subdir, "Old File Name", "New File Name")
        utils.rename_files_in_directory(test_subdir, "Another Old Name", "Another New Name")
        
        # Check results
        new_file1 = os.path.join(test_subdir, "New File Name.smc")
        new_file2 = os.path.join(test_subdir, "Another New Name.smc")
        
        self.assertFalse(os.path.exists(old_file1))
        self.assertFalse(os.path.exists(old_file2))
        self.assertTrue(os.path.exists(new_file1))
        self.assertTrue(os.path.exists(new_file2))

if __name__ == '__main__':
    unittest.main()
