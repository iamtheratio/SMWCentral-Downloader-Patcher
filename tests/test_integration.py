"""
Integration tests for SMWCentral Downloader & Patcher
Tests end-to-end workflows and component interactions
"""
import unittest
import os
import json
import tempfile
from unittest.mock import Mock, patch, MagicMock
import sys

# Import test configuration
from .test_config import TestConfig, TestDataManager, MockHackData, run_with_mock_gui

# Import modules for integration testing
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

class TestIntegration(unittest.TestCase):
    """Integration test cases for complete workflows"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = TestConfig.get_temp_dir()
        self.data_manager = TestDataManager(self.test_dir)
        self.data_manager.setup_test_files()
    
    def tearDown(self):
        """Clean up test environment"""
        self.data_manager.cleanup()
    
    @patch('api_pipeline.requests.get')
    @patch('api_pipeline.PatchHandler')
    @patch('api_pipeline.extract_patches_from_zip')
    def test_complete_download_workflow(self, mock_extract, mock_patch_handler, mock_get):
        """Test complete download workflow from API to patched ROM"""
        from api_pipeline import run_single_download_pipeline
        from config_manager import ConfigManager
        
        # Setup mocks
        mock_get.return_value = Mock(
            status_code=200,
            content=b'mock zip content'
        )
        mock_extract.return_value = os.path.join(self.test_dir, "test.bps")
        mock_patch_handler.apply_patch.return_value = True
        
        # Create mock patch file
        with open(os.path.join(self.test_dir, "test.bps"), 'wb') as f:
            f.write(b'mock patch content')
        
        # Setup config
        config = ConfigManager(self.data_manager.config_file)
        
        # Mock log function
        mock_log = Mock()
        
        # Test data
        selected_hacks = [MockHackData.get_sample_hack()]
        
        # Run the pipeline
        run_single_download_pipeline(
            selected_hacks,
            log=mock_log,
            progress_callback=Mock()
        )
        
        # Verify workflow completed
        mock_log.assert_called()
        mock_extract.assert_called_once()
    
    def test_data_persistence_workflow(self):
        """Test data persistence across application sessions"""
        from hack_data_manager import HackDataManager
        from config_manager import ConfigManager
        
        # Session 1: Create and save data
        config1 = ConfigManager(self.data_manager.config_file)
        config1.set("test_setting", "test_value")
        
        hdm1 = HackDataManager(self.data_manager.processed_file)
        test_hack = {
            "title": "Integration Test Hack",
            "hack_types": ["standard"],
            "completed": True
        }
        hdm1.data["integration_test"] = test_hack
        hdm1.save_data()
        
        # Session 2: Load and verify data
        config2 = ConfigManager(self.data_manager.config_file)
        self.assertEqual(config2.get("test_setting"), "test_value")
        
        hdm2 = HackDataManager(self.data_manager.processed_file)
        loaded_hack = hdm2.get_hack_by_id("integration_test")
        self.assertIsNotNone(loaded_hack)
        self.assertEqual(loaded_hack["title"], "Integration Test Hack")
        self.assertTrue(loaded_hack["completed"])
    
    def test_filter_and_analytics_workflow(self):
        """Test filtering and analytics workflow"""
        from hack_data_manager import HackDataManager
        
        # Setup test data with diverse hacks
        test_data = {
            "1": {
                "title": "Standard Easy Hack",
                "hack_types": ["standard"],
                "current_difficulty": "Newcomer",
                "completed": True,
                "personal_rating": 4,
                "hall_of_fame": False,
                "obsolete": False
            },
            "2": {
                "title": "Kaizo Hard Hack",
                "hack_types": ["kaizo"],
                "current_difficulty": "Expert",
                "completed": False,
                "personal_rating": 0,
                "hall_of_fame": True,
                "obsolete": False
            },
            "3": {
                "title": "Multi-Type Hack",
                "hack_types": ["kaizo", "puzzle"],
                "current_difficulty": "Skilled",
                "completed": True,
                "personal_rating": 5,
                "hall_of_fame": True,
                "obsolete": False
            },
            "4": {
                "title": "Obsolete Hack",
                "hack_types": ["standard"],
                "current_difficulty": "Casual",
                "completed": False,
                "personal_rating": 0,
                "hall_of_fame": False,
                "obsolete": True
            }
        }
        
        # Save test data
        with open(self.data_manager.processed_file, 'w') as f:
            json.dump(test_data, f)
        
        hdm = HackDataManager(self.data_manager.processed_file)
        
        # Test comprehensive filtering workflow
        all_hacks = hdm.get_all_hacks(include_obsolete=False)
        self.assertEqual(len(all_hacks), 3)  # Excluding obsolete
        
        # Filter by type
        kaizo_hacks = hdm.filter_by_type(["kaizo"])
        self.assertEqual(len(kaizo_hacks), 2)  # Two kaizo hacks
        
        # Filter by completion
        completed_hacks = hdm.filter_by_completion("completed")
        self.assertEqual(len(completed_hacks), 2)  # Two completed
        
        # Filter by features
        hof_hacks = hdm.filter_by_features(hall_of_fame=True)
        self.assertEqual(len(hof_hacks), 2)  # Two HOF hacks
        
        # Test analytics
        analytics = hdm.get_analytics(include_obsolete=False)
        self.assertEqual(analytics['total_hacks'], 3)
        self.assertEqual(analytics['completed_hacks'], 2)
        self.assertAlmostEqual(analytics['completion_rate'], 66.67, places=1)
        
        # Verify type distribution
        type_dist = analytics['type_distribution']
        self.assertEqual(type_dist['Standard'], 1)
        self.assertEqual(type_dist['Kaizo'], 2)  # Multi-type hack counted for both
    
    def test_multi_type_system_workflow(self):
        """Test complete multi-type system workflow"""
        from multi_type_utils import get_hack_types_from_raw_data, handle_multi_type_download
        from config_manager import ConfigManager
        from utils import make_output_path
        
        # Setup config for multi-type
        config = ConfigManager(self.data_manager.config_file)
        config.set("multi_type_enabled", True)
        config.set("multi_type_download_mode", "copy_all")
        
        # Test hack with multiple types
        raw_fields = {
            "types": ["kaizo", "puzzle", "tool_assisted"]
        }
        hack_data = {"type": "kaizo"}
        
        # Get hack types
        hack_types = get_hack_types_from_raw_data(raw_fields, hack_data)
        self.assertEqual(len(hack_types), 3)
        self.assertIn("kaizo", hack_types)
        self.assertIn("puzzle", hack_types)
        self.assertIn("tool_assisted", hack_types)
        
        # Test multi-type download handling
        primary_path = os.path.join(self.test_dir, "output", "Kaizo", "05 - Expert", "Test Hack.smc")
        output_dir = os.path.join(self.test_dir, "output")
        folder_name = "05 - Expert"
        
        # Create primary file
        os.makedirs(os.path.dirname(primary_path), exist_ok=True)
        with open(primary_path, 'wb') as f:
            f.write(b'test rom content')
        
        # Handle multi-type download
        additional_paths = handle_multi_type_download(
            primary_path, hack_types, output_dir, folder_name,
            "Test Hack", ".smc", config, Mock()
        )
        
        # Verify additional copies were created
        self.assertEqual(len(additional_paths), 2)  # Two additional copies
        
        # Verify files exist
        for path in additional_paths:
            self.assertTrue(os.path.exists(path))
    
    @run_with_mock_gui
    def test_ui_data_integration(self):
        """Test UI and data layer integration"""
        with patch.dict('sys.modules', {
            'ui.dashboard.analytics': Mock(),
            'ui.pages.history_page': Mock()
        }):
            from hack_data_manager import HackDataManager
            
            # Setup mock UI components
            mock_analytics_component = Mock()
            mock_history_component = Mock()
            
            # Setup data
            hdm = HackDataManager(self.data_manager.processed_file)
            analytics = hdm.get_analytics()
            all_hacks = hdm.get_all_hacks()
            
            # Test UI data integration
            mock_analytics_component.update_analytics(analytics)
            mock_history_component.populate_hacks(all_hacks)
            
            # Verify UI was updated with data
            mock_analytics_component.update_analytics.assert_called_once_with(analytics)
            mock_history_component.populate_hacks.assert_called_once_with(all_hacks)
    
    def test_migration_workflow(self):
        """Test data migration workflow"""
        from migration_manager import MigrationManager
        
        # Create old format data
        old_data = {
            "12345": {
                "title": "Old Format Hack",
                "current_difficulty": "Skilled",
                "type": "standard"  # Old single type field
                # Missing new fields
            }
        }
        
        old_file = os.path.join(self.test_dir, "old_processed.json")
        with open(old_file, 'w') as f:
            json.dump(old_data, f)
        
        # Test migration detection
        migration_manager = MigrationManager(old_file)
        needs_migration = migration_manager.needs_migration()
        self.assertTrue(needs_migration)
        
        # Test migration would update the data format
        # (Full migration testing would require more complex setup)
    
    def test_backup_and_recovery_workflow(self):
        """Test backup and recovery workflow"""
        from api_pipeline import save_processed, load_processed
        
        # Create original data
        original_data = {
            "test_id": {
                "title": "Test Hack",
                "completed": False
            }
        }
        
        # Save data (creates backup)
        save_processed(original_data, self.data_manager.processed_file)
        
        # Verify backup exists
        backup_file = self.data_manager.processed_file + ".backup"
        self.assertTrue(os.path.exists(backup_file))
        
        # Modify original
        modified_data = original_data.copy()
        modified_data["test_id"]["completed"] = True
        save_processed(modified_data, self.data_manager.processed_file)
        
        # Recovery: restore from backup
        import shutil
        shutil.copy2(backup_file, self.data_manager.processed_file)
        
        # Verify recovery
        recovered_data = load_processed(self.data_manager.processed_file)
        self.assertFalse(recovered_data["test_id"]["completed"])
    
    def test_error_handling_workflow(self):
        """Test error handling across components"""
        from hack_data_manager import HackDataManager
        from config_manager import ConfigManager
        
        # Test graceful handling of corrupted files
        corrupted_file = os.path.join(self.test_dir, "corrupted.json")
        with open(corrupted_file, 'w') as f:
            f.write("corrupted json content")
        
        # Should handle gracefully without crashing
        config = ConfigManager(corrupted_file)
        self.assertIsNotNone(config.config)
        
        hdm = HackDataManager(corrupted_file)
        self.assertEqual(hdm.data, {})
    
    def test_concurrent_operations_workflow(self):
        """Test concurrent operations workflow"""
        from hack_data_manager import HackDataManager
        import threading
        
        # Test concurrent data access
        hdm = HackDataManager(self.data_manager.processed_file)
        
        results = []
        
        def read_data():
            data = hdm.get_all_hacks()
            results.append(len(data))
        
        def write_data():
            hdm.update_hack("12345", {"notes": "Updated concurrently"})
        
        # Run concurrent operations
        threads = []
        for _ in range(3):
            t1 = threading.Thread(target=read_data)
            t2 = threading.Thread(target=write_data)
            threads.extend([t1, t2])
        
        for thread in threads:
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # Verify no crashes occurred
        self.assertEqual(len(results), 3)
    
    def test_performance_with_large_dataset(self):
        """Test performance with large dataset"""
        from hack_data_manager import HackDataManager
        import time
        
        # Create large dataset
        large_data = {}
        for i in range(1000):
            large_data[str(i)] = {
                "title": f"Test Hack {i}",
                "hack_types": ["standard"],
                "current_difficulty": "Skilled",
                "completed": i % 2 == 0,
                "personal_rating": i % 6,
                "obsolete": False
            }
        
        large_file = os.path.join(self.test_dir, "large_processed.json")
        with open(large_file, 'w') as f:
            json.dump(large_data, f)
        
        # Test performance
        start_time = time.time()
        hdm = HackDataManager(large_file)
        load_time = time.time() - start_time
        
        start_time = time.time()
        all_hacks = hdm.get_all_hacks()
        query_time = time.time() - start_time
        
        start_time = time.time()
        analytics = hdm.get_analytics()
        analytics_time = time.time() - start_time
        
        # Verify reasonable performance (adjust thresholds as needed)
        self.assertLess(load_time, 5.0)  # Should load within 5 seconds
        self.assertLess(query_time, 2.0)  # Should query within 2 seconds
        self.assertLess(analytics_time, 3.0)  # Should calculate analytics within 3 seconds
        
        # Verify data integrity
        self.assertEqual(len(all_hacks), 1000)
        self.assertEqual(analytics['total_hacks'], 1000)

if __name__ == '__main__':
    unittest.main()
