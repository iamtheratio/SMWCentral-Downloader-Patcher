"""
Test configuration and utilities for SMWCentral Downloader & Patcher tests
"""
import os
import sys
import tempfile
import shutil
import json
from unittest.mock import Mock, MagicMock
import tkinter as tk

# Add the project root to Python path for imports
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

class TestConfig:
    """Configuration for test environment"""
    
    @staticmethod
    def get_test_data_dir():
        """Get the test data directory"""
        return os.path.join(os.path.dirname(__file__), 'data')
    
    @staticmethod
    def get_temp_dir():
        """Create a temporary directory for tests"""
        return tempfile.mkdtemp(prefix='smwc_test_')
    
    @staticmethod
    def cleanup_temp_dir(temp_dir):
        """Clean up a temporary directory"""
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)

class MockHackData:
    """Mock hack data for testing"""
    
    @staticmethod
    def get_sample_hack():
        """Get a sample hack for testing"""
        return {
            "id": 12345,
            "name": "Test Hack",
            "authors": ["Test Author"],
            "type": "standard",
            "difficulty": "diff_3",
            "length": 95,
            "download_url": "https://example.com/test.zip",
            "raw_fields": {
                "difficulty": "diff_3",
                "hof": False,
                "sa1": False,
                "collab": False,
                "demo": False,
                "length": 95,
                "obsolete": False
            }
        }
    
    @staticmethod
    def get_sample_processed_data():
        """Get sample processed.json data"""
        return {
            "12345": {
                "title": "Test Hack",
                "current_difficulty": "Skilled",
                "folder_name": "03 - Skilled",
                "file_path": "/test/path/Test Hack.smc",
                "additional_paths": [],
                "hack_type": "standard",
                "hack_types": ["standard"],
                "hall_of_fame": False,
                "sa1_compatibility": False,
                "collaboration": False,
                "demo": False,
                "authors": ["Test Author"],
                "exits": 95,
                "obsolete": False,
                "completed": False,
                "completed_date": None,
                "personal_rating": 0,
                "notes": ""
            }
        }
    
    @staticmethod
    def get_multi_type_hack():
        """Get a multi-type hack for testing"""
        return {
            "id": 67890,
            "name": "Multi Type Hack",
            "authors": ["Multi Author"],
            "type": "kaizo",
            "difficulty": "diff_5",
            "length": 150,
            "download_url": "https://example.com/multi.zip",
            "raw_fields": {
                "difficulty": "diff_5",
                "hof": True,
                "sa1": True,
                "collab": True,
                "demo": False,
                "length": 150,
                "obsolete": False,
                "types": ["kaizo", "puzzle"]  # Multi-type
            }
        }

class MockTkinter:
    """Mock Tkinter components for GUI testing"""
    
    @staticmethod
    def create_mock_root():
        """Create a mock root window"""
        mock_root = Mock()
        mock_root.update = Mock()
        mock_root.update_idletasks = Mock()
        mock_root.after = Mock()
        mock_root.bind = Mock()
        mock_root.protocol = Mock()
        return mock_root
    
    @staticmethod
    def create_mock_widget():
        """Create a mock widget"""
        mock_widget = Mock()
        mock_widget.configure = Mock()
        mock_widget.config = Mock()
        mock_widget.pack = Mock()
        mock_widget.grid = Mock()
        mock_widget.place = Mock()
        return mock_widget

class TestDataManager:
    """Manages test data files and setup"""
    
    def __init__(self, test_dir):
        self.test_dir = test_dir
        self.config_file = os.path.join(test_dir, "config.json")
        self.processed_file = os.path.join(test_dir, "processed.json")
    
    def setup_test_files(self):
        """Set up test configuration and data files"""
        # Create test config
        test_config = {
            "base_rom_path": os.path.join(self.test_dir, "base.smc"),
            "output_dir": os.path.join(self.test_dir, "output"),
            "multi_type_enabled": True,
            "multi_type_download_mode": "copy_all",
            "theme": "dark"
        }
        
        with open(self.config_file, 'w') as f:
            json.dump(test_config, f, indent=2)
        
        # Create test processed data
        with open(self.processed_file, 'w') as f:
            json.dump(MockHackData.get_sample_processed_data(), f, indent=2)
        
        # Create directories
        os.makedirs(os.path.join(self.test_dir, "output"), exist_ok=True)
        
        # Create dummy ROM file
        with open(os.path.join(self.test_dir, "base.smc"), 'wb') as f:
            f.write(b'\x00' * 1024)  # Dummy ROM data
    
    def cleanup(self):
        """Clean up test files"""
        TestConfig.cleanup_temp_dir(self.test_dir)

def create_mock_response(status_code=200, json_data=None, content=b''):
    """Create a mock HTTP response"""
    mock_response = Mock()
    mock_response.status_code = status_code
    mock_response.json.return_value = json_data or {}
    mock_response.content = content
    mock_response.raise_for_status = Mock()
    if status_code >= 400:
        mock_response.raise_for_status.side_effect = Exception(f"HTTP {status_code}")
    return mock_response

def run_with_mock_gui(test_func):
    """Decorator to run tests with mocked GUI components"""
    def wrapper(*args, **kwargs):
        # Mock tkinter imports to prevent GUI creation during tests
        import sys
        from unittest.mock import patch
        
        with patch.dict('sys.modules', {
            'tkinter': Mock(),
            'tkinter.ttk': Mock(),
            'sv_ttk': Mock(),
            'pywinstyles': Mock()
        }):
            return test_func(*args, **kwargs)
    
    return wrapper
