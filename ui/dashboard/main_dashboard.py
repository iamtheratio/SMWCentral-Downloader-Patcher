"""
Simplified Dashboard Page
Main dashboard controller with proper scrolling and modular design
"""
import tkinter as tk
from tkinter import ttk
import sys
import os
import platform

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
        self.data_manager = HackDataManager(logger=logger)
        self.analytics = DashboardAnalytics(self.data_manager)
        self.analytics_data = {}
        self.date_filter = "last_week"
        
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
        
        # Ensure we start at the top after everything is loaded
        self.frame.after(100, lambda: self.canvas.yview_moveto(0))
        
        return self.frame
    
    def _create_scrollable_container(self):
        """Create properly working scrollable container"""
        # Create canvas and scrollbar
        self.canvas = tk.Canvas(self.frame, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.frame, orient="vertical", command=self.canvas.yview)
        
        # Create scrollable frame
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        # Configure scrolling - simplified and working
        def on_frame_configure(event):
            # Update scroll region when frame contents change
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        
        def on_canvas_configure(event):
            # Update the scrollable frame width to match canvas width
            canvas_width = event.width
            self.canvas.itemconfig(self.canvas_window, width=canvas_width)
        
        # Bind events
        self.scrollable_frame.bind("<Configure>", on_frame_configure)
        self.canvas.bind("<Configure>", on_canvas_configure)
        
        # Create window in canvas
        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        
        # Configure canvas scrolling
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Mouse wheel scrolling - different approach for macOS trackpad
        def _on_mousewheel(event):
            """Handle mouse wheel scrolling"""
            if platform.system() == "Darwin":  # macOS
                # Try different approaches for macOS
                delta = event.delta
                self.canvas.yview_scroll(-delta, "units")
            else:  # Windows/Linux
                self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        def _on_trackpad(event):
            """Alternative trackpad handler for macOS"""
            self.canvas.yview_scroll(-1 if event.delta > 0 else 1, "units")
        
        # Try multiple binding approaches for macOS trackpad
        widgets_to_bind = [self.canvas, self.scrollable_frame, self.frame, self.parent_frame]
        
        for widget in widgets_to_bind:
            # Standard mouse wheel
            widget.bind("<MouseWheel>", _on_mousewheel)
            
            # macOS specific bindings
            if platform.system() == "Darwin":
                # Try different event types for macOS trackpad
                widget.bind("<Button-4>", lambda e: self.canvas.yview_scroll(-1, "units"))
                widget.bind("<Button-5>", lambda e: self.canvas.yview_scroll(1, "units"))
                # Additional macOS trackpad events
                try:
                    widget.bind("<Shift-MouseWheel>", _on_trackpad)
                    widget.bind("<Control-MouseWheel>", _on_mousewheel)
                except:
                    pass
            
            # Ensure widget can receive events
            try:
                widget.bind("<Button-1>", lambda e, w=widget: w.focus_set())
                widget.bind("<Enter>", lambda e, w=widget: w.focus_set())
            except:
                pass
        
        # Make sure canvas is focused and can scroll
        self.canvas.focus_set()
        self.canvas.configure(takefocus=True)
        
        # Pack canvas and scrollbar
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # Focus the frame so it can receive mouse wheel events
        self.frame.focus_set()
    
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
    
    def _refresh_dashboard(self):
        """Refresh dashboard data and UI"""
        if self.logger:
            self.logger.log("Refreshing dashboard data...", level="info")
        
        # Reload data
        self.data_manager = HackDataManager(logger=self.logger)
        self.analytics = DashboardAnalytics(self.data_manager)
        self._load_analytics_data()
        
        # Clear and recreate content
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        self._create_dashboard_content()
        
        # Update scroll region and reset position
        self.scrollable_frame.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self.canvas.yview_moveto(0)
        
        # Re-bind mouse wheel to all new content
        if hasattr(self, '_bind_mousewheel_recursive'):
            self._bind_mousewheel_recursive()
        
        if self.logger:
            self.logger.log("Dashboard refreshed successfully!", level="info")
    
    def _apply_date_filter(self, filter_value):
        """Apply date filter and refresh"""
        self.date_filter = filter_value
        self._refresh_dashboard()
    
    def cleanup(self):
        """Cleanup method for when switching pages"""
        # Unbind mouse wheel from all widgets
        def unbind_recursive(widget):
            try:
                widget.unbind("<MouseWheel>")
                for child in widget.winfo_children():
                    unbind_recursive(child)
            except tk.TclError:
                pass
        
        if self.frame:
            unbind_recursive(self.frame)
        if self.canvas:
            self.canvas.unbind("<MouseWheel>")
        if self.scrollable_frame:
            unbind_recursive(self.scrollable_frame)

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
        canvas.bind("<MouseWheel>", _on_mousewheel)
    
    def unbind_mousewheel(event):
        canvas.unbind("<MouseWheel>")
    
    canvas.bind('<Enter>', bind_mousewheel)
    canvas.bind('<Leave>', unbind_mousewheel)
    
    # Pack
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    
    return scrollable_frame, canvas
