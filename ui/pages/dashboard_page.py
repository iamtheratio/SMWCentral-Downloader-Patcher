"""
Dashboard page for SMWCentral Downloader & Patcher
Displays user analytics and SMWC news/updates
"""
import tkinter as tk
from tkinter import ttk
import json
import os
import sys
import math
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import threading
import sv_ttk

# Add path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from hack_data_manager import HackDataManager
from colors import get_colors

class DashboardPage:
    """Main dashboard page with analytics and news"""
    
    def __init__(self, parent_frame, logger=None):
        self.parent_frame = parent_frame
        self.logger = logger
        self.frame = None
        self.data_manager = HackDataManager()
        self.analytics_data = {}
        self.news_data = []
        self.date_filter = "all_time"  # Default filter
        
    def create(self):
        """Create the dashboard page UI"""
        self.frame = ttk.Frame(self.parent_frame, padding=15)  # Reduced padding to prevent cutoff
        
        # Create main scrollable container
        self._create_scrollable_container()
        
        # Load analytics data
        self._load_analytics_data()
        
        # Create dashboard sections
        self._create_filter_section()
        self._create_main_metrics_with_circle_section()
        self._create_detailed_charts_section()
        
        return self.frame
    
    def _create_scrollable_container(self):
        """Create scrollable container for dashboard content"""
        # Create canvas and scrollbar
        canvas = tk.Canvas(self.frame, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.frame, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)
        
        # Configure scrolling
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        # Create window with sticky to expand to full width
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Configure scrollable frame to expand to full width
        self.scrollable_frame.bind('<Configure>', 
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        def configure_scroll_width(event):
            canvas.itemconfig(canvas.find_all()[0], width=event.width)
        canvas.bind('<Configure>', configure_scroll_width)
        
        # Function to show/hide scrollbar automatically
        def update_scrollbar():
            canvas.update_idletasks()
            bbox = canvas.bbox("all")
            if bbox:
                canvas_height = canvas.winfo_height()
                content_height = bbox[3] - bbox[1]
                if content_height > canvas_height:
                    scrollbar.pack(side="right", fill="y")
                else:
                    scrollbar.pack_forget()
        
        # Pack canvas and bind scrollbar updates
        canvas.pack(side="left", fill="both", expand=True)
        
        # Bind scrollbar update to content changes
        self.scrollable_frame.bind('<Configure>', lambda e: update_scrollbar())
        canvas.bind('<Configure>', lambda e: update_scrollbar())
        
        # Bind mousewheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        
        # Bind to canvas and all child widgets
        def bind_mousewheel(widget):
            widget.bind("<MouseWheel>", _on_mousewheel)
            for child in widget.winfo_children():
                bind_mousewheel(child)
        
        bind_mousewheel(canvas)
        
    def _load_analytics_data(self):
        """Load and process analytics data from processed.json"""
        try:
            # Get the raw data dictionary instead of the formatted list
            processed_data = self.data_manager.data
            
            # Calculate date range for filtering
            now = datetime.now()
            if self.date_filter == "last_week":
                filter_date = now - timedelta(days=7)
            elif self.date_filter == "last_month":
                filter_date = now - timedelta(days=30)
            elif self.date_filter == "3_months":
                filter_date = now - timedelta(days=90)
            elif self.date_filter == "6_months":
                filter_date = now - timedelta(days=180)
            elif self.date_filter == "1_year":
                filter_date = now - timedelta(days=365)
            else:  # all_time or year_plus
                filter_date = None
            
            # Initialize comprehensive analytics
            self.analytics_data = {
                'total_hacks': len(processed_data),
                'completed_hacks': 0,
                'completion_rate': 0.0,
                'filtered_completed': 0,
                'average_rating': 0.0,
                'total_playtime_estimate': 0,  # Estimated based on difficulty
                'difficulty_distribution': defaultdict(int),
                'type_distribution': defaultdict(int),
                'completion_by_difficulty': defaultdict(lambda: {'total': 0, 'completed': 0}),
                'completion_by_type': defaultdict(lambda: {'total': 0, 'completed': 0}),
                'rating_distribution': defaultdict(int),
                'monthly_completions': defaultdict(int),
                'completion_streak': 0,
                'longest_streak': 0,  # NEW: Track longest streak
                'current_streak': 0,  # NEW: Track current streak
                'recent_completions': [],
                'completion_timeline': [],
                'top_rated': [],
                'hardest_completed': [],
                'completion_velocity': 0.0,  # Completions per month
                'favorite_difficulty': '',
                'favorite_type': '',
            }
            
            completed_ratings = []
            completion_dates = []
            
            # Process each hack
            for hack_id, hack_data in processed_data.items():
                is_completed = hack_data.get('completed', False)
                difficulty = hack_data.get('current_difficulty', 'Unknown')
                hack_type = hack_data.get('hack_type', 'Unknown')
                rating = hack_data.get('personal_rating', 0)
                
                # Count totals
                self.analytics_data['difficulty_distribution'][difficulty] += 1
                self.analytics_data['type_distribution'][hack_type] += 1
                self.analytics_data['completion_by_difficulty'][difficulty]['total'] += 1
                self.analytics_data['completion_by_type'][hack_type]['total'] += 1
                
                # Estimate playtime based on difficulty (rough estimates in hours)
                difficulty_hours = {
                    'Easy': 2, 'Normal': 4, 'Hard': 8, 'Very Hard': 12,
                    'Expert': 20, 'Kaizo Light': 30, 'Kaizo': 40, 'Grandmaster': 60
                }
                self.analytics_data['total_playtime_estimate'] += difficulty_hours.get(difficulty, 5)
                
                if is_completed:
                    self.analytics_data['completed_hacks'] += 1
                    self.analytics_data['completion_by_difficulty'][difficulty]['completed'] += 1
                    self.analytics_data['completion_by_type'][hack_type]['completed'] += 1
                    
                    # Process completion date
                    completed_date = hack_data.get('completed_date', '')
                    if completed_date:
                        try:
                            date_obj = datetime.strptime(completed_date, '%Y-%m-%d')
                            completion_dates.append(date_obj)
                            
                            # Check if completion is within filter range
                            if not filter_date or date_obj >= filter_date:
                                self.analytics_data['filtered_completed'] += 1
                            
                            month_key = date_obj.strftime('%Y-%m')
                            self.analytics_data['monthly_completions'][month_key] += 1
                            
                            # Add to timeline
                            self.analytics_data['completion_timeline'].append({
                                'date': completed_date,
                                'title': hack_data.get('title', 'Unknown'),
                                'difficulty': difficulty,
                                'rating': rating,
                                'type': hack_type
                            })
                            
                            # Recent completions (last 30 days)
                            if date_obj >= datetime.now() - timedelta(days=30):
                                self.analytics_data['recent_completions'].append({
                                    'title': hack_data.get('title', 'Unknown'),
                                    'date': completed_date,
                                    'difficulty': difficulty,
                                    'rating': rating
                                })
                        except ValueError:
                            pass  # Invalid date format
                    
                    # Collect ratings for completed hacks
                    if rating > 0:
                        completed_ratings.append(rating)
                        self.analytics_data['rating_distribution'][rating] += 1
                    
                    # Collect hardest completed hacks
                    difficulty_rank = {'Easy': 1, 'Normal': 2, 'Hard': 3, 'Very Hard': 4,
                                     'Expert': 5, 'Kaizo Light': 6, 'Kaizo': 7, 'Grandmaster': 8}
                    if difficulty_rank.get(difficulty, 0) >= 6:  # Kaizo+ difficulties
                        self.analytics_data['hardest_completed'].append({
                            'title': hack_data.get('title', 'Unknown'),
                            'difficulty': difficulty,
                            'rating': rating,
                            'rank': difficulty_rank.get(difficulty, 0)
                        })
                
                # Count all ratings for top rated
                if rating >= 4:  # 4+ star ratings
                    self.analytics_data['top_rated'].append({
                        'title': hack_data.get('title', 'Unknown'),
                        'rating': rating,
                        'difficulty': difficulty,
                        'completed': is_completed,
                        'type': hack_type
                    })
            
            # Calculate derived metrics
            if self.analytics_data['total_hacks'] > 0:
                self.analytics_data['completion_rate'] = (
                    self.analytics_data['completed_hacks'] / self.analytics_data['total_hacks'] * 100
                )
            
            if completed_ratings:
                self.analytics_data['average_rating'] = sum(completed_ratings) / len(completed_ratings)
            
            # Calculate completion velocity (completions per month)
            if completion_dates and len(completion_dates) > 1:
                completion_dates.sort()
                first_completion = completion_dates[0]
                last_completion = completion_dates[-1]
                months_span = max(1, (last_completion - first_completion).days / 30.44)
                self.analytics_data['completion_velocity'] = len(completion_dates) / months_span
            
            # NEW: Calculate completion streaks
            self._calculate_completion_streaks(completion_dates)
            
            # Find favorite difficulty and type (most completed)
            difficulty_completed = {k: v['completed'] for k, v in self.analytics_data['completion_by_difficulty'].items()}
            type_completed = {k: v['completed'] for k, v in self.analytics_data['completion_by_type'].items()}
            
            if difficulty_completed:
                self.analytics_data['favorite_difficulty'] = max(difficulty_completed, key=difficulty_completed.get)
            if type_completed:
                self.analytics_data['favorite_type'] = max(type_completed, key=type_completed.get)
            
            # Sort and limit collections
            self.analytics_data['top_rated'].sort(key=lambda x: x['rating'], reverse=True)
            self.analytics_data['top_rated'] = self.analytics_data['top_rated'][:5]
            
            self.analytics_data['hardest_completed'].sort(key=lambda x: x['rank'], reverse=True)
            self.analytics_data['hardest_completed'] = self.analytics_data['hardest_completed'][:5]
            
            self.analytics_data['completion_timeline'].sort(key=lambda x: x['date'], reverse=True)
            
        except Exception as e:
            if self.logger:
                self.logger.log(f"Error loading analytics data: {e}", level="error")
            self.analytics_data = {'total_hacks': 0, 'completed_hacks': 0, 'completion_rate': 0.0}
    
    def _calculate_completion_streaks(self, completion_dates):
        """Calculate completion streaks based on completion dates"""
        if not completion_dates:
            self.analytics_data['longest_streak'] = 0
            self.analytics_data['current_streak'] = 0
            self.analytics_data['completion_streak'] = 0
            return
        
        # Sort dates and get unique dates (in case multiple completions on same day)
        unique_dates = sorted(list(set(completion_dates)))
        
        if not unique_dates:
            self.analytics_data['longest_streak'] = 0
            self.analytics_data['current_streak'] = 0
            self.analytics_data['completion_streak'] = 0
            return
        
        longest_streak = 1
        current_streak = 1
        streak_from_today = 0
        
        today = datetime.now().date()
        
        # Calculate streaks by checking consecutive days
        for i in range(1, len(unique_dates)):
            prev_date = unique_dates[i-1].date()
            curr_date = unique_dates[i].date()
            
            # Check if dates are consecutive (difference of 1 day)
            if (curr_date - prev_date).days == 1:
                current_streak += 1
            else:
                # Streak broken, record longest streak so far
                longest_streak = max(longest_streak, current_streak)
                current_streak = 1
        
        # Check final streak
        longest_streak = max(longest_streak, current_streak)
        
        # Calculate current streak from today backwards
        if unique_dates:
            last_completion_date = unique_dates[-1].date()
            
            # Check if streak is ongoing (last completion was today or yesterday)
            days_since_last = (today - last_completion_date).days
            
            if days_since_last <= 1:  # Today or yesterday
                # Count backwards from last completion to find current streak
                streak_from_today = 1
                for i in range(len(unique_dates) - 2, -1, -1):
                    prev_date = unique_dates[i].date()
                    next_date = unique_dates[i + 1].date()
                    
                    if (next_date - prev_date).days == 1:
                        streak_from_today += 1
                    else:
                        break
            else:
                streak_from_today = 0  # No current streak
        
        self.analytics_data['longest_streak'] = longest_streak
        self.analytics_data['current_streak'] = streak_from_today
        
        # Use the more meaningful streak (current if active, otherwise longest)
        self.analytics_data['completion_streak'] = streak_from_today if streak_from_today > 0 else longest_streak

    def _create_header_section(self):
        """Create the dashboard header"""
        header_frame = ttk.Frame(self.scrollable_frame)
        header_frame.pack(fill="x", padx=20, pady=(20, 10))
        
        # Dashboard title
        title_label = ttk.Label(
            header_frame,
            text="📊 Dashboard",
            font=("Segoe UI", 18, "bold")
        )
        title_label.pack(side="left")
        
        # Refresh button
        refresh_btn = ttk.Button(
            header_frame,
            text="🔄 Refresh",
            command=self._refresh_dashboard
        )
        refresh_btn.pack(side="right")
    
    def _create_filter_section(self):
        """Create simplified date filter section"""
        filter_frame = ttk.LabelFrame(self.scrollable_frame, text="Time Period", padding=10)
        filter_frame.pack(fill="x", padx=10, pady=(0, 15))  # Add horizontal padding
        
        # Create main container with filter buttons and refresh button
        main_container = ttk.Frame(filter_frame)
        main_container.pack(fill="x")
        
        # Create filter buttons container
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
                command=lambda v=value: self._apply_date_filter(v),
                style="Accent.TButton" if value == self.date_filter else "TButton"
            )
            btn.pack(side="left", padx=5)
        
        # Add refresh button on the right
        refresh_btn = ttk.Button(
            main_container,
            text="🔄 Refresh",
            command=self._refresh_dashboard
        )
        refresh_btn.pack(side="right", padx=(10, 0))
    
    def _apply_date_filter(self, filter_value):
        """Apply date filter and refresh dashboard"""
        self.date_filter = filter_value
        self._refresh_dashboard()
    
    def _create_large_metrics_section(self):
        """Create large, clean metrics section like the mockup"""
        colors = get_colors()
        
        # Main metrics container - REMOVED background, use parent background
        metrics_frame = tk.Frame(self.scrollable_frame)
        metrics_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Create two rows of metrics
        top_row = tk.Frame(metrics_frame)
        top_row.pack(fill="x", pady=(10, 5))
        
        bottom_row = tk.Frame(metrics_frame)
        bottom_row.pack(fill="x", pady=(5, 10))
        
        # Configure column weights for full width
        for i in range(4):
            top_row.columnconfigure(i, weight=1, uniform="metrics")
        for i in range(3):  # Bottom row now has 3 items
            bottom_row.columnconfigure(i, weight=1, uniform="metrics")
        
        # Top row metrics
        self._create_large_metric_card(
            top_row, "TOTAL HACKS", 
            str(self.analytics_data.get('total_hacks', 0)),
            "📦", colors.get("info"), 0, 0
        )
        
        self._create_large_metric_card(
            top_row, "COMPLETED", 
            str(self.analytics_data.get('filtered_completed', 0) if self.date_filter != 'all_time' else self.analytics_data.get('completed_hacks', 0)),
            "✅", colors.get("success"), 0, 1
        )
        
        recent_count = len(self.analytics_data.get('recent_completions', []))
        self._create_large_metric_card(
            top_row, "LAST 30 DAYS", 
            str(recent_count),
            "🔥", colors.get("warning"), 0, 2
        )
        
        # Bottom row metrics - gaming specific
        avg_rating = self.analytics_data.get('average_rating', 0.0)
        self._create_large_metric_card(
            bottom_row, "AVG RATING", 
            f"{avg_rating:.1f}⭐" if avg_rating > 0 else "N/A",
            "⭐", colors.get("warning"), 0, 0
        )
        
        velocity = self.analytics_data.get('completion_velocity', 0.0)
        self._create_large_metric_card(
            bottom_row, "AVG HACK PER MONTH", 
            f"{velocity:.1f}/m" if velocity > 0 else "N/A",
            "🚀", colors.get("accent"), 0, 1
        )
        
        # NEW: Completion Streak metric
        streak = self.analytics_data.get('completion_streak', 0)
        current_streak = self.analytics_data.get('current_streak', 0)
        
        # Show current streak if active, otherwise show longest streak
        if current_streak > 0:
            streak_text = f"{current_streak}"
            streak_label = "CURRENT STREAK"
            streak_color = colors.get("success")  # Green for active streak
        else:
            longest_streak = self.analytics_data.get('longest_streak', 0)
            streak_text = f"{longest_streak}" if longest_streak > 0 else "0"
            streak_label = "BEST STREAK"
            streak_color = colors.get("info")  # Blue for historical best
        
        self._create_large_metric_card(
            bottom_row, streak_label,
            streak_text,
            "🔥", streak_color, 0, 2
        )
    
    def _create_large_metric_card(self, parent, title, value, icon, color, row, col):
        """Create a large, clean metric card matching the mockup"""
        colors = get_colors()
        
        # Card frame with NO background - transparent
        card_frame = tk.Frame(parent)
        card_frame.grid(row=row, column=col, padx=10, pady=5, sticky="ew")  # Reduced padding
        
        # Large value on top - reduced font size to fit better
        value_label = tk.Label(
            card_frame,
            text=value,
            font=("Segoe UI", 44, "bold"),  # Reduced from 48 to 44
            fg=color,
            bg=parent.cget("bg")  # Match parent background
        )
        value_label.pack(pady=(0, 5))
        
        # Small title below the number
        title_label = tk.Label(
            card_frame,
            text=title,
            font=("Segoe UI", 10, "bold"),  # Reduced from 11 to 10
            fg=colors.get("text_secondary"),
            bg=parent.cget("bg")  # Match parent background
        )
        title_label.pack()
    
    def _create_completion_circle(self):
        """Create a large completion rate circle visualization"""
        colors = get_colors()
        
        # Use a regular frame instead of LabelFrame to remove background
        circle_frame = tk.Frame(self.scrollable_frame)
        circle_frame.pack(fill="x", padx=20, pady=15)
        
        # Add Progress Overview title as a separate label
        title_label = tk.Label(
            circle_frame,
            text="COMPLETION RATE",
            font=("Segoe UI", 14, "bold"),
            fg=colors.get("text_primary"),
            bg=circle_frame.cget("app_bg")
        )
        title_label.pack(anchor="w", pady=(0, 10))
        
        # Main container for circle and stats
        main_container = tk.Frame(circle_frame)
        main_container.pack(fill="x")
        
        # Create canvas for circle
        canvas_size = 200
        canvas = tk.Canvas(
            main_container, 
            width=canvas_size, 
            height=canvas_size,
            highlightthickness=0,
            relief='flat',
            borderwidth=0
        )
        canvas.pack(side="left", padx=20)
        
        # Draw completion circle
        self._draw_completion_circle(canvas, canvas_size)
        
        # Statistics beside the circle
        stats_frame = tk.Frame(main_container)
        stats_frame.pack(side="left", fill="both", expand=True, padx=20)
        
        # Completion stats
        completion_rate = self.analytics_data.get('completion_rate', 0.0)
        completed = self.analytics_data.get('completed_hacks', 0)
        total = self.analytics_data.get('total_hacks', 0)
        
        rate_label = tk.Label(
            stats_frame,
            text=f"{completion_rate:.1f}%",
            font=("Segoe UI", 32, "bold"),
            fg=colors.get("accent")
        )
        rate_label.pack(anchor="w")
        
        ratio_label = tk.Label(
            stats_frame,
            text=f"{completed} / {total}",
            font=("Segoe UI", 16),
            fg=colors.get("text")
        )
        ratio_label.pack(anchor="w")
        
        # Additional insights
        fav_diff = self.analytics_data.get('favorite_difficulty', 'N/A')
        fav_type = self.analytics_data.get('favorite_type', 'N/A')
        
        if fav_diff != 'N/A':
            tk.Label(
                stats_frame,
                text=f"Favorite Difficulty: {fav_diff}",
                font=("Segoe UI", 12),
                fg=colors.get("text_secondary")
            ).pack(anchor="w", pady=(10, 2))
        
        if fav_type != 'N/A':
            tk.Label(
                stats_frame,
                text=f"Favorite Type: {fav_type.title()}",
                font=("Segoe UI", 12),
                fg=colors.get("text_secondary")
            ).pack(anchor="w", pady=2)
    
    def _draw_completion_circle(self, canvas, size):
        """Draw completion rate as a circle chart"""
        colors = get_colors()
        center = size // 2
        radius = size // 2 - 20
        
        completion_rate = self.analytics_data.get('completion_rate', 0.0)
        completion_decimal = completion_rate / 100
        
        # Set canvas background to match theme
        if sv_ttk.get_theme() == "dark":
            canvas.configure(bg="#1c1c1c")
            inner_fill = "#1c1c1c"
        else:
            canvas.configure(bg="white")
            inner_fill = "white"
        
        # Background circle
        canvas.create_oval(
            center - radius, center - radius,
            center + radius, center + radius,
            fill=colors.get("progress_bg"),
            outline=""
        )
        
        # Completion arc
        if completion_decimal > 0:
            extent = 360 * completion_decimal
            canvas.create_arc(
                center - radius, center - radius,
                center + radius, center + radius,
                start=90, extent=-extent,
                fill=colors.get("accent"),
                outline=""
            )
        
        # Inner circle for donut effect
        inner_radius = radius - 30
        canvas.create_oval(
            center - inner_radius, center - inner_radius,
            center + inner_radius, center + inner_radius,
            fill=inner_fill,
            outline=""
        )
        
        # Add percentage text in the center of the circle
        canvas.create_text(
            center, center,
            text=f"{completion_rate:.1f}%",
            font=("Segoe UI", 24, "bold"),
            fill=colors.get("text"),  # Changed from accent to text color (white/black based on theme)
            anchor="center"
        )
    
    def _create_stats_overview(self):
        """Legacy method - replaced by _create_large_metrics_section"""
        pass
    
    def _create_charts_section(self):
        """Legacy method - replaced by _create_detailed_charts_section"""
        pass
    
    def _create_progress_section(self):
        """Legacy method - replaced by _create_gaming_insights_section"""
        pass
    
    def _create_stat_card(self, parent, title, value, row, col):
        """Legacy method - replaced by _create_large_metric_card"""
        pass
    
    def _create_difficulty_chart(self, parent, row, col):
        """Legacy method - replaced by _create_completion_by_difficulty_chart"""
        pass
    
    def _create_type_chart(self, parent, row, col):
        """Legacy method - replaced by _create_completion_by_type_chart"""
        pass
    
    def _create_news_section(self):
        """Create SMWCentral news/updates section"""
        news_frame = ttk.LabelFrame(self.scrollable_frame, text="SMWCentral Updates", padding=15)
        news_frame.pack(fill="x", padx=20, pady=10)
        
        # Loading indicator
        self.news_loading_label = ttk.Label(news_frame, text="Loading SMWC updates...")
        self.news_loading_label.pack()
        
        # News container (will be populated when data loads)
        self.news_container = ttk.Frame(news_frame)
        self.news_container.pack(fill="x")
    
    def _load_smwc_news(self):
        """Load SMWC news/updates in background thread"""
        def fetch_news():
            try:
                # Try to fetch recent hack submissions/updates from SMWC API
                from smwc_api_proxy import smwc_api_get
                
                # Get recent hack submissions (last 10)
                params = {
                    "a": "getsectionlist",
                    "s": "smwhacks",
                    "n": 1,  # First page
                    "u": 0   # Moderated hacks
                }
                
                response = smwc_api_get("https://www.smwcentral.net/ajax.php", params=params, log=self.logger.log if self.logger else None)
                data = response.json()
                
                if data.get('status') == 'success' and 'data' in data:
                    # Process recent hacks as "news"
                    hacks = data['data'][:5]  # Get first 5 hacks
                    
                    self.news_data = []
                    for hack in hacks:
                        self.news_data.append({
                            'title': f"New Hack: {hack.get('name', 'Unknown')}",
                            'description': f"By {hack.get('authors', 'Unknown')} - {hack.get('difficulty', 'Unknown')} difficulty",
                            'date': hack.get('date', ''),
                            'url': f"https://www.smwcentral.net/?p=section&a=details&id={hack.get('id', '')}"
                        })
                    
                    # Update UI in main thread
                    self.frame.after(0, self._update_news_ui)
                else:
                    # Fallback to placeholder news
                    self._create_fallback_news()
                    
            except Exception as e:
                if self.logger:
                    self.logger.log(f"Error fetching SMWC news: {e}", level="warning")
                # Create fallback news
                self.frame.after(0, self._create_fallback_news)
        
        # Start background thread
        threading.Thread(target=fetch_news, daemon=True).start()
    
    def _update_news_ui(self):
        """Update news UI with fetched data"""
        # Hide loading indicator
        self.news_loading_label.pack_forget()
        
        # Clear existing news
        for widget in self.news_container.winfo_children():
            widget.destroy()
        
        # Add news items
        for news_item in self.news_data:
            self._create_news_item(news_item)
    
    def _create_fallback_news(self):
        """Create fallback news when API is unavailable"""
        self.news_data = [
            {
                'title': "📰 SMWC News Unavailable",
                'description': "Unable to fetch latest updates from SMWCentral. Check your internet connection.",
                'date': datetime.now().strftime('%Y-%m-%d'),
                'url': "https://www.smwcentral.net"
            },
            {
                'title': "💡 Pro Tip",
                'description': "Use the Bulk Download page to discover and download new hacks!",
                'date': datetime.now().strftime('%Y-%m-%d'),
                'url': ""
            }
        ]
        self._update_news_ui()
    
    def _create_news_item(self, news_item):
        """Create a single news item widget"""
        item_frame = ttk.Frame(self.news_container)
        item_frame.pack(fill="x", pady=5)
        
        # Title
        title_label = ttk.Label(
            item_frame,
            text=news_item['title'],
            font=("Segoe UI", 10, "bold")
        )
        title_label.pack(anchor="w")
        
        # Description
        desc_label = ttk.Label(
            item_frame,
            text=news_item['description'],
            font=("Segoe UI", 9)
        )
        desc_label.pack(anchor="w")
        
        # Date
        if news_item.get('date'):
            date_label = ttk.Label(
                item_frame,
                text=f"📅 {news_item['date']}",
                font=("Segoe UI", 8),
                foreground="gray"
            )
            date_label.pack(anchor="w")
    
    def _refresh_dashboard(self):
        """Refresh dashboard data"""
        if self.logger:
            self.logger.log("Refreshing dashboard data...", level="info")
        
        # Reload data manager
        self.data_manager = HackDataManager()
        
        # Reload analytics data
        self._load_analytics_data()
        
        # Recreate the entire dashboard
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        self._create_filter_section()
        self._create_main_metrics_with_circle_section()
        self._create_detailed_charts_section()
        
        if self.logger:
            self.logger.log("Dashboard refreshed successfully!", level="info")
    
    def _create_detailed_charts_section(self):
        """Create detailed charts section with organized layout"""
        charts_frame = ttk.LabelFrame(self.scrollable_frame, text="Detailed Analytics", padding=10)
        charts_frame.pack(fill="x", padx=5, pady=(10, 15))  # Reduced horizontal padding from 10 to 5
        
        # Create two column layout for charts
        charts_container = ttk.Frame(charts_frame)
        charts_container.pack(fill="x", expand=True)
        
        charts_container.columnconfigure(0, weight=1)
        charts_container.columnconfigure(1, weight=1)
        
        # Column 1
        col1_frame = ttk.Frame(charts_container)
        col1_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        
        # Column 2
        col2_frame = ttk.Frame(charts_container)
        col2_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        
        # Configure row weights for proper expansion
        col1_frame.rowconfigure(0, weight=1)
        col1_frame.rowconfigure(1, weight=1)
        col2_frame.rowconfigure(0, weight=1)
        col2_frame.rowconfigure(1, weight=1)
        
        # Column 1 charts
        self._create_completion_by_type_chart(col1_frame, 0, 0)
        self._create_completion_by_difficulty_chart(col1_frame, 1, 0)
        
        # Column 2 charts
        self._create_special_completion_counts_chart(col2_frame, 0, 0)
        self._create_rating_distribution_chart(col2_frame, 1, 0)
    
    def _create_completion_by_difficulty_chart(self, parent, row, col):
        """Create completion rate by difficulty chart"""
        colors = get_colors()
        chart_frame = ttk.LabelFrame(parent, text="📊 Completion by Difficulty", padding=8)
        chart_frame.grid(row=row, column=col, padx=2, pady=2, sticky="nsew")
        
        # Ensure the frame expands properly
        parent.rowconfigure(row, weight=1)
        parent.columnconfigure(col, weight=1)
        
        completion_data = self.analytics_data.get('completion_by_difficulty', {})
        
        if not completion_data:
            ttk.Label(chart_frame, text="No data available").pack()
            return
        
        # Sort difficulties by rank
        difficulty_order = ['Easy', 'Normal', 'Hard', 'Very Hard', 'Expert', 'Kaizo Light', 'Kaizo', 'Grandmaster']
        sorted_difficulties = [d for d in difficulty_order if d in completion_data]
        
        for difficulty in sorted_difficulties:
            data = completion_data[difficulty]
            if data['total'] > 0:
                completion_rate = (data['completed'] / data['total']) * 100
                
                # Create bar visualization
                bar_frame = tk.Frame(chart_frame)
                bar_frame.pack(fill="x", pady=3)
                
                # Label
                label_text = f"{difficulty}: {data['completed']}/{data['total']} ({completion_rate:.0f}%)"
                label = tk.Label(
                    bar_frame,
                    text=label_text,
                    font=("Segoe UI", 9),
                    fg=colors.get("text"),
                    width=28,
                    anchor="w"
                )
                label.pack(side="left")
                
                # Progress bar visualization
                progress_frame = tk.Frame(bar_frame)
                progress_frame.pack(side="left", fill="x", expand=True, padx=(5, 0))
                
                progress_bg = tk.Frame(
                    progress_frame, 
                    bg=colors.get("progress_bg"),
                    height=22,  # Increased from 18 to 22
                    relief="flat",  # Remove borders
                    bd=0  # Remove border width
                )
                progress_bg.pack(fill="x")
                
                if completion_rate > 0:
                    progress_fill = tk.Frame(
                        progress_bg,
                        bg=colors.get("success") if completion_rate >= 50 else colors.get("warning"),
                        height=22,  # Increased to match background
                        relief="flat",  # Remove borders
                        bd=0  # Remove border width
                    )
                    progress_fill.place(x=0, y=0, relwidth=completion_rate/100, height=22)  # Remove 1px margin
    
    def _create_completion_by_type_chart(self, parent, row, col):
        """Create completion rate by type chart"""
        colors = get_colors()
        chart_frame = ttk.LabelFrame(parent, text="🎮 Completion by Type", padding=8)
        chart_frame.grid(row=row, column=col, padx=2, pady=2, sticky="nsew")
        
        # Ensure the frame expands properly
        parent.rowconfigure(row, weight=1)
        parent.columnconfigure(col, weight=1)
        
        completion_data = self.analytics_data.get('completion_by_type', {})
        
        if not completion_data:
            ttk.Label(chart_frame, text="No data available").pack()
            return
        
        for hack_type, data in sorted(completion_data.items()):
            if data['total'] > 0:
                completion_rate = (data['completed'] / data['total']) * 100
                
                # Create bar visualization
                bar_frame = tk.Frame(chart_frame)
                bar_frame.pack(fill="x", pady=3)
                
                # Label
                label_text = f"{hack_type.title()}: {data['completed']}/{data['total']} ({completion_rate:.0f}%)"
                label = tk.Label(
                    bar_frame,
                    text=label_text,
                    font=("Segoe UI", 9),
                    fg=colors.get("text"),
                    width=28,
                    anchor="w"
                )
                label.pack(side="left")
                
                # Progress bar visualization
                progress_frame = tk.Frame(bar_frame)
                progress_frame.pack(side="left", fill="x", expand=True, padx=(5, 0))
                
                progress_bg = tk.Frame(
                    progress_frame, 
                    bg=colors.get("progress_bg"),
                    height=22,  # Increased from 18 to 22
                    relief="flat",  # Remove borders
                    bd=0  # Remove border width
                )
                progress_bg.pack(fill="x")
                
                if completion_rate > 0:
                    progress_fill = tk.Frame(
                        progress_bg,
                        bg=colors.get("info"),
                        height=22,  # Increased to match background
                        relief="flat",  # Remove borders
                        bd=0  # Remove border width
                    )
                    progress_fill.place(x=0, y=0, relwidth=completion_rate/100, height=22)  # Remove 1px margin
    
    def _create_rating_distribution_chart(self, parent, row, col):
        """Create rating distribution chart"""
        colors = get_colors()
        chart_frame = ttk.LabelFrame(parent, text="⭐ Rating Distribution", padding=8)
        chart_frame.grid(row=row, column=col, padx=2, pady=2, sticky="nsew")
        
        # Ensure the frame expands properly
        parent.rowconfigure(row, weight=1)
        parent.columnconfigure(col, weight=1)
        
        rating_data = self.analytics_data.get('rating_distribution', {})
        
        if not rating_data:
            ttk.Label(chart_frame, text="No ratings given yet").pack()
            return
        
        total_ratings = sum(rating_data.values())
        
        for rating in range(5, 0, -1):  # 5 stars to 1 star
            count = rating_data.get(rating, 0)
            if count > 0 or rating >= 4:  # Show 4-5 stars even if 0
                percentage = (count / total_ratings) * 100 if total_ratings > 0 else 0
                
                # Create bar visualization
                bar_frame = tk.Frame(chart_frame)
                bar_frame.pack(fill="x", pady=2)
                
                # Star label
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
                
                # Progress bar
                progress_frame = tk.Frame(bar_frame)
                progress_frame.pack(side="left", fill="x", expand=True, padx=(5, 0))
                
                progress_bg = tk.Frame(
                    progress_frame, 
                    bg=colors.get("progress_bg"),
                    height=20,  # Increased from 15 to 20
                    relief="flat",  # Remove borders
                    bd=0  # Remove border width
                )
                progress_bg.pack(fill="x")
                
                if percentage > 0:
                    color = colors.get("warning") if rating >= 4 else colors.get("accent")
                    progress_fill = tk.Frame(
                        progress_bg,
                        bg=color,
                        height=20,  # Increased to match background
                        relief="flat",  # Remove borders
                        bd=0  # Remove border width
                    )
                    progress_fill.place(x=0, y=0, relwidth=percentage/100, height=20)  # Remove 1px margin
    
    def _create_special_completion_counts_chart(self, parent, row, col):
        """Create completion counts by special categories"""
        colors = get_colors()
        chart_frame = ttk.LabelFrame(parent, text="🏆 Special Completion Counts", padding=8)
        chart_frame.grid(row=row, column=col, padx=2, pady=2, sticky="nsew")
        
        # Ensure the frame expands properly
        parent.rowconfigure(row, weight=1)
        parent.columnconfigure(col, weight=1)
        
        # Count special categories from processed data
        special_counts = {
            'Hall of Fame': 0,
            'SA-1': 0,
            'Collaboration': 0,
            'Demo': 0
        }
        
        # Load processed data to check for special categories
        try:
            with open('processed.json', 'r') as f:
                processed_data = json.load(f)
                
            for hack_id, hack_data in processed_data.items():
                if hack_data.get('completed', False):
                    # Check for Hall of Fame (assuming high featured score)
                    featured_score = hack_data.get('featured_score', 0)
                    if featured_score >= 30:  # High threshold for hall of fame
                        special_counts['Hall of Fame'] += 1
                    
                    # Check hack name/description for special types
                    hack_name = hack_data.get('name', '').lower()
                    hack_description = hack_data.get('description', '').lower()
                    
                    if 'sa-1' in hack_name or 'sa1' in hack_name or 'sa-1' in hack_description:
                        special_counts['SA-1'] += 1
                    if 'collab' in hack_name or 'collaboration' in hack_name or 'collab' in hack_description:
                        special_counts['Collaboration'] += 1
                    if 'demo' in hack_name or hack_data.get('hack_type', '').lower() == 'demo':
                        special_counts['Demo'] += 1
                        
        except (FileNotFoundError, json.JSONDecodeError):
            pass
        
        # Display special counts
        for category, count in special_counts.items():
            if count > 0:  # Only show categories with completions
                item_frame = tk.Frame(chart_frame)
                item_frame.pack(fill="x", pady=3)
                
                # Icon and label
                icon_map = {
                    'Hall of Fame': '🏆',
                    'SA-1': '⚡',
                    'Collaboration': '🤝', 
                    'Demo': '🎮'
                }
                
                label = tk.Label(
                    item_frame,
                    text=f"{icon_map[category]} {category}: {count}",
                    font=("Segoe UI", 10),
                    fg=colors.get("text"),
                    anchor="w"
                )
                label.pack(side="left")
        
        # If no special completions found
        if all(count == 0 for count in special_counts.values()):
            ttk.Label(chart_frame, text="No special completions yet").pack()
    
    def _create_gaming_insights_section(self):
        """Create gaming-specific insights and achievements"""
        colors = get_colors()
        insights_frame = ttk.LabelFrame(self.scrollable_frame, text="Gaming Insights", padding=15)
        insights_frame.pack(fill="x", padx=20, pady=15)
        
        # Create two column layout
        insights_container = ttk.Frame(insights_frame)
        insights_container.pack(fill="x")
        
        insights_container.columnconfigure(0, weight=1)
        insights_container.columnconfigure(1, weight=1)
        
        # Left column - Achievements & Stats
        left_frame = ttk.LabelFrame(insights_container, text="🏆 Achievements", padding=10)
        left_frame.grid(row=0, column=0, padx=(0, 10), pady=5, sticky="ew")
        
        # Right column - Top Rated & Hardest
        right_frame = ttk.LabelFrame(insights_container, text="🌟 Hall of Fame", padding=10)
        right_frame.grid(row=0, column=1, padx=(10, 0), pady=5, sticky="ew")
        
        # Achievements
        self._create_achievements_section(left_frame)
        
        # Hall of Fame
        self._create_hall_of_fame_section(right_frame)
    
    def _create_achievements_section(self, parent):
        """Create achievements based on completion data"""
        colors = get_colors()
        
        achievements = []
        
        # Calculate achievements
        completed = self.analytics_data.get('completed_hacks', 0)
        total = self.analytics_data.get('total_hacks', 0)
        completion_rate = self.analytics_data.get('completion_rate', 0)
        hardest_completed = self.analytics_data.get('hardest_completed', [])
        perfectionist = self.analytics_data.get('perfectionist_score', 0)
        
        if completed >= 1:
            achievements.append(("🥇", "First Completion", "Completed your first hack!"))
        if completed >= 5:
            achievements.append(("🔥", "On Fire", "Completed 5 hacks"))
        if completed >= 10:
            achievements.append(("💯", "Double Digits", "Completed 10 hacks"))
        if completed >= 25:
            achievements.append(("🚀", "Quarter Century", "Completed 25 hacks"))
        if completion_rate >= 50:
            achievements.append(("⚡", "Half Way", "50% completion rate"))
        if perfectionist >= 75:
            achievements.append(("👑", "Perfectionist", "75%+ high ratings"))
        if any(h['rank'] >= 7 for h in hardest_completed):
            achievements.append(("😈", "Kaizo Master", "Completed Kaizo+ difficulty"))
        
        if not achievements:
            achievements.append(("🎯", "Getting Started", "Start completing hacks to unlock achievements!"))
        
        for emoji, title, description in achievements[-5:]:  # Show last 5 achievements
            achievement_frame = tk.Frame(parent)
            achievement_frame.pack(fill="x", pady=3)
            
            tk.Label(
                achievement_frame,
                text=emoji,
                font=("Segoe UI Emoji", 16)
            ).pack(side="left")
            
            text_frame = tk.Frame(achievement_frame)
            text_frame.pack(side="left", fill="x", expand=True, padx=(10, 0))
            
            tk.Label(
                text_frame,
                text=title,
                font=("Segoe UI", 10, "bold"),
                fg=colors.get("text"),
                anchor="w"
            ).pack(fill="x")
            
            tk.Label(
                text_frame,
                text=description,
                font=("Segoe UI", 9),
                fg=colors.get("text_secondary"),
                anchor="w"
            ).pack(fill="x")
    
    def _create_hall_of_fame_section(self, parent):
        """Create hall of fame with top rated and hardest completed"""
        colors = get_colors()
        
        top_rated = self.analytics_data.get('top_rated', [])
        hardest_completed = self.analytics_data.get('hardest_completed', [])
        
        if top_rated:
            tk.Label(
                parent,
                text="⭐ Top Rated Hacks",
                font=("Segoe UI", 11, "bold"),
                fg=colors.get("text")
            ).pack(anchor="w", pady=(0, 5))
            
            for hack in top_rated[:3]:
                hack_frame = tk.Frame(parent)
                hack_frame.pack(fill="x", pady=2)
                
                title_text = f"{'⭐' * hack['rating']} {hack['title'][:25]}{'...' if len(hack['title']) > 25 else ''}"
                tk.Label(
                    hack_frame,
                    text=title_text,
                    font=("Segoe UI", 9),
                    fg=colors.get("text"),
                    anchor="w"
                ).pack(fill="x")
        
        if hardest_completed:
            tk.Label(
                parent,
                text="😈 Hardest Conquered",
                font=("Segoe UI", 11, "bold"),
                fg=colors.get("text")
            ).pack(anchor="w", pady=(15, 5))
            
            for hack in hardest_completed[:3]:
                hack_frame = tk.Frame(parent)
                hack_frame.pack(fill="x", pady=2)
                
                difficulty_emoji = {"Kaizo Light": "🟡", "Kaizo": "🔴", "Grandmaster": "💀"}
                emoji = difficulty_emoji.get(hack['difficulty'], "⚪")
                title_text = f"{emoji} {hack['title'][:25]}{'...' if len(hack['title']) > 25 else ''}"
                
                tk.Label(
                    hack_frame,
                    text=title_text,
                    font=("Segoe UI", 9),
                    fg=colors.get("text"),
                    anchor="w"
                ).pack(fill="x")
        
        if not top_rated and not hardest_completed:
            tk.Label(
                parent,
                text="Complete and rate some hacks to see your hall of fame!",
                font=("Segoe UI", 9),
                fg=colors.get("text_secondary"),
                wraplength=200
            ).pack()
    
    def _create_main_metrics_with_circle_section(self):
        """Create main metrics section with completion circle on the right"""
        colors = get_colors()
        
        # Main container for metrics and circle
        main_container = tk.Frame(self.scrollable_frame)
        main_container.pack(fill="x", padx=5, pady=(10, 15))  # Reduced padding from 10 to 5
        
        # Left side - metrics (70% width)
        metrics_container = tk.Frame(main_container)
        metrics_container.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        # Right side - completion circle (30% width)
        circle_container = tk.Frame(main_container, width=280)  # Reduced from 320 to 280
        circle_container.pack(side="right", fill="y")
        circle_container.pack_propagate(False)  # Maintain fixed width
        
        # Create metrics grid (2 rows, 3 columns)
        top_row = tk.Frame(metrics_container)
        top_row.pack(fill="x", pady=(0, 10))  # Reduced from 15 to 10
        
        bottom_row = tk.Frame(metrics_container)
        bottom_row.pack(fill="x", pady=(0, 5))  # Reduced from 10 to 5
        
        # Configure column weights for metrics
        for i in range(3):
            top_row.columnconfigure(i, weight=1, uniform="metrics")
            bottom_row.columnconfigure(i, weight=1, uniform="metrics")
        
        # Top row metrics (removed completion rate)
        self._create_large_metric_card(
            top_row, "TOTAL HACKS", 
            str(self.analytics_data.get('total_hacks', 0)),
            "📦", colors.get("text"), 0, 0  # Changed to text color
        )
        
        self._create_large_metric_card(
            top_row, "COMPLETED", 
            str(self.analytics_data.get('filtered_completed', 0) if self.date_filter != 'all_time' else self.analytics_data.get('completed_hacks', 0)),
            "✅", colors.get("text"), 0, 1  # Changed to text color
        )
        
        recent_count = len(self.analytics_data.get('recent_completions', []))
        self._create_large_metric_card(
            top_row, "LAST 30 DAYS", 
            str(recent_count),
            "🔥", colors.get("text"), 0, 2  # Changed to text color
        )
        
        # Bottom row metrics - REPLACED PERFECTIONIST WITH COMPLETION STREAK
        avg_rating = self.analytics_data.get('average_rating', 0.0)
        self._create_large_metric_card(
            bottom_row, "AVG RATING", 
            f"{avg_rating:.1f}⭐" if avg_rating > 0 else "N/A",
            "⭐", colors.get("text"), 0, 0  # Changed to text color
        )
        
        velocity = self.analytics_data.get('completion_velocity', 0.0)
        self._create_large_metric_card(
            bottom_row, "AVG HACK PER MONTH", 
            f"{velocity:.1f}/m" if velocity > 0 else "N/A",
            "🚀", colors.get("text"), 0, 1  # Changed to text color
        )
        
        # NEW: Completion Streak metric
        streak = self.analytics_data.get('completion_streak', 0)
        current_streak = self.analytics_data.get('current_streak', 0)
        
        # Show current streak if active, otherwise show longest streak
        if current_streak > 0:
            streak_text = f"{current_streak}"
            streak_label = "CURRENT STREAK"
            streak_color = colors.get("text")  # Changed to text color
        else:
            longest_streak = self.analytics_data.get('longest_streak', 0)
            streak_text = f"{longest_streak}" if longest_streak > 0 else "0"
            streak_label = "BEST STREAK"
            streak_color = colors.get("text")  # Changed to text color
        
        self._create_large_metric_card(
            bottom_row, streak_label,
            streak_text,
            "🔥", streak_color, 0, 2
        )
        
        # Completion circle on the right side
        self._create_completion_circle_widget(circle_container)
    
    def _create_completion_circle_widget(self, parent):
        """Create the completion circle widget for the right side"""
        colors = get_colors()
        
        # Create a background frame that matches the theme
        circle_bg_frame = tk.Frame(parent, bg=colors.get("card_bg"))
        circle_bg_frame.pack(fill="both", expand=True, padx=5, pady=5)  # Reduced padding from 10 to 5
        
        # Progress Overview title
        title_label = tk.Label(
            circle_bg_frame,
            text="COMPLETION RATE",
            font=("Segoe UI", 14, "bold"),  # Reduced font size from 16 to 14
            fg=colors.get("text_secondary"),  # Changed to match other metric titles
            bg=colors.get("card_bg")
        )
        title_label.pack(pady=(10, 10))  # Reduced padding from (15, 15) to (10, 10)
        
        # Create canvas for circle - OPTIMIZED SIZE
        canvas_size = 180  # Reduced from 200 to 180 to fit better
        canvas = tk.Canvas(
            circle_bg_frame, 
            width=canvas_size, 
            height=canvas_size,
            highlightthickness=0,
            relief='flat',
            borderwidth=0,
            bg=colors.get("card_bg")
        )
        canvas.pack(pady=(0, 10))  # Reduced padding from (0, 15) to (0, 10)
        
        # Draw completion circle
        self._draw_completion_circle(canvas, canvas_size)
        
        # Completion stats below circle (only show count, not percentage)
        completed = self.analytics_data.get('completed_hacks', 0)
        total = self.analytics_data.get('total_hacks', 0)
        
        count_label = tk.Label(
            circle_bg_frame,
            text=f"{completed} / {total}",
            font=("Segoe UI", 13),  # Larger font
            fg=colors.get("text_secondary"),
            bg=colors.get("card_bg")
        )
        count_label.pack(pady=(5, 15))  # Reduced top padding from 10 to 5
        
        # Favorite stats
        fav_difficulty = self.analytics_data.get('favorite_difficulty', 'N/A')
        fav_type = self.analytics_data.get('favorite_type', 'N/A')
        
        if fav_difficulty != 'N/A':
            diff_label = tk.Label(
                circle_bg_frame,
                text=f"Favorite Difficulty: {fav_difficulty}",
                font=("Segoe UI", 10),
                fg=colors.get("text_secondary"),
                bg=colors.get("card_bg")
            )
            diff_label.pack(pady=(0, 5))
        
        if fav_type != 'N/A':
            type_label = tk.Label(
                circle_bg_frame,
                text=f"Favorite Type: {fav_type}",
                font=("Segoe UI", 10),
                fg=colors.get("text_secondary"),
                bg=colors.get("card_bg")
            )
            type_label.pack(pady=(0, 10))  # Reduced bottom padding from 15 to 10
