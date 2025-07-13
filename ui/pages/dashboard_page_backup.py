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
        self.modular_dashboard._refresh_dashboard()
    
    def cleanup(self):
        """Cleanup when switching pages"""
        if hasattr(self.modular_dashboard, 'cleanup'):
            self.modular_dashboard.cleanup()

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
        
        # Advanced analytics sections
        self._create_efficiency_insights_section()
        self._create_goals_and_achievements_section()
        
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
                'avg_time_per_hack': 0.0,  # NEW: Average time to beat per hack (hours)
                'avg_time_per_exit': 0.0,  # NEW: Average time per exit across all hacks
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
            
            # NEW: Calculate time-based metrics
            self._calculate_time_metrics(processed_data)
            
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
        
        avg_time_per_hack = self.analytics_data.get('avg_time_per_hack', 0.0)
        self._create_large_metric_card(
            bottom_row, "AVG TIME PER HACK", 
            f"{avg_time_per_hack:.1f}h" if avg_time_per_hack > 0 else "N/A",
            "⏱️", colors.get("accent"), 0, 1
        )
        
        # NEW: Average time per exit metric
        avg_time_per_exit = self.analytics_data.get('avg_time_per_exit', 0.0)
        self._create_large_metric_card(
            bottom_row, "AVG TIME PER EXIT",
            f"{avg_time_per_exit:.2f}h" if avg_time_per_exit > 0 else "N/A",
            "🚪", colors.get("info"), 0, 2
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
            fg=colors.get("text"),
            bg=colors.get("app_bg")
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
        canvas.configure(bg=colors.get("chart_bg"))
        inner_fill = colors.get("chart_bg")
        
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
        colors = get_colors()
        
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
                foreground=colors.get("text_secondary")
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
        
        # Advanced analytics sections
        self._create_efficiency_insights_section()
        self._create_goals_and_achievements_section()
        
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
        
        # Time progression chart (full width below other charts)
        time_chart_frame = ttk.Frame(charts_frame)
        time_chart_frame.pack(fill="x", pady=(15, 0))
        self._create_time_progression_chart(time_chart_frame)
    
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
        
        # Load processed data to check for special types
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
        
        # REPLACED: AVG TIME PER HACK (replaces velocity metric)
        avg_time_per_hack = self.analytics_data.get('avg_time_per_hack', 0.0)
        self._create_large_metric_card(
            bottom_row, "AVG TIME PER HACK", 
            f"{avg_time_per_hack:.1f}h" if avg_time_per_hack > 0 else "N/A",
            "⏱️", colors.get("text"), 0, 1  # Changed to text color
        )
        
        # REPLACED: AVG TIME PER EXIT (replaces streak metric)
        avg_time_per_exit = self.analytics_data.get('avg_time_per_exit', 0.0)
        self._create_large_metric_card(
            bottom_row, "AVG TIME PER EXIT",
            f"{avg_time_per_exit:.2f}h" if avg_time_per_exit > 0 else "N/A",
            "🚪", colors.get("text"), 0, 2
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
    
    def _calculate_time_metrics(self, processed_data):
        """Calculate time-based performance metrics"""
        total_time = 0
        total_exits = 0
        completed_count = 0
        
        for hack_id, hack_data in processed_data.items():
            if not hack_data.get('completed', False):
                continue
                
            # Get time to beat (should be in seconds from v3.1)
            time_to_beat = hack_data.get('time_to_beat', 0)
            if isinstance(time_to_beat, str):
                try:
                    # Try to parse if it's still in string format
                    time_to_beat = float(time_to_beat)
                except (ValueError, TypeError):
                    time_to_beat = 0
            
            # Get exit count (from v3.1 API data)
            exits = hack_data.get('exits', 0)
            if isinstance(exits, str):
                try:
                    exits = int(exits)
                except (ValueError, TypeError):
                    exits = 0
            
            if time_to_beat > 0:
                total_time += time_to_beat
                completed_count += 1
                
                if exits > 0:
                    total_exits += exits
        
        # Calculate averages
        if completed_count > 0:
            # Convert seconds to hours for better readability
            self.analytics_data['avg_time_per_hack'] = (total_time / completed_count) / 3600
            
            if total_exits > 0:
                # Average time per exit (also in hours)
                self.analytics_data['avg_time_per_exit'] = (total_time / total_exits) / 3600
            else:
                self.analytics_data['avg_time_per_exit'] = 0
        else:
            self.analytics_data['avg_time_per_hack'] = 0
            self.analytics_data['avg_time_per_exit'] = 0
    
    def _create_time_progression_chart(self, parent):
        """Create time progression chart showing improvement over 6 months"""
        colors = get_colors()
        
        chart_frame = ttk.LabelFrame(parent, text="Performance Progression (Last 6 Months)", padding=5)
        chart_frame.pack(fill="x", pady=5)
        
        # Calculate 6-month data
        progression_data = self._calculate_time_progression_data()
        
        if not progression_data['months']:
            no_data_label = ttk.Label(chart_frame, text="No completion data available for time progression analysis", 
                                    foreground=colors["text_secondary"])
            no_data_label.pack(pady=20)
            return
        
        # Create canvas for chart
        canvas_frame = ttk.Frame(chart_frame)
        canvas_frame.pack(fill="x", padx=5, pady=5)
        
        canvas = tk.Canvas(canvas_frame, height=200, bg=colors["card_bg"], highlightthickness=0)
        canvas.pack(fill="x")
        
        # Chart dimensions
        margin = 40
        chart_width = canvas.winfo_reqwidth() - (2 * margin)
        chart_height = 160
        
        # Wait for canvas to be drawn
        canvas.update_idletasks()
        actual_width = canvas.winfo_width()
        chart_width = actual_width - (2 * margin)
        
        months = progression_data['months']
        avg_time_data = progression_data['avg_time_per_hack']
        avg_exit_data = progression_data['avg_time_per_exit']
        
        if len(months) < 2:
            no_data_label = ttk.Label(chart_frame, text="Need at least 2 months of data for progression analysis", 
                                    foreground=colors["text_secondary"])
            no_data_label.pack(pady=10)
            return
        
        # Find max values for scaling
        max_time = max(max(avg_time_data, default=0), max(avg_exit_data, default=0))
        if max_time == 0:
            max_time = 1
        
        # Draw grid lines
        for i in range(5):
            y = margin + (i * chart_height / 4)
            canvas.create_line(margin, y, margin + chart_width, y, 
                             fill=colors["border"], width=1, dash=(2, 2))
        
        # Draw axes
        canvas.create_line(margin, margin, margin, margin + chart_height, 
                         fill=colors["text"], width=2)
        canvas.create_line(margin, margin + chart_height, margin + chart_width, margin + chart_height, 
                         fill=colors["text"], width=2)
        
        # Plot data points and lines
        if len(months) > 1:
            step_x = chart_width / (len(months) - 1)
            
            # Draw avg time per hack line (blue)
            prev_x, prev_y = None, None
            for i, (month, time_val) in enumerate(zip(months, avg_time_data)):
                x = margin + (i * step_x)
                y = margin + chart_height - (time_val / max_time * chart_height)
                
                # Draw point
                canvas.create_oval(x-3, y-3, x+3, y+3, fill=colors["accent"], outline=colors["accent"])
                
                # Draw line to previous point
                if prev_x is not None:
                    canvas.create_line(prev_x, prev_y, x, y, fill=colors["accent"], width=2)
                
                prev_x, prev_y = x, y
            
            # Draw avg time per exit line (green)
            prev_x, prev_y = None, None
            for i, (month, time_val) in enumerate(zip(months, avg_exit_data)):
                x = margin + (i * step_x)
                y = margin + chart_height - (time_val / max_time * chart_height)
                
                # Draw point
                canvas.create_oval(x-3, y-3, x+3, y+3, fill=colors["success"], outline=colors["success"])
                
                # Draw line to previous point
                if prev_x is not None:
                    canvas.create_line(prev_x, prev_y, x, y, fill=colors["success"], width=2)
                
                prev_x, prev_y = x, y
        
        # Add month labels
        if len(months) > 1:
            step_x = chart_width / (len(months) - 1)
            for i, month in enumerate(months):
                x = margin + (i * step_x)
                canvas.create_text(x, margin + chart_height + 15, text=month, 
                                 fill=colors["text"], font=("Segoe UI", 8))
        
        # Add Y-axis labels
        for i in range(5):
            y = margin + (i * chart_height / 4)
            value = max_time * (1 - i/4)
            canvas.create_text(margin - 10, y, text=f"{value:.1f}h", 
                             fill=colors["text"], font=("Segoe UI", 8), anchor="e")
        
        # Add legend
        legend_frame = ttk.Frame(chart_frame)
        legend_frame.pack(pady=5)
        
        legend1 = tk.Label(legend_frame, text="● Avg Time per Hack", 
                          fg=colors["accent"], bg=colors["card_bg"], font=("Segoe UI", 9))
        legend1.pack(side="left", padx=10)
        
        legend2 = tk.Label(legend_frame, text="● Avg Time per Exit", 
                          fg=colors["success"], bg=colors["card_bg"], font=("Segoe UI", 9))
        legend2.pack(side="left", padx=10)

    def _calculate_time_progression_data(self):
        """Calculate time progression data for the last 6 months"""
        now = datetime.now()
        months_data = {}
        
        # Initialize 6 months of data
        for i in range(6):
            month_date = now - timedelta(days=30 * i)
            month_key = month_date.strftime('%Y-%m')
            month_display = month_date.strftime('%b')
            months_data[month_key] = {
                'display': month_display,
                'total_time': 0,
                'total_exits': 0,
                'hack_count': 0,
                'times': []
            }
        
        # Process completed hacks
        for hack_id, hack_data in self.data_manager.data.items():
            if not hack_data.get('completed', False):
                continue
                
            completed_date = hack_data.get('completed_date', '')
            if not completed_date:
                continue
                
            try:
                date_obj = datetime.strptime(completed_date, '%Y-%m-%d')
                month_key = date_obj.strftime('%Y-%m')
                
                if month_key in months_data:
                    time_to_beat = hack_data.get('time_to_beat', 0)
                    exits = hack_data.get('exits', 0)
                    
                    # Convert to numeric if needed
                    if isinstance(time_to_beat, str):
                        try:
                            time_to_beat = float(time_to_beat)
                        except:
                            time_to_beat = 0
                    
                    if isinstance(exits, str):
                        try:
                            exits = int(exits)
                        except:
                            exits = 0
                    
                    if time_to_beat > 0:
                        months_data[month_key]['total_time'] += time_to_beat
                        months_data[month_key]['hack_count'] += 1
                        months_data[month_key]['times'].append(time_to_beat)
                        
                        if exits > 0:
                            months_data[month_key]['total_exits'] += exits
                            
            except ValueError:
                continue
        
        # Calculate averages and prepare final data
        months = []
        avg_time_per_hack = []
        avg_time_per_exit = []
        
        # Sort months chronologically (oldest first)
        sorted_months = sorted(months_data.keys(), reverse=True)[:6]
        sorted_months.reverse()  # Oldest to newest for chart
        
        for month_key in sorted_months:
            data = months_data[month_key]
            if data['hack_count'] > 0:
                months.append(data['display'])
                
                # Average time per hack (convert seconds to hours)
                avg_hack_time = (data['total_time'] / data['hack_count']) / 3600
                avg_time_per_hack.append(avg_hack_time)
                
                # Average time per exit
                if data['total_exits'] > 0:
                    avg_exit_time = (data['total_time'] / data['total_exits']) / 3600
                    avg_time_per_exit.append(avg_exit_time)
                else:
                    avg_time_per_exit.append(0)
        
        return {
            'months': months,
            'avg_time_per_hack': avg_time_per_hack,
            'avg_time_per_exit': avg_time_per_exit
        }

    def _create_efficiency_insights_section(self):
        """Create advanced efficiency insights section"""
        colors = get_colors()
        
        insights_frame = ttk.LabelFrame(self.scrollable_frame, text="🎯 Performance Insights", padding=10)
        insights_frame.pack(fill="x", padx=5, pady=(10, 15))
        
        # Create three column layout for efficiency metrics
        insights_container = ttk.Frame(insights_frame)
        insights_container.pack(fill="x", expand=True)
        
        for i in range(3):
            insights_container.columnconfigure(i, weight=1)
        
        # Speed Analysis
        speed_frame = ttk.LabelFrame(insights_container, text="⚡ Speed Analysis", padding=8)
        speed_frame.grid(row=0, column=0, padx=2, pady=2, sticky="nsew")
        
        # Consistency Metrics  
        consistency_frame = ttk.LabelFrame(insights_container, text="📊 Consistency", padding=8)
        consistency_frame.grid(row=0, column=1, padx=2, pady=2, sticky="nsew")
        
        # Improvement Tracking
        improvement_frame = ttk.LabelFrame(insights_container, text="📈 Progress", padding=8)
        improvement_frame.grid(row=0, column=2, padx=2, pady=2, sticky="nsew")
        
        self._populate_speed_analysis(speed_frame)
        self._populate_consistency_metrics(consistency_frame)
        self._populate_improvement_tracking(improvement_frame)
    
    def _populate_speed_analysis(self, parent):
        """Populate speed analysis metrics"""
        colors = get_colors()
        
        # Calculate speed metrics
        speed_data = self._calculate_advanced_speed_metrics()
        
        metrics = [
            ("🏃 Fastest Clear", f"{speed_data['fastest_time']:.1f}h", speed_data['fastest_hack']),
            ("🚪 Best Exit Rate", f"{speed_data['best_exit_rate']:.1f}/h", "Exits per hour"),
            ("📊 Speed Trend", speed_data['speed_trend'], "Recent vs Overall"),
            ("🎯 Sweet Spot", speed_data['optimal_difficulty'], "Most efficient level")
        ]
        
        for icon_label, value, description in metrics:
            self._create_insight_item(parent, icon_label, value, description, colors)
    
    def _populate_consistency_metrics(self, parent):
        """Populate consistency metrics"""
        colors = get_colors()
        
        consistency_data = self._calculate_consistency_data()
        
        metrics = [
            ("📏 Time Variance", f"±{consistency_data['variance']:.1f}h", "Completion time spread"),
            ("🎲 Pattern", consistency_data['pattern'], "Your playing style"),
            ("⚖️ Balance Score", f"{consistency_data['balance']:.0f}%", "Difficulty distribution"),
            ("🔄 Regularity", consistency_data['regularity'], "Completion frequency")
        ]
        
        for icon_label, value, description in metrics:
            self._create_insight_item(parent, icon_label, value, description, colors)
    
    def _populate_improvement_tracking(self, parent):
        """Populate improvement tracking metrics"""
        colors = get_colors()
        
        improvement_data = self._calculate_improvement_data()
        
        metrics = [
            ("📈 Speed Change", improvement_data['speed_improvement'], "Time efficiency trend"),
            ("🎯 Accuracy Trend", improvement_data['accuracy_trend'], "Completion success rate"),
            ("🏆 Skill Level", improvement_data['skill_assessment'], "Estimated ability"),
            ("🔮 Next Goal", improvement_data['next_milestone'], "Recommended target")
        ]
        
        for icon_label, value, description in metrics:
            self._create_insight_item(parent, icon_label, value, description, colors)
    
    def _create_insight_item(self, parent, label, value, description, colors):
        """Create a single insight item"""
        item_frame = tk.Frame(parent)
        item_frame.pack(fill="x", pady=2)
        
        # Main metric
        tk.Label(
            item_frame,
            text=f"{label}: {value}",
            font=("Segoe UI", 9, "bold"),
            fg=colors.get("text"),
            anchor="w"
        ).pack(fill="x")
        
        # Description
        tk.Label(
            item_frame,
            text=description,
            font=("Segoe UI", 8),
            fg=colors.get("text_secondary"),
            anchor="w"
        ).pack(fill="x")
    
    def _calculate_advanced_speed_metrics(self):
        """Calculate advanced speed metrics"""
        import statistics
        from collections import defaultdict
        import statistics
        
        fastest_time = float('inf')
        fastest_hack = "None"
        exit_rates = []
        recent_times = []
        all_times = []
        difficulty_times = defaultdict(list)
        
        now = datetime.now()
        three_months_ago = now - timedelta(days=90)
        
        for hack_id, hack_data in self.data_manager.data.items():
            if not hack_data.get('completed', False):
                continue
                
            time_to_beat = hack_data.get('time_to_beat', 0)
            exits = hack_data.get('exits', 0)
            difficulty = hack_data.get('current_difficulty', 'Unknown')
            completed_date = hack_data.get('completed_date', '')
            
            # Convert to numeric
            if isinstance(time_to_beat, str):
                try:
                    time_to_beat = float(time_to_beat)
                except:
                    continue
            
            if isinstance(exits, str):
                try:
                    exits = int(exits)
                except:
                    exits = 0
            
            if time_to_beat <= 0:
                continue
                
            time_hours = time_to_beat / 3600
            all_times.append(time_hours)
            difficulty_times[difficulty].append(time_hours)
            
            # Track fastest
            if time_hours < fastest_time:
                fastest_time = time_hours
                fastest_hack = hack_data.get('title', 'Unknown')[:20]
            
            # Exit rate calculation
            if exits > 0:
                exit_rate = exits / time_hours
                exit_rates.append(exit_rate)
            
            # Recent times
            if completed_date:
                try:
                    date_obj = datetime.strptime(completed_date, '%Y-%m-%d')
                    if date_obj >= three_months_ago:
                        recent_times.append(time_hours)
                except:
                    pass
        
        # Calculate trends
        speed_trend = "📊 Stable"
        if recent_times and all_times and len(all_times) >= 5:
            recent_avg = statistics.mean(recent_times)
            overall_avg = statistics.mean(all_times)
            change_pct = ((overall_avg - recent_avg) / overall_avg) * 100
            
            if change_pct > 15:
                speed_trend = "🚀 Accelerating"
            elif change_pct < -15:
                speed_trend = "🐌 Slowing"
        
        # Find optimal difficulty
        optimal_difficulty = "Unknown"
        best_avg = float('inf')
        for diff, times in difficulty_times.items():
            if len(times) >= 2:
                avg_time = statistics.mean(times)
                if avg_time < best_avg:
                    best_avg = avg_time
                    optimal_difficulty = diff
        
        return {
            'fastest_time': fastest_time if fastest_time != float('inf') else 0,
            'fastest_hack': fastest_hack,
            'best_exit_rate': max(exit_rates) if exit_rates else 0,
            'speed_trend': speed_trend,
            'optimal_difficulty': optimal_difficulty
        }
    
    def _calculate_consistency_data(self):
        """Calculate consistency metrics"""
        import statistics
        
        completion_times = []
        difficulty_counts = defaultdict(int)
        total_completed = 0
       
        completion_gaps = []
        last_date = None
        
        for hack_id, hack_data in self.data_manager.data.items():
            if not hack_data.get('completed', False):
                continue
                
            time_to_beat = hack_data.get('time_to_beat', 0)
            difficulty = hack_data.get('current_difficulty', 'Unknown')
            completed_date = hack_data.get('completed_date', '')
            
            if isinstance(time_to_beat, str):
                try:
                    time_to_beat = float(time_to_beat)
                except:
                    continue
            
            if time_to_beat > 0:
                completion_times.append(time_to_beat / 3600)
                difficulty_counts[difficulty] += 1
                total_completed += 1
            
            # Track completion gaps
            if completed_date:
                try:
                    date_obj = datetime.strptime(completed_date, '%Y-%m-%d')
                    if last_date:
                        gap = (date_obj - last_date).days
                        completion_gaps.append(gap)
                    last_date = date_obj
                except:
                    pass
        
        # Calculate variance
        variance = statistics.stdev(completion_times) if len(completion_times) > 1 else 0
        
        # Determine pattern
        pattern = "Balanced"
        if completion_times:
            avg_time = statistics.mean(completion_times)
            if variance < 2:
                pattern = "🎯 Consistent"
            elif avg_time < 3:
                pattern = "⚡ Speed Runner"
            elif avg_time > 15:
                pattern = "🐌 Marathon"
            elif variance > 10:
                pattern = "🎲 Variable"
        
        # Calculate balance score
        total_diffs = sum(difficulty_counts.values())
        balance_score = 0
        if total_diffs > 0:
            # Ideal distribution would be even across difficulties
            ideal_per_diff = total_diffs / max(1, len(difficulty_counts))
            deviations = [abs(count - ideal_per_diff) for count in difficulty_counts.values()]
            balance_score = max(0, 100 - (sum(deviations) / total_diffs * 100))
        
        # Calculate regularity
        regularity = "📈 Improving"
        if completion_gaps:
            avg_gap = statistics.mean(completion_gaps)
            if avg_gap <= 7:
                regularity = "🔥 Daily"
            elif avg_gap <= 14:
                regularity = "📅 Weekly"
            elif avg_gap <= 30:
                regularity = "📆 Monthly"
            else:
                regularity = "🐢 Sporadic"
        
        return {
            'variance': variance,
            'pattern': pattern,
            'balance': balance_score,
            'regularity': regularity
        }
    
    def _calculate_improvement_data(self):
        """Calculate improvement tracking data"""
        import statistics
        
        completion_times = []
        completion_dates = []
        difficulties_completed = set()
        
        for hack_id, hack_data in self.data_manager.data.items():
            if not hack_data.get('completed', False):
                continue
                
            time_to_beat = hack_data.get('time_to_beat', 0)
            difficulty = hack_data.get('current_difficulty', 'Unknown')
            completed_date = hack_data.get('completed_date', '')
            
            if isinstance(time_to_beat, str):
                try:
                    time_to_beat = float(time_to_beat)
                except:
                    continue
            
            if time_to_beat > 0 and completed_date:
                try:
                    date_obj = datetime.strptime(completed_date, '%Y-%m-%d')
                    completion_times.append((date_obj, time_to_beat / 3600))
                    completion_dates.append(date_obj)
                    difficulties_completed.add(difficulty)
                except:
                    continue
        
        # Sort by date
        completion_times.sort(key=lambda x: x[0])
        
        # Calculate speed improvement
        speed_improvement = "📊 Stable"
        if len(completion_times) >= 6:
            first_third = [t[1] for t in completion_times[:len(completion_times)//3]]
            last_third = [t[1] for t in completion_times[-len(completion_times)//3:]]
            
            if first_third and last_third:
                first_avg = statistics.mean(first_third)
                last_avg = statistics.mean(last_third)
                improvement_pct = ((first_avg - last_avg) / first_avg) * 100
                
                if improvement_pct > 20:
                    speed_improvement = "🚀 +20% Faster"
                elif improvement_pct > 10:
                    speed_improvement = "📈 +10% Faster"
                elif improvement_pct < -10:
                    speed_improvement = "📉 Slowing Down"
        
        # Accuracy trend (completion frequency)
        accuracy_trend = "📊 Steady"
        if len(completion_dates) >= 3:
            recent_month = datetime.now() - timedelta(days=30)
            recent_completions = sum(1 for d in completion_dates if d >= recent_month)
            
            if recent_completions >= 10:
                accuracy_trend = "🔥 Hot Streak"
            elif recent_completions >= 5:
                accuracy_trend = "📈 Active"
            elif recent_completions <= 1:
                accuracy_trend = "😴 Quiet"
        
        # Skill assessment
        difficulty_rank = {
            'Easy': 1, 'Normal': 2, 'Hard': 3, 'Very Hard': 4,
            'Expert': 5, 'Kaizo Light': 6, 'Kaizo': 7, 'Grandmaster': 8
        }
        
        max_difficulty = 0
        for diff in difficulties_completed:
            rank = difficulty_rank.get(diff, 0)
            max_difficulty = max(max_difficulty, rank)
        
        skill_levels = {
            0: "🌱 Beginner",
            1: "🌱 Beginner", 2: "🌱 Beginner",
            3: "🌿 Intermediate", 4: "🌿 Intermediate",
            5: "🌳 Advanced", 6: "🌳 Advanced",
            7: "👹 Kaizo Master", 8: "🏆 Grandmaster"
        }
        skill_assessment = skill_levels.get(max_difficulty, "🌱 Beginner")
        
        # Next milestone
        milestones = [
            (5, "Complete 5 hacks"),
            (10, "Reach 10 completions"),
            (25, "Hit 25 hacks"),
            (50, "Achieve 50 clears"),
            (100, "Century club!")
        ]
        
        completed_count = len(completion_times)
        next_milestone = "🏆 Hall of Fame!"
        for milestone_count, description in milestones:
            if completed_count < milestone_count:
                next_milestone = f"🎯 {description}"
                break
        
        return {
            'speed_improvement': speed_improvement,
            'accuracy_trend': accuracy_trend,
            'skill_assessment': skill_assessment,
            'next_milestone': next_milestone
        }
    
    def _create_goals_and_achievements_section(self):
        """Create goals and achievements tracking section"""
        colors = get_colors()
        
        goals_frame = ttk.LabelFrame(self.scrollable_frame, text="🏆 Goals & Achievements", padding=10)
        goals_frame.pack(fill="x", padx=5, pady=(10, 15))
        
        # Create two column layout
        goals_container = ttk.Frame(goals_frame)
        goals_container.pack(fill="x", expand=True)
        
        goals_container.columnconfigure(0, weight=1)
        goals_container.columnconfigure(1, weight=1)
        
        # Current Goals
        current_goals_frame = ttk.LabelFrame(goals_container, text="🎯 Current Goals", padding=8)
        current_goals_frame.grid(row=0, column=0, padx=2, pady=2, sticky="nsew")
        
        # Recent Achievements
        achievements_frame = ttk.LabelFrame(goals_container, text="🏅 Recent Achievements", padding=8)
        achievements_frame.grid(row=0, column=1, padx=2, pady=2, sticky="nsew")
        
        self._populate_current_goals(current_goals_frame)
        self._populate_recent_achievements(achievements_frame)
    
    def _populate_current_goals(self, parent):
        """Populate current goals section"""
        colors = get_colors()
        
        goals_data = self._calculate_goals_data()
        
        for goal in goals_data['current_goals']:
            goal_frame = tk.Frame(parent)
            goal_frame.pack(fill="x", pady=3)
            
            # Goal text
            tk.Label(
                goal_frame,
                text=f"🎯 {goal['title']}",
                font=("Segoe UI", 9, "bold"),
                fg=colors.get("text"),
                anchor="w"
            ).pack(fill="x")
            
            # Progress bar
            progress_frame = tk.Frame(goal_frame)
            progress_frame.pack(fill="x", pady=1)
            
            progress_bg = tk.Frame(progress_frame, height=6, bg=colors.get("button_secondary"))
            progress_bg.pack(fill="x")
            
            if goal['progress'] > 0:
                progress_fill = tk.Frame(
                    progress_bg, 
                    height=6, 
                    bg=colors.get("accent"),
                    width=int(goal['progress'] * progress_bg.winfo_reqwidth() / 100) if goal['progress'] <= 100 else progress_bg.winfo_reqwidth()
                )
                progress_fill.place(x=0, y=0)
            
            # Progress text
            tk.Label(
                goal_frame,
                text=f"{goal['current']}/{goal['target']} ({goal['progress']:.0f}%)",
                font=("Segoe UI", 8),
                fg=colors.get("text_secondary"),
                anchor="w"
            ).pack(fill="x")
    
    def _populate_recent_achievements(self, parent):
        """Populate recent achievements section"""
        colors = get_colors()
        
        achievements_data = self._calculate_achievements_data()
        
        if not achievements_data['recent_achievements']:
            tk.Label(
                parent,
                text="🎮 Keep playing to unlock achievements!",
                font=("Segoe UI", 9),
                fg=colors.get("text_secondary"),
                anchor="w"
            ).pack(fill="x", pady=10)
            return
        
        for achievement in achievements_data['recent_achievements'][:5]:  # Show last 5
            achievement_frame = tk.Frame(parent)
            achievement_frame.pack(fill="x", pady=3)
            
            # Achievement icon and title
            tk.Label(
                achievement_frame,
                text=f"{achievement['icon']} {achievement['title']}",
                font=("Segoe UI", 9, "bold"),
                fg=colors.get("text"),
                anchor="w"
            ).pack(fill="x")
            
            # Achievement description
            tk.Label(
                achievement_frame,
                text=achievement['description'],
                font=("Segoe UI", 8),
                fg=colors.get("text_secondary"),
                anchor="w"
            ).pack(fill="x")
            
            # Date earned
            if achievement.get('date'):
                tk.Label(
                    achievement_frame,
                    text=f"Earned: {achievement['date']}",
                    font=("Segoe UI", 7),
                    fg=colors.get("text_tertiary"),
                    anchor="w"
                ).pack(fill="x")
    
    def _calculate_goals_data(self):
        """Calculate current goals based on progress"""
        completed_count = sum(1 for hack_data in self.data_manager.data.values() 
                             if hack_data.get('completed', False))
        
        # Dynamic goal calculation
        goals = []
        
        # Completion goals
        completion_milestones = [5, 10, 25, 50, 100, 200, 500]
        for milestone in completion_milestones:
            if completed_count < milestone:
                goals.append({
                    'title': f"Complete {milestone} Hacks",
                    'current': completed_count,
                    'target': milestone,
                    'progress': min(100, (completed_count / milestone) * 100)
                })
                break
        
        # Difficulty goals
        difficulty_counts = defaultdict(int)
        for hack_data in self.data_manager.data.values():
            if hack_data.get('completed', False):
                difficulty = hack_data.get('current_difficulty', 'Unknown')
                difficulty_counts[difficulty] += 1
        
        # Check for next difficulty milestone
        difficulty_progression = ['Easy', 'Normal', 'Hard', 'Very Hard', 'Expert', 'Kaizo Light', 'Kaizo']
        for i, diff in enumerate(difficulty_progression):
            if difficulty_counts[diff] < 5 and (i == 0 or difficulty_counts.get(difficulty_progression[i-1], 0) >= 3):
                goals.append({
                    'title': f"Master {diff} Difficulty",
                    'current': difficulty_counts[diff],
                    'target': 5,
                    'progress': min(100, (difficulty_counts[diff] / 5) * 100)
                })
                break
        
        # Speed goals (if time data available)
        completion_times = []
        for hack_data in self.data_manager.data.values():
            if hack_data.get('completed', False) and hack_data.get('time_to_beat'):
                try:
                    time_val = float(hack_data['time_to_beat']) / 3600  # Convert to hours
                    if time_val > 0:
                        completion_times.append(time_val)
                except:
                    continue
        
        if completion_times and len(completion_times) >= 3:
            import statistics
            avg_time = statistics.mean(completion_times)
            target_time = max(1, avg_time * 0.8)  # 20% improvement goal
            recent_times = completion_times[-5:] if len(completion_times) >= 5 else completion_times
            recent_avg = statistics.mean(recent_times)
            
            progress = min(100, max(0, ((avg_time - recent_avg) / (avg_time - target_time)) * 100))
            
            goals.append({
                'title': f"Improve Average Time",
                'current': f"{recent_avg:.1f}h",
                'target': f"{target_time:.1f}h",
                'progress': progress
            })
        
        return {'current_goals': goals}
    
    def _calculate_achievements_data(self):
        """Calculate recent achievements"""
        achievements = []
        
        completed_count = sum(1 for hack_data in self.data_manager.data.values() 
                             if hack_data.get('completed', False))
        
        # Completion milestones
        milestones = [
            (1, "🎮 First Steps", "Completed your first hack"),
            (5, "🌟 Getting Started", "Completed 5 hacks"),
            (10, "🔥 On Fire", "Reached 10 completions"),
            (25, "🚀 Quarter Century", "25 hacks conquered"),
            (50, "💎 Half Century", "50 hacks mastered"),
            (100, "👑 Century Club", "100 hacks completed"),
            (200, "🏆 Elite Player", "200 hacks beaten"),
            (500, "🎯 Legendary", "500 hack completions")
        ]
        
        for count, title, description in milestones:
            if completed_count >= count:
                achievements.append({
                    'icon': '🏅',
                    'title': title,
                    'description': description,
                    'date': 'Recently'  # Would need completion date tracking for exact dates
                })
        
        # Difficulty achievements
        difficulty_counts = defaultdict(int)
        for hack_data in self.data_manager.data.values():
            if hack_data.get('completed', False):
                difficulty = hack_data.get('current_difficulty', 'Unknown')
                difficulty_counts[difficulty] += 1
        
        difficulty_achievements = [
            ('Hard', 1, "💪 Challenge Accepted", "Completed first Hard difficulty"),
            ('Very Hard', 1, "🔥 Hardcore", "Conquered Very Hard difficulty"),
            ('Expert', 1, "🎯 Expert Level", "Mastered Expert difficulty"),
            ('Kaizo Light', 1, "😈 Kaizo Initiate", "Survived Kaizo Light"),
            ('Kaizo', 1, "👹 Kaizo Master", "Conquered true Kaizo"),
            ('Expert', 10, "🧠 Genius", "10 Expert hacks beaten"),
            ('Kaizo', 5, "🏆 Kaizo Legend", "5 Kaizo hacks mastered")
        ]
        
        for diff, req_count, title, description in difficulty_achievements:
            if difficulty_counts[diff] >= req_count:
                achievements.append({
                    'icon': '🎖️',
                    'title': title,
                    'description': description,
                    'date': 'Recently'
                })
        
        # Speed achievements (if time data available)
        completion_times = []
        for hack_data in self.data_manager.data.values():
            if hack_data.get('completed', False) and hack_data.get('time_to_beat'):
                try:
                    time_val = float(hack_data['time_to_beat']) / 3600
                    if time_val > 0:
                        completion_times.append(time_val)
                except:
                    continue
        
        if completion_times:
            fastest_time = min(completion_times)
            if fastest_time < 1:
                achievements.append({
                    'icon': '⚡',
                    'title': 'Speed Demon',
                    'description': 'Completed a hack in under 1 hour',
                    'date': 'Recently'
                })
            
            if len(completion_times) >= 5:
                import statistics
                avg_time = statistics.mean(completion_times)
                if avg_time < 5:
                    achievements.append({
                        'icon': '🏃',
                        'title': 'Efficiency Expert',
                        'description': 'Average completion time under 5 hours',
                        'date': 'Recently'
                    })
        
        # Return most recent achievements first
        return {'recent_achievements': achievements[-10:]}  # Last 10 achievements
