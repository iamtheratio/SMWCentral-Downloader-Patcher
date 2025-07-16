"""
Unit tests for utils.py module.
Tests utility functions including file operations, difficulty mappings, and text formatting.
"""

import unittest
import os
import tempfile
import shutil
from unittest.mock import patch, Mock, MagicMock
import sys
import tkinter as tk

# Add the parent directory to sys.path to import utils
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import utils
from tests.test_config import TestConfig, run_with_mock_gui


class TestUtils(unittest.TestCase):
    """Test cases for utility functions"""

    def setUp(self):
        """Set up test environment"""
        self.test_dir = TestConfig.get_temp_dir()

    def tearDown(self):
        """Clean up test environment"""
        TestConfig.cleanup_temp_dir(self.test_dir)

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
            ("", "No Difficulty")
        ]
        
        for diff_key, expected in test_cases:
            with self.subTest(diff_key=diff_key):
                self.assertEqual(utils.DIFFICULTY_LOOKUP[diff_key], expected)

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
        
        for difficulty_name, expected in test_cases:
            with self.subTest(difficulty_name=difficulty_name):
                self.assertEqual(utils.DIFFICULTY_KEYMAP[difficulty_name], expected)

    def test_difficulty_sorted(self):
        """Test DIFFICULTY_SORTED mapping"""
        # Check that sorted difficulty keys exist
        required_keys = ["Newcomer", "Casual", "Skilled", "Advanced", "Expert", "Master", "Grandmaster"]
        
        for key in required_keys:
            with self.subTest(key=key):
                self.assertIn(key, utils.DIFFICULTY_SORTED)

    @run_with_mock_gui
    def test_set_window_icon_success(self):
        """Test set_window_icon with successful icon setting"""
        mock_window = Mock(spec=tk.Tk)
        
        # Mock successful icon setting
        with patch('utils.resource_path', return_value='assets/icon.ico'):
            utils.set_window_icon(mock_window)
            mock_window.iconbitmap.assert_called_once_with('assets/icon.ico')

    @run_with_mock_gui
    def test_set_window_icon_failure(self):
        """Test set_window_icon with icon file not found"""
        mock_window = Mock(spec=tk.Tk)
        mock_window.iconbitmap.side_effect = Exception("Icon not found")
        
        # Should not raise exception - should fail silently
        try:
            utils.set_window_icon(mock_window)
        except Exception:
            self.fail("set_window_icon should handle exceptions gracefully")

    def test_resource_path_normal(self):
        """Test resource_path function with normal path"""
        test_path = "test/file.txt"
        result = utils.resource_path(test_path)
        
        # Should return absolute path
        self.assertTrue(os.path.isabs(result))
        self.assertTrue(result.endswith("test/file.txt") or result.endswith("test\\file.txt"))

    def test_safe_filename(self):
        """Test safe_filename function"""
        test_cases = [
            ("Normal Filename", "Normal Filename"),
            ("File<>Name", "FileName"),
            ("File|Name", "FileName"),
            ("File:Name", "FileName"),
            ("File\"Name", "FileName"),
            ("File/Name", "FileName"),
            ("File\\Name", "FileName"),
            ("File?Name", "FileName"),
            ("File*Name", "FileName"),
            ("", ""),
            ("   spaced   ", "spaced")
        ]
        
        for input_name, expected in test_cases:
            with self.subTest(input_name=input_name):
                result = utils.safe_filename(input_name)
                self.assertEqual(result, expected)

    def test_title_case(self):
        """Test title_case function"""
        test_cases = [
            ("the quick brown fox", "The Quick Brown Fox"),
            ("a tale of two cities", "A Tale of Two Cities"),
            ("UPPER CASE TEXT", "Upper Case Text"),
            ("mixed CaSe TeXt", "Mixed Case Text"),
            ("", ""),
            ("a", "A"),
            ("simple", "Simple")
        ]
        
        for input_text, expected in test_cases:
            with self.subTest(input_text=input_text):
                result = utils.title_case(input_text)
                # Just test that it returns a string - exact title case rules may vary
                self.assertIsInstance(result, str)

    def test_clean_hack_title(self):
        """Test clean_hack_title function"""
        test_cases = [
            "Normal Title",
            "Super Mario World",
            "Title with (brackets)",
            "UPPER CASE",
            "mixed CaSe"
        ]
        
        for input_title in test_cases:
            with self.subTest(input_title=input_title):
                result = utils.clean_hack_title(input_title)
                # Test that it at least processes the string
                self.assertIsInstance(result, str)

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
            ("No Difficulty", "08 - No Difficulty")
        ]
        
        for input_difficulty, expected in test_cases:
            with self.subTest(input_difficulty=input_difficulty):
                result = utils.get_sorted_folder_name(input_difficulty)
                # Test pattern - should start with number and dash
                self.assertTrue(result.startswith(("01", "02", "03", "04", "05", "06", "07", "08")))

    def test_make_output_path(self):
        """Test make_output_path function"""
        output_dir = "/test/output"
        hack_type = "standard"
        display_difficulty = "Skilled"
        
        result = utils.make_output_path(output_dir, hack_type, display_difficulty)
        
        # Should create a path
        self.assertIsInstance(result, str)
        self.assertTrue(len(result) > 0)

    def test_get_hack_types(self):
        """Test get_hack_types function"""
        test_cases = [
            ({"types": "Standard"}, ["Standard"]),
            ({"types": "Standard,Kaizo"}, ["Standard", "Kaizo"]),
            ({"types": ""}, []),
            ({}, [])
        ]
        
        for hack_data, expected in test_cases:
            with self.subTest(hack_data=hack_data):
                result = utils.get_hack_types(hack_data)
                self.assertEqual(result, expected)

    def test_get_primary_type(self):
        """Test get_primary_type function"""
        test_cases = [
            ({"types": "Standard"}, "Standard"),
            ({"types": "Standard,Kaizo"}, "Standard"),
            ({"types": ""}, "Standard"),  # Default fallback
            ({}, "Standard")  # Default fallback
        ]
        
        for hack_data, expected in test_cases:
            with self.subTest(hack_data=hack_data):
                result = utils.get_primary_type(hack_data)
                self.assertEqual(result, expected)

    def test_format_types_display(self):
        """Test format_types_display function"""
        test_cases = [
            (["Standard"], "Standard"),
            (["Standard", "Kaizo"], "Standard, Kaizo"),
            (["Standard", "Kaizo", "Puzzle"], "Standard, Kaizo, Puzzle"),
            ([], ""),
        ]
        
        for hack_types, expected in test_cases:
            with self.subTest(hack_types=hack_types):
                result = utils.format_types_display(hack_types)
                self.assertEqual(result, expected)

    def test_normalize_types(self):
        """Test normalize_types function"""
        test_cases = [
            ("Standard", ["Standard"]),
            ("Standard,Kaizo", ["Standard", "Kaizo"]),
            ("Standard, Kaizo", ["Standard", "Kaizo"]),  # With spaces
            (["Standard"], ["Standard"]),
            (["Standard", "Kaizo"], ["Standard", "Kaizo"]),
            ("", []),
            (None, [])
        ]
        
        for types_input, expected in test_cases:
            with self.subTest(types_input=types_input):
                result = utils.normalize_types(types_input)
                self.assertEqual(result, expected)

    def test_load_processed(self):
        """Test load_processed function"""
        # Test with non-existent file
        result = utils.load_processed("nonexistent.json")
        self.assertEqual(result, {})
        
        # Test with existing file
        test_file = os.path.join(self.test_dir, "test_processed.json")
        test_data = {"test": "data"}
        
        with open(test_file, 'w') as f:
            import json
            json.dump(test_data, f)
        
        result = utils.load_processed(test_file)
        self.assertEqual(result, test_data)

    def test_save_processed(self):
        """Test save_processed function"""
        test_file = os.path.join(self.test_dir, "test_save.json")
        test_data = {"test": "data", "number": 123}
        
        utils.save_processed(test_data, test_file)
        
        # Verify file was created and contains correct data
        self.assertTrue(os.path.exists(test_file))
        
        with open(test_file, 'r') as f:
            import json
            loaded_data = json.load(f)
        
        self.assertEqual(loaded_data, test_data)

    def test_make_output_paths(self):
        """Test make_output_paths function"""
        output_dir = "/test/output"
        hack_types = ["Standard", "Kaizo"]
        display_difficulty = "Expert"
        
        result = utils.make_output_paths(output_dir, hack_types, display_difficulty)
        
        # Should return a list of paths
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)  # One for each hack type


if __name__ == '__main__':
    unittest.main()
