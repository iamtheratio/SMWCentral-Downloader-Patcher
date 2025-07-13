"""
Simplified Dashboard Page
Main dashboard controller with proper scrolling and modular design
"""
import tkinter as tk
from tkinter import ttk
import sys
import os

# Add paths for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from hack_data_manager import HackDataManager
from colors import get_colors
from ui_constants import get_page_padding
from .analytics import DashboardAnalytics
from .widgets import DashboardMetrics
from .charts import DashboardCharts

class DashboardPage:
    """Simplified dashboard page with proper scrolling"""
    
    def __init__(self, parent_frame, logger=None):
        self.parent_frame = parent_frame
        self.logger = logger
        self.frame = None
        self.data_manager = HackDataManager()
        self.analytics = DashboardAnalytics(self.data_manager)
        self.analytics_data = {}
        self.date_filter = "all_time"
        
        # Scrolling components
        self.canvas = None
        self.scrollable_frame = None
        self.scrollbar = None
        
    def create(self):
        """Create the dashboard page UI with proper scrolling"""
        # Main frame with standardized padding
        self.frame = ttk.Frame(self.parent_frame, padding=get_page_padding())
        
        # Create scrollable container
        self._create_scrollable_container()
        
        # Load data and create content
        self._load_analytics_data()
        self._create_dashboard_content()
        
        return self.frame
    
    def _create_scrollable_container(self):
        """Create properly working scrollable container"""
        # Create canvas and scrollbar
        self.canvas = tk.Canvas(self.frame, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.frame, orient="vertical", command=self.canvas.yview)
        
        # Create scrollable frame
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        # Configure scrolling
        def configure_scrollable_frame(event):
            # Update scroll region and ensure proper bounds
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
            # Prevent scrolling above content
            self.canvas.yview_moveto(0)
        
        self.scrollable_frame.bind("<Configure>", configure_scrollable_frame)
        
        # Create window in canvas
        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        
        # Configure canvas scrolling
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Bind canvas width to scrollable frame width
        def configure_canvas_width(event):
            canvas_width = event.width
            self.canvas.itemconfig(self.canvas_window, width=canvas_width)
            # Also update scroll region when canvas resizes
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        
        self.canvas.bind('<Configure>', configure_canvas_width)
        
        # Mouse wheel scrolling with bounds checking
        def _on_mousewheel(event):
            # Check if we can scroll in the requested direction
            if event.delta > 0:  # Scrolling up
                # Don't allow scrolling above the top
                if self.canvas.canvasy(0) <= 0:
                    return
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        def bind_mousewheel(event):
            self.canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        def unbind_mousewheel(event):
            self.canvas.unbind_all("<MouseWheel>")
        
        self.canvas.bind('<Enter>', bind_mousewheel)
        self.canvas.bind('<Leave>', unbind_mousewheel)
        
        # Pack canvas and scrollbar
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # Initialize scroll position to top
        self.canvas.update_idletasks()
        self.canvas.yview_moveto(0)
    
    def _load_analytics_data(self):
        """Load analytics data using the analytics module"""
        self.analytics_data = self.analytics.load_analytics_data(self.date_filter)
        
        if self.logger:
            self.logger.log(f"Dashboard loaded: {self.analytics_data['completed_hacks']} completed hacks", level="info")
    
    def _create_dashboard_content(self):
        """Create all dashboard content sections"""
        # Initialize component classes with dashboard reference and current filter
        metrics = DashboardMetrics(self.scrollable_frame, self.analytics_data, self)
        # Set the current filter on the metrics instance
        metrics.current_filter = self.date_filter
        charts = DashboardCharts(self.scrollable_frame, self.analytics_data)
        
        # Create sections with proper spacing
        metrics.create_filter_section()
        metrics.create_main_metrics()
        charts.create_charts_section()
        
        # Add some bottom padding
        bottom_padding = tk.Frame(self.scrollable_frame, height=50)
        bottom_padding.pack(fill="x")
        
        # Ensure scroll region is properly set after content creation
        self.scrollable_frame.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self.canvas.yview_moveto(0)  # Ensure we start at the top
    
    def _refresh_dashboard(self):
        """Refresh dashboard data and UI"""
        if self.logger:
            self.logger.log("Refreshing dashboard data...", level="info")
        
        # Reload data
        self.data_manager = HackDataManager()
        self.analytics = DashboardAnalytics(self.data_manager)
        self._load_analytics_data()
        
        # Clear and recreate content
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        self._create_dashboard_content()
        
        # Reset scroll position to top and update scroll region
        self.canvas.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self.canvas.yview_moveto(0)
        
        if self.logger:
            self.logger.log("Dashboard refreshed successfully!", level="info")
    
    def _apply_date_filter(self, filter_value):
        """Apply date filter and refresh"""
        self.date_filter = filter_value
        self._refresh_dashboard()
    
    def cleanup(self):
        """Cleanup method for when switching pages"""
        if self.canvas:
            self.canvas.unbind_all("<MouseWheel>")

# Create a simple scrollable frame for testing
def create_scrollable_frame(parent):
    """Utility function to create a properly working scrollable frame"""
    # Canvas and scrollbar
    canvas = tk.Canvas(parent, highlightthickness=0)
    scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas)
    
    # Configure scrolling
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    
    canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    
    # Bind canvas width
    def configure_canvas_width(event):
        canvas_width = event.width
        canvas.itemconfig(canvas_window, width=canvas_width)
    
    canvas.bind('<Configure>', configure_canvas_width)
    
    # Mouse wheel
    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    def bind_mousewheel(event):
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
    
    def unbind_mousewheel(event):
        canvas.unbind_all("<MouseWheel>")
    
    canvas.bind('<Enter>', bind_mousewheel)
    canvas.bind('<Leave>', unbind_mousewheel)
    
    # Pack
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    
    return scrollable_frame, canvas
