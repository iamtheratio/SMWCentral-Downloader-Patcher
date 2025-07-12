import tkinter as tk
from tkinter import ttk
from .navigation import NavigationBar
from .page_manager import PageManager
from .theme_controls import ThemeControls
from .version_display import VersionDisplay
from .pages import DashboardPage, BulkDownloadPage, HackHistoryPage

class MainLayout:
    """Main UI layout manager - now simplified and modular"""
    
    def __init__(self, root, run_pipeline_func, toggle_theme_callback, 
                 setup_section, filter_section, difficulty_section, logger, version=None):
        self.root = root
        self.run_pipeline_func = run_pipeline_func
        self.toggle_theme_callback = toggle_theme_callback
        self.setup_section = setup_section
        self.filter_section = filter_section
        self.difficulty_section = difficulty_section
        self.logger = logger
        self.version = version
        
        # UI Components
        self.content_frame = None
        self.page_manager = None
        self.navigation = None
        self.theme_controls = None
        self.version_display = None
        
        # Pages
        self.dashboard_page = None
        self.bulk_download_page = None
        self.hack_history_page = None
    
    def create(self):
        """Create the main UI layout"""
        # Create content frame first
        self.content_frame = ttk.Frame(self.root)
        
        # Initialize page manager
        self.page_manager = PageManager(self.content_frame)
        
        # Create navigation bar
        self.navigation = NavigationBar(self.root, self.page_manager, self.toggle_theme_callback)
        self.navigation.create()
        
        # Store navigation reference for theme updates
        self.root.navigation = self.navigation
        
        # Pack content frame after navigation
        self.content_frame.pack(fill="both", expand=True)
        
        # Create pages
        self._create_pages()
        
        # Create version display
        self.version_display = VersionDisplay(self.root, self.version)
        self.version_display.create()
        
        # Show default page - CHANGED to Dashboard
        self.navigation.show_page("Dashboard")
        
        # Force refresh navigation
        self.root.after(100, lambda: self.navigation.show_page("Dashboard"))
        
        return self.content_frame
    
    def _create_pages(self):
        """Create and register all pages"""
        # Create dashboard page - NEW DEFAULT PAGE
        self.dashboard_page = DashboardPage(self.content_frame, self.logger)
        dashboard_frame = self.dashboard_page.create()
        self.page_manager.add_page("Dashboard", dashboard_frame)
        
        # Create bulk download page
        self.bulk_download_page = BulkDownloadPage(
            self.content_frame,
            self.run_pipeline_func,
            self.setup_section,
            self.filter_section,
            self.difficulty_section,
            self.logger
        )
        bulk_frame = self.bulk_download_page.create()
        self.page_manager.add_page("Bulk Download", bulk_frame)
        
        # Store log_text reference for theme toggling
        if hasattr(self.bulk_download_page, 'frame') and hasattr(self.logger, 'log_text'):
            self.root.log_text = self.logger.log_text
        
        # Create hack history page - PASS LOGGER for centralized logging
        self.hack_history_page = HackHistoryPage(self.content_frame, self.logger)
        history_frame = self.hack_history_page.create()
        self.page_manager.add_page("Hack History", history_frame)
    
    def get_download_button(self):
        """Return the download button reference"""
        if self.bulk_download_page:
            return self.bulk_download_page.get_download_button()
        return None