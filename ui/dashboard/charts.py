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
        
        # Two column layout
        charts_container = ttk.Frame(charts_frame)
        charts_container.pack(fill="x", expand=True)
        
        charts_container.columnconfigure(0, weight=1)
        charts_container.columnconfigure(1, weight=1)
        
        # Column frames
        col1_frame = ttk.Frame(charts_container)
        col1_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        
        col2_frame = ttk.Frame(charts_container)
        col2_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        
        # Configure row weights
        col1_frame.rowconfigure(0, weight=1)
        col1_frame.rowconfigure(1, weight=1)
        col2_frame.rowconfigure(0, weight=1)
        col2_frame.rowconfigure(1, weight=1)
        
        # Create charts
        self._create_type_chart(col1_frame, 0, 0)
        self._create_difficulty_chart(col1_frame, 1, 0)
        self._create_special_chart(col2_frame, 0, 0)
        self._create_rating_chart(col2_frame, 1, 0)
        
        return charts_frame
    
    def _create_type_chart(self, parent, row, col):
        """Create completion by type chart"""
        colors = get_colors()
        chart_frame = ttk.LabelFrame(parent, text="🎮 Completion by Type", padding=8)
        chart_frame.grid(row=row, column=col, padx=2, pady=2, sticky="nsew")
        
        parent.rowconfigure(row, weight=1)
        parent.columnconfigure(col, weight=1)
        
        completion_data = self.analytics_data.get('completion_by_type', {})
        
        if not completion_data:
            ttk.Label(chart_frame, text="No data available").pack()
            return
        
        for hack_type, data in sorted(completion_data.items()):
            if data['total'] > 0:
                self._create_progress_bar(chart_frame, hack_type.title(), data, colors)
    
    def _create_difficulty_chart(self, parent, row, col):
        """Create completion by difficulty chart"""
        colors = get_colors()
        chart_frame = ttk.LabelFrame(parent, text="📊 Completion by Difficulty", padding=8)
        chart_frame.grid(row=row, column=col, padx=2, pady=2, sticky="nsew")
        
        parent.rowconfigure(row, weight=1)
        parent.columnconfigure(col, weight=1)
        
        completion_data = self.analytics_data.get('completion_by_difficulty', {})
        
        if not completion_data:
            ttk.Label(chart_frame, text="No data available").pack()
            return
        
        # Sort by difficulty order
        difficulty_order = ['Easy', 'Normal', 'Hard', 'Very Hard', 'Expert', 'Kaizo Light', 'Kaizo', 'Grandmaster']
        sorted_difficulties = [d for d in difficulty_order if d in completion_data]
        
        for difficulty in sorted_difficulties:
            data = completion_data[difficulty]
            if data['total'] > 0:
                self._create_progress_bar(chart_frame, difficulty, data, colors)
    
    def _create_special_chart(self, parent, row, col):
        """Create special completions chart"""
        colors = get_colors()
        chart_frame = ttk.LabelFrame(parent, text="🏆 Special Completions", padding=8)
        chart_frame.grid(row=row, column=col, padx=2, pady=2, sticky="nsew")
        
        parent.rowconfigure(row, weight=1)
        parent.columnconfigure(col, weight=1)
        
        # Simple placeholder for special categories
        special_categories = ['Hall of Fame: 0', 'SA-1: 0', 'Collaboration: 0', 'Demo: 0']
        
        for category in special_categories:
            label = tk.Label(
                chart_frame,
                text=category,
                font=("Segoe UI", 10),
                fg=colors.get("text"),
                anchor="w"
            )
            label.pack(fill="x", pady=3)
    
    def _create_rating_chart(self, parent, row, col):
        """Create rating distribution chart"""
        colors = get_colors()
        chart_frame = ttk.LabelFrame(parent, text="⭐ Rating Distribution", padding=8)
        chart_frame.grid(row=row, column=col, padx=2, pady=2, sticky="nsew")
        
        parent.rowconfigure(row, weight=1)
        parent.columnconfigure(col, weight=1)
        
        rating_data = self.analytics_data.get('rating_distribution', {})
        
        if not rating_data:
            ttk.Label(chart_frame, text="No ratings given yet").pack()
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
