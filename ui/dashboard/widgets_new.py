"""
Dashboard Widgets - Main Metrics and Charts
Core visual components for the dashboard
"""
import tkinter as tk
from tkinter import ttk
import sys
import os

# Add path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from colors import get_colors
from ui_constants import get_dashboard_content_padding, SECTION_PADDING_Y

class DashboardMetrics:
    def __init__(self, parent, analytics_data, dashboard_ref=None):
        self.parent = parent
        self.analytics_data = analytics_data
        self.dashboard_ref = dashboard_ref  # Reference to main dashboard for refresh/filter
        
    def create_filter_section(self):
        """Create time period filter controls"""
        colors = get_colors()
        content_padding_x, content_padding_y = get_dashboard_content_padding()
        
        filter_frame = ttk.LabelFrame(self.parent, text="Time Period", padding=10)
        filter_frame.pack(fill="x", padx=content_padding_x, pady=content_padding_y)
        
        main_container = ttk.Frame(filter_frame)
        main_container.pack(fill="x")
        
        filter_container = ttk.Frame(main_container)
        filter_container.pack(side="left", fill="x", expand=True)
        
        filters = [
            ("Last Week", "last_week"),
            ("Last Month", "last_month"), 
            ("3 Months", "3_months"),
            ("6 Months", "6_months"),
            ("1 Year", "1_year"),
            ("All Time", "all_time")
        ]
        
        for i, (label, value) in enumerate(filters):
            btn = ttk.Button(
                filter_container,
                text=label,
                command=lambda v=value: self._apply_filter(v)
            )
            btn.pack(side="left", padx=2)
            
            if value == "all_time":
                btn.configure(style="Accent.TButton")
        
        refresh_btn = ttk.Button(
            main_container,
            text="🔄 Refresh",
            command=self._refresh_dashboard
        )
        refresh_btn.pack(side="right", padx=(10, 0))
        
        return filter_frame
    
    def create_main_metrics(self):
        """Create main metrics display"""
        colors = get_colors()
        content_padding_x, _ = get_dashboard_content_padding()
        
        main_container = tk.Frame(self.parent)
        main_container.pack(fill="x", padx=content_padding_x, pady=(SECTION_PADDING_Y, 15))
        
        # Left side - metrics
        metrics_container = tk.Frame(main_container)
        metrics_container.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        # Right side - completion circle
        circle_container = tk.Frame(main_container, width=280)
        circle_container.pack(side="right", fill="y")
        circle_container.pack_propagate(False)
        
        # Create metrics grid
        self._create_metrics_grid(metrics_container)
        self._create_completion_circle(circle_container)
        
        return main_container
    
    def _create_metrics_grid(self, parent):
        """Create the metrics grid layout"""
        colors = get_colors()
        
        # Top row
        top_row = tk.Frame(parent)
        top_row.pack(fill="x", pady=(0, 10))
        
        # Bottom row
        bottom_row = tk.Frame(parent)
        bottom_row.pack(fill="x", pady=(0, 5))
        
        # Configure column weights
        for i in range(3):
            top_row.columnconfigure(i, weight=1, uniform="metrics")
            bottom_row.columnconfigure(i, weight=1, uniform="metrics")
        
        # Top row metrics
        self._create_metric_card(
            top_row, "TOTAL HACKS", 
            str(self.analytics_data.get('total_hacks', 0)),
            "📦", colors.get("text"), 0, 0
        )
        
        self._create_metric_card(
            top_row, "COMPLETED", 
            str(self.analytics_data.get('completed_hacks', 0)),
            "✅", colors.get("text"), 0, 1
        )
        
        recent_count = len(self.analytics_data.get('recent_completions', []))
        self._create_metric_card(
            top_row, "LAST 30 DAYS", 
            str(recent_count),
            "🔥", colors.get("text"), 0, 2
        )
        
        # Bottom row metrics
        avg_rating = self.analytics_data.get('average_rating', 0.0)
        self._create_metric_card(
            bottom_row, "AVG RATING", 
            f"{avg_rating:.1f}⭐" if avg_rating > 0 else "N/A",
            "⭐", colors.get("text"), 0, 0
        )
        
        avg_time_per_hack = self.analytics_data.get('avg_time_per_hack', 0.0)
        self._create_metric_card(
            bottom_row, "AVG TIME PER HACK", 
            f"{avg_time_per_hack:.1f}h" if avg_time_per_hack > 0 else "N/A",
            "⏱️", colors.get("text"), 0, 1
        )
        
        avg_time_per_exit = self.analytics_data.get('avg_time_per_exit', 0.0)
        self._create_metric_card(
            bottom_row, "AVG TIME PER EXIT",
            f"{avg_time_per_exit:.2f}h" if avg_time_per_exit > 0 else "N/A",
            "🚪", colors.get("text"), 0, 2
        )
    
    def _create_metric_card(self, parent, title, value, icon, color, row, col):
        """Create a single metric card"""
        colors = get_colors()
        
        card_frame = tk.Frame(parent)
        card_frame.grid(row=row, column=col, padx=10, pady=5, sticky="ew")
        
        # Large value
        value_label = tk.Label(
            card_frame,
            text=value,
            font=("Segoe UI", 44, "bold"),
            fg=color,
            bg=parent.cget("bg")
        )
        value_label.pack(pady=(0, 5))
        
        # Title
        title_label = tk.Label(
            card_frame,
            text=title,
            font=("Segoe UI", 10, "bold"),
            fg=colors.get("text_secondary"),
            bg=parent.cget("bg")
        )
        title_label.pack()
    
    def _create_completion_circle(self, parent):
        """Create completion rate circle widget"""
        colors = get_colors()
        
        circle_bg_frame = tk.Frame(parent, bg=colors.get("card_bg"))
        circle_bg_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Title
        title_label = tk.Label(
            circle_bg_frame,
            text="COMPLETION RATE",
            font=("Segoe UI", 14, "bold"),
            fg=colors.get("text_secondary"),
            bg=colors.get("card_bg")
        )
        title_label.pack(pady=(10, 10))
        
        # Canvas for circle
        canvas_size = 180
        canvas = tk.Canvas(
            circle_bg_frame, 
            width=canvas_size, 
            height=canvas_size,
            highlightthickness=0,
            relief='flat',
            borderwidth=0,
            bg=colors.get("card_bg")
        )
        canvas.pack(pady=(0, 10))
        
        # Draw circle
        self._draw_completion_circle(canvas, canvas_size)
        
        # Stats below circle
        completed = self.analytics_data.get('completed_hacks', 0)
        total = self.analytics_data.get('total_hacks', 0)
        
        count_label = tk.Label(
            circle_bg_frame,
            text=f"{completed} / {total}",
            font=("Segoe UI", 13),
            fg=colors.get("text_secondary"),
            bg=colors.get("card_bg")
        )
        count_label.pack(pady=(5, 15))
    
    def _draw_completion_circle(self, canvas, size):
        """Draw the completion rate circle"""
        colors = get_colors()
        center = size // 2
        radius = size // 2 - 20
        
        completion_rate = self.analytics_data.get('completion_rate', 0.0)
        completion_decimal = completion_rate / 100
        
        canvas.configure(bg=colors.get("chart_bg"))
        
        # Background circle
        canvas.create_oval(
            center - radius, center - radius,
            center + radius, center + radius,
            fill=colors.get("progress_bg"),
            outline=""
        )
        
        # Progress arc
        if completion_decimal > 0:
            extent = 360 * completion_decimal
            canvas.create_arc(
                center - radius, center - radius,
                center + radius, center + radius,
                start=90, extent=-extent,
                fill=colors.get("accent"),
                outline=""
            )
        
        # Inner circle
        inner_radius = radius - 30
        canvas.create_oval(
            center - inner_radius, center - inner_radius,
            center + inner_radius, center + inner_radius,
            fill=colors.get("chart_bg"),
            outline=""
        )
        
        # Percentage text
        canvas.create_text(
            center, center,
            text=f"{completion_rate:.1f}%",
            font=("Segoe UI", 24, "bold"),
            fill=colors.get("text"),
            anchor="center"
        )
    
    def _apply_filter(self, filter_value):
        """Apply date filter"""
        if self.dashboard_ref and hasattr(self.dashboard_ref, '_apply_date_filter'):
            self.dashboard_ref._apply_date_filter(filter_value)
    
    def _refresh_dashboard(self):
        """Refresh dashboard data"""
        if self.dashboard_ref and hasattr(self.dashboard_ref, '_refresh_dashboard'):
            self.dashboard_ref._refresh_dashboard()
