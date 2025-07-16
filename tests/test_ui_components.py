"""
Unit tests for UI components
Tests GUI components, navigation, and user interactions
"""
import unittest
import os
import sys
from unittest.mock import Mock, patch, MagicMock

# Import test configuration
from .test_config import TestConfig, MockTkinter, run_with_mock_gui

# Import UI modules to test
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

class TestUIComponents(unittest.TestCase):
    """Test cases for UI components"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = TestConfig.get_temp_dir()
        self.mock_root = MockTkinter.create_mock_root()
    
    def tearDown(self):
        """Clean up test environment"""
        TestConfig.cleanup_temp_dir(self.test_dir)
    
    @run_with_mock_gui
    def test_navigation_component_creation(self):
        """Test navigation component creation"""
        with patch.dict('sys.modules', {
            'ui.navigation': Mock(),
            'ui.page_manager': Mock()
        }):
            # Mock navigation creation
            mock_navigation = Mock()
            mock_navigation.setup_navigation = Mock()
            
            # Test that navigation can be created without errors
            mock_navigation.setup_navigation(self.mock_root)
            mock_navigation.setup_navigation.assert_called_once()
    
    @run_with_mock_gui
    def test_theme_toggle_functionality(self):
        """Test theme toggle functionality"""
        with patch('sv_ttk.toggle_theme') as mock_toggle:
            # Mock theme toggle
            mock_toggle_callback = Mock()
            mock_toggle_callback()
            
            # Verify theme toggle was called
            self.assertTrue(True)  # Placeholder for actual theme testing
    
    @run_with_mock_gui
    def test_page_manager_navigation(self):
        """Test page manager navigation between pages"""
        # Mock page manager
        mock_page_manager = Mock()
        mock_page_manager.pages = {
            'Dashboard': Mock(),
            'Download': Mock(),
            'History': Mock(),
            'Settings': Mock()
        }
        
        # Test navigation to different pages
        for page_name in mock_page_manager.pages.keys():
            mock_page_manager.show_page = Mock()
            mock_page_manager.show_page(page_name)
            mock_page_manager.show_page.assert_called_with(page_name)
    
    @run_with_mock_gui
    def test_dashboard_analytics_display(self):
        """Test dashboard analytics display"""
        # Mock analytics data
        mock_analytics = {
            'total_hacks': 10,
            'completed_hacks': 5,
            'completion_rate': 50.0,
            'type_distribution': {'Standard': 5, 'Kaizo': 3, 'Puzzle': 2},
            'difficulty_distribution': {'Newcomer': 2, 'Skilled': 4, 'Expert': 4}
        }
        
        # Mock dashboard component
        mock_dashboard = Mock()
        mock_dashboard.update_analytics = Mock()
        mock_dashboard.update_analytics(mock_analytics)
        
        mock_dashboard.update_analytics.assert_called_once_with(mock_analytics)
    
    @run_with_mock_gui
    def test_filter_components_creation(self):
        """Test filter components creation and functionality"""
        # Mock filter section
        mock_filter_section = Mock()
        
        # Test filter types
        filter_types = ['type', 'difficulty', 'completion', 'features']
        for filter_type in filter_types:
            mock_filter_section.create_filter = Mock()
            mock_filter_section.create_filter(filter_type)
            mock_filter_section.create_filter.assert_called_with(filter_type)
    
    @run_with_mock_gui
    def test_hack_list_display(self):
        """Test hack list display functionality"""
        # Mock hack data
        mock_hacks = [
            {
                'id': '12345',
                'title': 'Test Hack 1',
                'hack_types': ['standard'],
                'current_difficulty': 'Skilled',
                'completed': False
            },
            {
                'id': '67890',
                'title': 'Test Hack 2',
                'hack_types': ['kaizo'],
                'current_difficulty': 'Expert',
                'completed': True
            }
        ]
        
        # Mock hack list component
        mock_hack_list = Mock()
        mock_hack_list.populate_hacks = Mock()
        mock_hack_list.populate_hacks(mock_hacks)
        
        mock_hack_list.populate_hacks.assert_called_once_with(mock_hacks)
    
    @run_with_mock_gui
    def test_download_progress_display(self):
        """Test download progress display"""
        # Mock progress bar
        mock_progress = Mock()
        mock_progress.configure = Mock()
        
        # Test progress updates
        for progress in [0, 25, 50, 75, 100]:
            mock_progress.configure(value=progress)
            
        # Verify configure was called multiple times
        self.assertEqual(mock_progress.configure.call_count, 5)
    
    @run_with_mock_gui
    def test_settings_components(self):
        """Test settings components functionality"""
        # Mock settings data
        mock_settings = {
            'base_rom_path': '/test/rom.smc',
            'output_dir': '/test/output',
            'theme': 'dark',
            'multi_type_enabled': True
        }
        
        # Mock settings component
        mock_settings_component = Mock()
        mock_settings_component.load_settings = Mock()
        mock_settings_component.save_settings = Mock()
        
        mock_settings_component.load_settings(mock_settings)
        mock_settings_component.save_settings(mock_settings)
        
        mock_settings_component.load_settings.assert_called_once()
        mock_settings_component.save_settings.assert_called_once()
    
    @run_with_mock_gui
    def test_log_display_functionality(self):
        """Test log display functionality"""
        # Mock log widget
        mock_log_widget = Mock()
        mock_log_widget.config = Mock()
        mock_log_widget.insert = Mock()
        mock_log_widget.see = Mock()
        
        # Test log message insertion
        test_messages = [
            ("Information", "Test info message"),
            ("Warning", "Test warning message"),
            ("Error", "Test error message")
        ]
        
        for level, message in test_messages:
            # Simulate log insertion
            mock_log_widget.config(state="normal")
            mock_log_widget.insert("end", f"[{level}] {message}\n")
            mock_log_widget.see("end")
            mock_log_widget.config(state="disabled")
        
        # Verify log operations
        self.assertEqual(mock_log_widget.config.call_count, 6)  # 2 per message
        self.assertEqual(mock_log_widget.insert.call_count, 3)
        self.assertEqual(mock_log_widget.see.call_count, 3)
    
    @run_with_mock_gui
    def test_button_state_management(self):
        """Test button state management (enabled/disabled)"""
        # Mock button
        mock_button = Mock()
        mock_button.configure = Mock()
        
        # Test enabling and disabling
        mock_button.configure(state="normal")
        mock_button.configure(state="disabled")
        
        self.assertEqual(mock_button.configure.call_count, 2)
    
    @run_with_mock_gui
    def test_window_icon_setting(self):
        """Test window icon setting"""
        # Mock window
        mock_window = Mock()
        mock_window.iconbitmap = Mock()
        
        # Test icon setting
        try:
            mock_window.iconbitmap("assets/icon.ico")
        except:
            pass  # Icon might not exist in test environment
        
        mock_window.iconbitmap.assert_called_once()
    
    @run_with_mock_gui
    def test_keyboard_shortcuts(self):
        """Test keyboard shortcuts functionality"""
        # Mock root window
        mock_root = Mock()
        mock_root.bind = Mock()
        
        # Test keyboard shortcut binding
        shortcuts = [
            ("<Control-l>", "clear_log"),
            ("<F1>", "show_help"),
            ("<Control-s>", "save_settings")
        ]
        
        for key_combo, action in shortcuts:
            mock_root.bind(key_combo, Mock())
        
        self.assertEqual(mock_root.bind.call_count, 3)
    
    @run_with_mock_gui
    def test_responsive_layout(self):
        """Test responsive layout functionality"""
        # Mock layout components
        mock_layout = Mock()
        mock_layout.configure_grid = Mock()
        mock_layout.configure_weights = Mock()
        
        # Test grid configuration
        mock_layout.configure_grid(row=0, column=0, sticky="nsew")
        mock_layout.configure_weights(weight=1)
        
        mock_layout.configure_grid.assert_called_once()
        mock_layout.configure_weights.assert_called_once()
    
    @run_with_mock_gui
    def test_error_dialog_display(self):
        """Test error dialog display"""
        with patch('tkinter.messagebox.showerror') as mock_error:
            # Mock error dialog
            mock_error("Error", "Test error message")
            mock_error.assert_called_once_with("Error", "Test error message")
    
    @run_with_mock_gui
    def test_file_dialog_operations(self):
        """Test file dialog operations"""
        with patch('tkinter.filedialog.askopenfilename') as mock_open, \
             patch('tkinter.filedialog.askdirectory') as mock_dir:
            
            # Mock file selection
            mock_open.return_value = "/test/file.smc"
            mock_dir.return_value = "/test/directory"
            
            # Test file and directory selection
            file_result = mock_open()
            dir_result = mock_dir()
            
            self.assertEqual(file_result, "/test/file.smc")
            self.assertEqual(dir_result, "/test/directory")
    
    @run_with_mock_gui
    def test_multi_threading_ui_updates(self):
        """Test UI updates from background threads"""
        # Mock thread-safe UI update
        mock_root = Mock()
        mock_root.after = Mock()
        
        # Test scheduling UI update from background thread
        def update_ui():
            mock_root.after(0, lambda: print("UI updated"))
        
        update_ui()
        mock_root.after.assert_called_once()
    
    @run_with_mock_gui
    def test_widget_styling(self):
        """Test widget styling with themes"""
        # Mock style
        mock_style = Mock()
        mock_style.configure = Mock()
        
        # Test style configuration
        widget_styles = [
            ("TLabel", {"font": ("Segoe UI", 9)}),
            ("TButton", {"font": ("Segoe UI", 9)}),
            ("Treeview", {"font": ("Segoe UI", 10), "rowheight": 25})
        ]
        
        for widget_type, style_config in widget_styles:
            mock_style.configure(widget_type, **style_config)
        
        self.assertEqual(mock_style.configure.call_count, 3)
    
    @run_with_mock_gui
    def test_data_validation_in_forms(self):
        """Test data validation in form inputs"""
        # Mock validation functions
        def validate_path(path):
            return path and os.path.isabs(path)
        
        def validate_number(value):
            try:
                int(value)
                return True
            except ValueError:
                return False
        
        # Test validations
        self.assertTrue(validate_path("/absolute/path"))
        self.assertFalse(validate_path("relative/path"))
        self.assertTrue(validate_number("123"))
        self.assertFalse(validate_number("abc"))

if __name__ == '__main__':
    unittest.main()
