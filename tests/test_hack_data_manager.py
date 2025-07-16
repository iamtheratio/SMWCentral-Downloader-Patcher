"""
Unit tests for hack_data_manager.py module
Tests hack data management, filtering, analytics, and database operations
"""
import unittest
import os
import json
import tempfile
from unittest.mock import Mock, patch, MagicMock
import sys

# Import test configuration
from .test_config import TestConfig, TestDataManager, MockHackData

# Import the module to test
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from hack_data_manager import HackDataManager

class TestHackDataManager(unittest.TestCase):
    """Test cases for HackDataManager class"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = TestConfig.get_temp_dir()
        self.data_manager = TestDataManager(self.test_dir)
        self.data_manager.setup_test_files()
        
        # Create HackDataManager instance
        self.hdm = HackDataManager(self.data_manager.processed_file)
        
        # Add more test data
        self.test_data = {
            "12345": {
                "title": "Test Standard Hack",
                "current_difficulty": "Skilled",
                "folder_name": "03 - Skilled",
                "file_path": "/test/Standard/03 - Skilled/Test Standard Hack.smc",
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
            },
            "67890": {
                "title": "Test Kaizo Hack",
                "current_difficulty": "Expert",
                "folder_name": "05 - Expert",
                "file_path": "/test/Kaizo/05 - Expert/Test Kaizo Hack.smc",
                "additional_paths": ["/test/Puzzle/05 - Expert/Test Kaizo Hack.smc"],
                "hack_type": "kaizo",
                "hack_types": ["kaizo", "puzzle"],
                "hall_of_fame": True,
                "sa1_compatibility": True,
                "collaboration": True,
                "demo": False,
                "authors": ["Kaizo Author", "Co-Author"],
                "exits": 150,
                "obsolete": False,
                "completed": True,
                "completed_date": "2024-01-15",
                "personal_rating": 5,
                "notes": "Excellent hack!"
            },
            "11111": {
                "title": "Obsolete Hack",
                "current_difficulty": "Casual",
                "folder_name": "02 - Casual",
                "file_path": "/test/Standard/02 - Casual/Obsolete Hack.smc",
                "additional_paths": [],
                "hack_type": "standard",
                "hack_types": ["standard"],
                "hall_of_fame": False,
                "sa1_compatibility": False,
                "collaboration": False,
                "demo": False,
                "authors": ["Old Author"],
                "exits": 50,
                "obsolete": True,
                "completed": False,
                "completed_date": None,
                "personal_rating": 0,
                "notes": ""
            }
        }
        
        # Save test data
        with open(self.data_manager.processed_file, 'w') as f:
            json.dump(self.test_data, f, indent=2)
    
    def tearDown(self):
        """Clean up test environment"""
        self.data_manager.cleanup()
    
    def test_init_with_existing_file(self):
        """Test initialization with existing processed.json file"""
        hdm = HackDataManager(self.data_manager.processed_file)
        self.assertIsNotNone(hdm.data)
        self.assertEqual(len(hdm.data), 3)
    
    def test_init_with_missing_file(self):
        """Test initialization with missing processed.json file"""
        missing_file = os.path.join(self.test_dir, "missing.json")
        hdm = HackDataManager(missing_file)
        self.assertEqual(hdm.data, {})
    
    def test_get_all_hacks_include_obsolete(self):
        """Test get_all_hacks with obsolete hacks included"""
        result = self.hdm.get_all_hacks(include_obsolete=True)
        self.assertEqual(len(result), 3)
        
        # Verify all hacks are present
        hack_ids = [hack['id'] for hack in result]
        self.assertIn('12345', hack_ids)
        self.assertIn('67890', hack_ids)
        self.assertIn('11111', hack_ids)
    
    def test_get_all_hacks_exclude_obsolete(self):
        """Test get_all_hacks with obsolete hacks excluded (default)"""
        result = self.hdm.get_all_hacks(include_obsolete=False)
        self.assertEqual(len(result), 2)
        
        # Verify only non-obsolete hacks are present
        hack_ids = [hack['id'] for hack in result]
        self.assertIn('12345', hack_ids)
        self.assertIn('67890', hack_ids)
        self.assertNotIn('11111', hack_ids)
    
    def test_get_hack_by_id_existing(self):
        """Test getting hack by ID for existing hack"""
        result = self.hdm.get_hack_by_id("12345")
        self.assertIsNotNone(result)
        self.assertEqual(result['id'], "12345")
        self.assertEqual(result['title'], "Test Standard Hack")
    
    def test_get_hack_by_id_missing(self):
        """Test getting hack by ID for non-existing hack"""
        result = self.hdm.get_hack_by_id("99999")
        self.assertIsNone(result)
    
    def test_get_hack_by_id_obsolete_included(self):
        """Test getting obsolete hack by ID when included"""
        result = self.hdm.get_hack_by_id("11111", include_obsolete=True)
        self.assertIsNotNone(result)
        self.assertEqual(result['id'], "11111")
        self.assertTrue(result['obsolete'])
    
    def test_get_hack_by_id_obsolete_excluded(self):
        """Test getting obsolete hack by ID when excluded"""
        result = self.hdm.get_hack_by_id("11111", include_obsolete=False)
        self.assertIsNone(result)
    
    def test_filter_by_type_single(self):
        """Test filtering by single hack type"""
        result = self.hdm.filter_by_type(["kaizo"])
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['hack_types'], ["kaizo", "puzzle"])
    
    def test_filter_by_type_multiple(self):
        """Test filtering by multiple hack types"""
        result = self.hdm.filter_by_type(["standard", "kaizo"])
        self.assertEqual(len(result), 2)
        
        hack_types = set()
        for hack in result:
            hack_types.update(hack['hack_types'])
        
        self.assertIn("standard", hack_types)
        self.assertIn("kaizo", hack_types)
    
    def test_filter_by_type_empty(self):
        """Test filtering with empty type list"""
        result = self.hdm.filter_by_type([])
        self.assertEqual(len(result), 2)  # Should return all non-obsolete hacks
    
    def test_filter_by_difficulty_single(self):
        """Test filtering by single difficulty"""
        result = self.hdm.filter_by_difficulty(["Skilled"])
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['current_difficulty'], "Skilled")
    
    def test_filter_by_difficulty_multiple(self):
        """Test filtering by multiple difficulties"""
        result = self.hdm.filter_by_difficulty(["Skilled", "Expert"])
        self.assertEqual(len(result), 2)
        
        difficulties = [hack['current_difficulty'] for hack in result]
        self.assertIn("Skilled", difficulties)
        self.assertIn("Expert", difficulties)
    
    def test_filter_by_completion_completed(self):
        """Test filtering by completion status - completed only"""
        result = self.hdm.filter_by_completion("completed")
        self.assertEqual(len(result), 1)
        self.assertTrue(result[0]['completed'])
    
    def test_filter_by_completion_incomplete(self):
        """Test filtering by completion status - incomplete only"""
        result = self.hdm.filter_by_completion("incomplete")
        self.assertEqual(len(result), 1)
        self.assertFalse(result[0]['completed'])
    
    def test_filter_by_completion_all(self):
        """Test filtering by completion status - all"""
        result = self.hdm.filter_by_completion("all")
        self.assertEqual(len(result), 2)  # Non-obsolete hacks
    
    def test_filter_by_features_hof(self):
        """Test filtering by Hall of Fame feature"""
        result = self.hdm.filter_by_features(hall_of_fame=True)
        self.assertEqual(len(result), 1)
        self.assertTrue(result[0]['hall_of_fame'])
    
    def test_filter_by_features_sa1(self):
        """Test filtering by SA1 compatibility feature"""
        result = self.hdm.filter_by_features(sa1_compatibility=True)
        self.assertEqual(len(result), 1)
        self.assertTrue(result[0]['sa1_compatibility'])
    
    def test_filter_by_features_collaboration(self):
        """Test filtering by collaboration feature"""
        result = self.hdm.filter_by_features(collaboration=True)
        self.assertEqual(len(result), 1)
        self.assertTrue(result[0]['collaboration'])
    
    def test_filter_by_features_demo(self):
        """Test filtering by demo feature"""
        result = self.hdm.filter_by_features(demo=True)
        self.assertEqual(len(result), 0)  # No demo hacks in test data
    
    def test_filter_by_features_multiple(self):
        """Test filtering by multiple features"""
        result = self.hdm.filter_by_features(hall_of_fame=True, sa1_compatibility=True)
        self.assertEqual(len(result), 1)
        hack = result[0]
        self.assertTrue(hack['hall_of_fame'])
        self.assertTrue(hack['sa1_compatibility'])
    
    def test_filter_by_rating_exact(self):
        """Test filtering by exact rating"""
        result = self.hdm.filter_by_rating(5, 5)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['personal_rating'], 5)
    
    def test_filter_by_rating_range(self):
        """Test filtering by rating range"""
        result = self.hdm.filter_by_rating(0, 3)
        self.assertEqual(len(result), 1)
        self.assertLessEqual(result[0]['personal_rating'], 3)
    
    def test_search_by_title(self):
        """Test searching by title"""
        result = self.hdm.search_by_title("Standard")
        self.assertEqual(len(result), 1)
        self.assertIn("Standard", result[0]['title'])
    
    def test_search_by_title_case_insensitive(self):
        """Test searching by title (case insensitive)"""
        result = self.hdm.search_by_title("KAIZO")
        self.assertEqual(len(result), 1)
        self.assertIn("Kaizo", result[0]['title'])
    
    def test_search_by_title_partial(self):
        """Test searching by partial title"""
        result = self.hdm.search_by_title("Test")
        self.assertEqual(len(result), 2)  # Both test hacks
    
    def test_search_by_author(self):
        """Test searching by author"""
        result = self.hdm.search_by_author("Kaizo Author")
        self.assertEqual(len(result), 1)
        self.assertIn("Kaizo Author", result[0]['authors'])
    
    def test_search_by_author_partial(self):
        """Test searching by partial author name"""
        result = self.hdm.search_by_author("Author")
        self.assertEqual(len(result), 2)  # Both have "Author" in their author names
    
    def test_get_analytics_basic(self):
        """Test basic analytics calculation"""
        analytics = self.hdm.get_analytics()
        
        self.assertIn('total_hacks', analytics)
        self.assertIn('completed_hacks', analytics)
        self.assertIn('completion_rate', analytics)
        self.assertIn('type_distribution', analytics)
        self.assertIn('difficulty_distribution', analytics)
        
        self.assertEqual(analytics['total_hacks'], 2)  # Non-obsolete hacks
        self.assertEqual(analytics['completed_hacks'], 1)
        self.assertEqual(analytics['completion_rate'], 50.0)
    
    def test_get_analytics_include_obsolete(self):
        """Test analytics with obsolete hacks included"""
        analytics = self.hdm.get_analytics(include_obsolete=True)
        
        self.assertEqual(analytics['total_hacks'], 3)  # All hacks including obsolete
        self.assertEqual(analytics['completed_hacks'], 1)
        self.assertAlmostEqual(analytics['completion_rate'], 33.33, places=1)
    
    def test_get_analytics_type_distribution(self):
        """Test analytics type distribution"""
        analytics = self.hdm.get_analytics()
        type_dist = analytics['type_distribution']
        
        # Should have standard and kaizo types
        self.assertIn('Standard', type_dist)
        self.assertIn('Kaizo', type_dist)
        self.assertEqual(type_dist['Standard'], 1)
        self.assertEqual(type_dist['Kaizo'], 1)
    
    def test_get_analytics_difficulty_distribution(self):
        """Test analytics difficulty distribution"""
        analytics = self.hdm.get_analytics()
        diff_dist = analytics['difficulty_distribution']
        
        self.assertIn('Skilled', diff_dist)
        self.assertIn('Expert', diff_dist)
        self.assertEqual(diff_dist['Skilled'], 1)
        self.assertEqual(diff_dist['Expert'], 1)
    
    def test_get_analytics_special_features(self):
        """Test analytics special features calculation"""
        analytics = self.hdm.get_analytics()
        
        self.assertIn('hall_of_fame_count', analytics)
        self.assertIn('sa1_compatible_count', analytics)
        self.assertIn('collaboration_count', analytics)
        self.assertIn('demo_count', analytics)
        
        self.assertEqual(analytics['hall_of_fame_count'], 1)
        self.assertEqual(analytics['sa1_compatible_count'], 1)
        self.assertEqual(analytics['collaboration_count'], 1)
        self.assertEqual(analytics['demo_count'], 0)
    
    def test_get_recent_hacks(self):
        """Test getting recent hacks"""
        # This test would need actual date handling
        # For now, just test that the method exists and returns data
        result = self.hdm.get_recent_hacks(limit=5)
        self.assertIsInstance(result, list)
        self.assertLessEqual(len(result), 5)
    
    def test_get_favorites(self):
        """Test getting favorite hacks (high ratings)"""
        result = self.hdm.get_favorites(min_rating=4)
        self.assertEqual(len(result), 1)
        self.assertGreaterEqual(result[0]['personal_rating'], 4)
    
    def test_update_hack_existing(self):
        """Test updating existing hack data"""
        hack_id = "12345"
        updates = {
            "completed": True,
            "completed_date": "2024-01-20",
            "personal_rating": 4,
            "notes": "Great hack!"
        }
        
        success = self.hdm.update_hack(hack_id, updates)
        self.assertTrue(success)
        
        # Verify updates
        updated_hack = self.hdm.get_hack_by_id(hack_id)
        self.assertTrue(updated_hack['completed'])
        self.assertEqual(updated_hack['completed_date'], "2024-01-20")
        self.assertEqual(updated_hack['personal_rating'], 4)
        self.assertEqual(updated_hack['notes'], "Great hack!")
    
    def test_update_hack_nonexistent(self):
        """Test updating non-existent hack"""
        success = self.hdm.update_hack("99999", {"completed": True})
        self.assertFalse(success)
    
    def test_delete_hack_existing(self):
        """Test deleting existing hack"""
        hack_id = "12345"
        
        # Verify hack exists
        self.assertIsNotNone(self.hdm.get_hack_by_id(hack_id))
        
        # Delete hack
        success = self.hdm.delete_hack(hack_id)
        self.assertTrue(success)
        
        # Verify hack is gone
        self.assertIsNone(self.hdm.get_hack_by_id(hack_id))
    
    def test_delete_hack_nonexistent(self):
        """Test deleting non-existent hack"""
        success = self.hdm.delete_hack("99999")
        self.assertFalse(success)
    
    def test_combined_filters(self):
        """Test applying multiple filters together"""
        # Should work with method chaining or combined calls
        hacks = self.hdm.get_all_hacks()
        filtered = self.hdm.filter_by_type(["kaizo"])
        filtered = self.hdm.filter_by_difficulty(["Expert"], filtered)
        
        self.assertEqual(len(filtered), 1)
        hack = filtered[0]
        self.assertIn("kaizo", hack['hack_types'])
        self.assertEqual(hack['current_difficulty'], "Expert")
    
    def test_data_persistence(self):
        """Test that changes persist to disk"""
        hack_id = "12345"
        
        # Update hack
        self.hdm.update_hack(hack_id, {"personal_rating": 3})
        
        # Create new instance and verify persistence
        new_hdm = HackDataManager(self.data_manager.processed_file)
        updated_hack = new_hdm.get_hack_by_id(hack_id)
        self.assertEqual(updated_hack['personal_rating'], 3)
    
    def test_malformed_data_handling(self):
        """Test handling of malformed data in processed.json"""
        # Create malformed data
        malformed_data = {
            "12345": "not_a_dict",  # Invalid format
            "67890": {
                "title": "Valid Hack",
                # Missing required fields
            },
            "invalid_key": None
        }
        
        with open(self.data_manager.processed_file, 'w') as f:
            json.dump(malformed_data, f)
        
        # Should handle gracefully
        hdm = HackDataManager(self.data_manager.processed_file)
        result = hdm.get_all_hacks()
        
        # Should filter out malformed entries
        self.assertIsInstance(result, list)

if __name__ == '__main__':
    unittest.main()
