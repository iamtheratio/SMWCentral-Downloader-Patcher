"""
Dashboard page for SMWCentral Downloader & Patcher
SIMPLIFIED VERSION - Uses modular dashboard components
"""
import sys
import os

# Add paths for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# Import the new modular dashboard
from ui.dashboard.main_dashboard import DashboardPage as ModularDashboard

class DashboardPage:
    """Wrapper for the new modular dashboard system"""
    
    def __init__(self, parent_frame, logger=None):
        self.modular_dashboard = ModularDashboard(parent_frame, logger)
        # Keep reference for theme refresh compatibility
        self.parent_frame = parent_frame
        self.logger = logger
        self.frame = None
        
    def create(self):
        """Create the dashboard page"""
        self.frame = self.modular_dashboard.create()
        return self.frame
    
    def _refresh_dashboard(self):
        """Refresh dashboard - compatibility method"""
        if hasattr(self.modular_dashboard, '_refresh_dashboard'):
            self.modular_dashboard._refresh_dashboard()
    
    def cleanup(self):
        """Cleanup when switching pages"""
        if hasattr(self.modular_dashboard, 'cleanup'):
            self.modular_dashboard.cleanup()
