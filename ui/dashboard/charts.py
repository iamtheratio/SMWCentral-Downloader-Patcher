"""
Dashboard Charts - Visual Analytics Components
Handles all chart creation and data visualization
"""
import tkinter as tk
from tkinter import ttk
import sys
import os

# Add path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from colors import get_colors
from ui_constants import get_dashboard_content_padding, get_labelframe_padding, SECTION_PADDING_Y

class DashboardCharts:
    def __init__(self, parent, analytics_data):
        self.parent = parent
        self.analytics_data = analytics_data
    
    def create_charts_section(self):
        """Create the main charts section"""
        content_padding_x, _ = get_dashboard_content_padding()
        
        charts_frame = ttk.LabelFrame(self.parent, text="Detailed Analytics", padding=get_labelframe_padding())
        charts_frame.pack(fill="x", padx=content_padding_x, pady=(SECTION_PADDING_Y, 15))
        
        # Two column layout - only showing Type and Difficulty charts
        charts_container = ttk.Frame(charts_frame)
        charts_container.pack(fill="x", expand=True)
        
        charts_container.columnconfigure(0, weight=1)
        charts_container.columnconfigure(1, weight=1)
        
        # Configure frame for charts
        charts_container.rowconfigure(0, weight=1)
        
        # Create only Type and Difficulty charts (removed Special and Rating as requested)
        self._create_type_chart(charts_container, 0, 0)
        self._create_difficulty_chart(charts_container, 0, 1)
        
        return charts_frame
    
    def _create_type_chart(self, parent, row, col):
        """Create completion by type chart"""
        colors = get_colors()
        chart_frame = ttk.LabelFrame(parent, text="🎮 Completion by Type", padding=get_labelframe_padding())
        chart_frame.grid(row=row, column=col, padx=(0, 5), pady=2, sticky="nsew")
        
        parent.rowconfigure(row, weight=1)
        parent.columnconfigure(col, weight=1)
        
        completion_data = self.analytics_data.get('completion_by_type', {})
        
        if not completion_data:
            ttk.Label(chart_frame, text="No data available").pack()
            return
        
        # Capitalize hack type names for display
        for hack_type, data in sorted(completion_data.items()):
            if data['total'] > 0:
                display_name = hack_type.title() if hack_type != 'kaizo' else 'Kaizo'
                self._create_progress_bar(chart_frame, display_name, data, colors)
    
    def _create_difficulty_chart(self, parent, row, col):
        """Create completion by difficulty chart"""
        colors = get_colors()
        chart_frame = ttk.LabelFrame(parent, text="📊 Completion by Difficulty", padding=get_labelframe_padding())
        chart_frame.grid(row=row, column=col, padx=(5, 0), pady=2, sticky="nsew")
        
        parent.rowconfigure(row, weight=1)
        parent.columnconfigure(col, weight=1)
        
        completion_data = self.analytics_data.get('completion_by_difficulty', {})
        
        if not completion_data:
            ttk.Label(chart_frame, text="No data available").pack()
            return
        
        # Sort by difficulty order (easiest to hardest)
        difficulty_order = ['Newcomer', 'Casual', 'Skilled', 'Advanced', 'Expert', 'Master', 'Grandmaster']
        sorted_difficulties = [d for d in difficulty_order if d in completion_data]
        # Add any remaining difficulties not in the standard order
        remaining = [d for d in completion_data.keys() if d not in difficulty_order]
        sorted_difficulties.extend(remaining)
        
        for difficulty in sorted_difficulties:
            data = completion_data[difficulty]
            if data['total'] > 0:
                self._create_progress_bar(chart_frame, difficulty, data, colors)
    
    def _create_special_chart(self, parent, row, col):
        """Create special completions chart - Removing as requested"""
        # User requested to remove this widget as it's not working accurately
        return
    
    def _create_rating_chart(self, parent, row, col):
        """Create rating distribution chart - Removing as requested"""
        # User requested to remove this widget as it's not working accurately
        return
        
        total_ratings = sum(rating_data.values())
        
        for rating in range(5, 0, -1):
            count = rating_data.get(rating, 0)
            if count > 0 or rating >= 4:
                percentage = (count / total_ratings) * 100 if total_ratings > 0 else 0
                
                bar_frame = tk.Frame(chart_frame)
                bar_frame.pack(fill="x", pady=2)
                
                stars = "⭐" * rating
                label = tk.Label(
                    bar_frame,
                    text=f"{stars}: {count}",
                    font=("Segoe UI", 9),
                    fg=colors.get("text"),
                    width=15,
                    anchor="w"
                )
                label.pack(side="left")
                
                if percentage > 0:
                    self._create_simple_progress_bar(bar_frame, percentage, colors)
    
    def _create_progress_bar(self, parent, label_text, data, colors):
        """Create a progress bar for completion data"""
        completion_rate = (data['completed'] / data['total']) * 100
        
        bar_frame = tk.Frame(parent)
        bar_frame.pack(fill="x", pady=3)
        
        # Label
        label_text_full = f"{label_text}: {data['completed']}/{data['total']} ({completion_rate:.0f}%)"
        label = tk.Label(
            bar_frame,
            text=label_text_full,
            font=("Segoe UI", 9),
            fg=colors.get("text"),
            width=28,
            anchor="w"
        )
        label.pack(side="left")
        
        # Progress bar
        if completion_rate > 0:
            self._create_simple_progress_bar(bar_frame, completion_rate, colors)
    
    def _create_simple_progress_bar(self, parent, percentage, colors):
        """Create a simple visual progress bar"""
        progress_frame = tk.Frame(parent)
        progress_frame.pack(side="left", fill="x", expand=True, padx=(5, 0))
        
        progress_bg = tk.Frame(
            progress_frame, 
            bg=colors.get("progress_bg"),
            height=20,
            relief="flat",
            bd=0
        )
        progress_bg.pack(fill="x")
        
        if percentage > 0:
            progress_fill = tk.Frame(
                progress_bg,
                bg=colors.get("accent"),
                height=20
            )
            progress_fill.place(x=0, y=0, relwidth=min(percentage/100, 1), relheight=1)
