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
        """Create the main charts section with time progression chart"""
        content_padding_x, _ = get_dashboard_content_padding()
        
        # Single column layout for the larger time progression chart
        charts_container = ttk.Frame(self.parent)
        charts_container.pack(fill="both", expand=True, padx=content_padding_x, pady=(SECTION_PADDING_Y, 15))
        
        # Create time progression chart directly (no nested container)
        self._create_time_progression_chart(charts_container)
        
        return charts_container
    
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
    
    def _create_time_progression_chart(self, parent):
        """Create time progression line chart showing avg completion time by difficulty over 6 months"""
        colors = get_colors()
        
        # Chart container
        chart_frame = ttk.LabelFrame(parent, text="📈 Average Completion Time by Difficulty (Last 6 Months)", 
                                   padding=get_labelframe_padding())
        chart_frame.pack(fill="both", expand=True, pady=5)
        
        # Type filter dropdown
        filter_frame = ttk.Frame(chart_frame)
        filter_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Label(filter_frame, text="Filter by Type:").pack(side="left", padx=(0, 5))
        
        # Get available types
        all_types = set()
        progression_data = self.analytics_data.get('time_progression', {})
        for month_data in progression_data.values():
            for diff_data in month_data.get('difficulties', {}).values():
                all_types.update(diff_data.get('types', []))
        
        # Create display names for types (capitalized) while preserving original values
        type_display_map = {}
        type_value_map = {}  # Reverse mapping from display name to original value
        
        for type_name in sorted(list(all_types)):
            display_name = type_name.capitalize()
            type_display_map[type_name] = display_name
            type_value_map[display_name] = type_name
        
        type_options = ['All Types'] + [type_display_map[t] for t in sorted(list(all_types))]
        type_var = tk.StringVar(value='All Types')
        type_combo = ttk.Combobox(filter_frame, textvariable=type_var, values=type_options, 
                                state="readonly", width=15)
        type_combo.pack(side="left", padx=(0, 10))
        
        # Canvas for the line chart - increased height for legend
        canvas_frame = ttk.Frame(chart_frame)
        canvas_frame.pack(fill="both", expand=True)
        
        canvas = tk.Canvas(canvas_frame, height=520, bg=colors.get("chart_bg"))
        canvas.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Function to update chart based on filter
        def update_chart():
            canvas.delete("all")
            selected_display = type_var.get()
            # Convert display name back to original value for filtering
            if selected_display == 'All Types':
                selected_type = 'All Types'
            else:
                selected_type = type_value_map.get(selected_display, selected_display)
            # Ensure canvas is properly sized before drawing
            canvas.update_idletasks()
            self._draw_time_progression_lines(canvas, selected_type)
        
        # Bind filter change
        type_combo.bind('<<ComboboxSelected>>', lambda e: update_chart())
        
        # Initial chart draw - delay to ensure proper canvas sizing
        canvas.after(50, update_chart)
        
        return chart_frame
    
    def _draw_time_progression_lines(self, canvas, filter_type='All Types'):
        """Draw the actual line chart on the canvas"""
        colors = get_colors()
        progression_data = self.analytics_data.get('time_progression', {})
        
        if not progression_data:
            canvas.create_text(canvas.winfo_width()//2, canvas.winfo_height()//2, 
                             text="No completion data available", 
                             font=("Segoe UI", 12), fill=colors.get("text_secondary"))
            return
        
        # Update canvas after it's been drawn
        canvas.update_idletasks()
        width = canvas.winfo_width()
        height = canvas.winfo_height()
        
        if width <= 1 or height <= 1:
            # Canvas not ready yet, try again with a longer delay
            canvas.after(100, lambda: self._draw_time_progression_lines(canvas, filter_type))
            return
        
        # Ensure minimum width for proper chart display
        if width < 300:
            width = 800  # Use a reasonable default width
        
        # Chart margins - reduced to give more space
        margin_left = 70
        margin_right = 30
        margin_top = 30
        margin_bottom = 160  # Increased from 130 to 160 to accommodate multi-row legend
        chart_width = width - margin_left - margin_right
        chart_height = height - margin_top - margin_bottom
        
        # Get sorted months
        sorted_months = sorted(progression_data.keys())
        if not sorted_months:
            return
        
        # Define difficulty colors and order using theme colors
        difficulty_colors = {
            'Newcomer': colors.get('diff_newcomer'),
            'Casual': colors.get('diff_casual'),        
            'Skilled': colors.get('diff_skilled'),
            'Advanced': colors.get('diff_advanced'),
            'Expert': colors.get('diff_expert'),
            'Master': colors.get('diff_master'),
            'Grandmaster': colors.get('diff_grandmaster')
        }
        
        difficulty_order = ['Newcomer', 'Casual', 'Skilled', 'Advanced', 'Expert', 'Master', 'Grandmaster']
        
        # Extract data for each difficulty
        difficulty_lines = {}
        max_time = 0
        
        for difficulty in difficulty_order:
            times = []
            for month in sorted_months:
                month_data = progression_data[month]['difficulties'].get(difficulty)
                if month_data:
                    # Filter by type if needed
                    if filter_type == 'All Types' or filter_type in month_data.get('types', []):
                        avg_time = month_data['avg_time']
                        times.append(avg_time)
                        max_time = max(max_time, avg_time)
                    else:
                        times.append(None)  # No data for this filter
                else:
                    times.append(None)  # No data for this month
            
            if any(t is not None for t in times):
                difficulty_lines[difficulty] = times
        
        if not difficulty_lines or max_time == 0:
            canvas.create_text(width//2, height//2 - 10, 
                             text=f"No data available for {filter_type}", 
                             font=("Segoe UI", 12), fill=colors.get("text_secondary"))
            canvas.create_text(width//2, height//2 + 15, 
                             text="Enter your Time to Beat in Hack Collection to see stats appear here!", 
                             font=("Segoe UI", 10), fill=colors.get("text_secondary"))
            return
        
        # Draw grid and axes
        # Y-axis (time)
        y_steps = 5
        for i in range(y_steps + 1):
            y_val = (max_time * i) / y_steps
            y_pos = margin_top + chart_height - (i * chart_height / y_steps)
            
            # Grid line
            canvas.create_line(margin_left, y_pos, margin_left + chart_width, y_pos,
                             fill=colors.get("border"), width=1, dash=(2, 2))
            
            # Y-axis label
            canvas.create_text(margin_left - 10, y_pos, text=f"{y_val:.1f}h",
                             font=("Segoe UI", 9), fill=colors.get("text_secondary"), anchor="e")
        
        # X-axis (months)
        x_step = chart_width / max(1, len(sorted_months) - 1) if len(sorted_months) > 1 else chart_width
        for i, month in enumerate(sorted_months):
            x_pos = margin_left + (i * x_step) if len(sorted_months) > 1 else margin_left + chart_width // 2
            
            # Grid line
            canvas.create_line(x_pos, margin_top, x_pos, margin_top + chart_height,
                             fill=colors.get("border"), width=1, dash=(2, 2))
            
            # X-axis label
            month_name = progression_data[month]['month_name']
            canvas.create_text(x_pos, margin_top + chart_height + 20, text=month_name,
                             font=("Segoe UI", 9), fill=colors.get("text_secondary"), anchor="n")
        
        # Draw lines for each difficulty
        for difficulty, times in difficulty_lines.items():
            color = difficulty_colors.get(difficulty, colors.get("accent"))
            points = []
            
            for i, time_val in enumerate(times):
                if time_val is not None:
                    x_pos = margin_left + (i * x_step) if len(sorted_months) > 1 else margin_left + chart_width // 2
                    y_pos = margin_top + chart_height - (time_val * chart_height / max_time)
                    points.append((x_pos, y_pos))
            
            # Draw line segments between valid points
            if len(points) > 1:
                for i in range(len(points) - 1):
                    canvas.create_line(points[i][0], points[i][1], points[i+1][0], points[i+1][1],
                                     fill=color, width=3)
            
            # Draw points
            for x_pos, y_pos in points:
                canvas.create_oval(x_pos-4, y_pos-4, x_pos+4, y_pos+4,
                                 fill=color, outline=colors.get("chart_bg"), width=2)
        
        # Draw horizontal legend below the chart with extra padding
        legend_y = margin_top + chart_height + 80  # Increased from 40 to 60 for better separation
        legend_start_x = margin_left
        
        canvas.create_text(legend_start_x, legend_y, text="Difficulties:", 
                         font=("Segoe UI", 12, "bold"), fill=colors.get("text"), anchor="w")
        
        # Calculate spacing for horizontal layout
        available_width = chart_width
        items_per_row = min(4, len(difficulty_lines))  # Max 4 per row
        item_width = available_width // items_per_row if items_per_row > 0 else available_width
        
        for i, (difficulty, times) in enumerate(difficulty_lines.items()):
            row = i // items_per_row
            col = i % items_per_row
            
            x_offset = legend_start_x + (col * item_width)
            y_offset = legend_y + 25 + (row * 25)
            color = difficulty_colors.get(difficulty, colors.get("accent"))
            
            # Legend bullet point
            canvas.create_text(x_offset, y_offset, text="●", 
                             font=("Segoe UI", 14), fill=color, anchor="w")
            
            # Legend text  
            canvas.create_text(x_offset + 15, y_offset, text=difficulty,
                             font=("Segoe UI", 11), fill=colors.get("text"), anchor="w")
        
        # Chart title/labels
        canvas.create_text(width//2, 15, text="Avg Hours per Hack per Month",
                         font=("Segoe UI", 11, "bold"), fill=colors.get("text"))
        
        # Y-axis title
        canvas.create_text(15, height//2, text="Avg Time (Hours)", 
                         font=("Segoe UI", 10), fill=colors.get("text_secondary"), angle=90)
