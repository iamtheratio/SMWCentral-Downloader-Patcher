"""
Dashboard Analytics Engine
Handles all data calculation and processing for the dashboard
"""
import json
import os
import sys
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import statistics

# Add path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

class DashboardAnalytics:
    def __init__(self, data_manager):
        self.data_manager = data_manager
        self.analytics_data = {}
        self.date_filter = "all_time"  # Default filter
        
    def load_analytics_data(self, date_filter="all_time"):
        """Load and calculate all analytics data with optional date filtering"""
        self.date_filter = date_filter
        
        # Get different datasets for different metric types
        # Inventory metrics (exclude obsolete): Total Hacks, Total Exits, Completion Rate
        current_hacks = self.data_manager.get_all_hacks(include_obsolete=False)
        current_data = {hack['id']: self.data_manager.data[hack['id']] for hack in current_hacks if hack['id'] in self.data_manager.data}
        
        # Completion metrics (include obsolete): Completed Hacks, Completed Exits, Time metrics, Line Graph
        all_hacks = self.data_manager.get_all_hacks(include_obsolete=True)
        all_data = {hack['id']: self.data_manager.data[hack['id']] for hack in all_hacks if hack['id'] in self.data_manager.data}
        
        self.analytics_data = {
            'total_hacks': len(current_data),  # Exclude obsolete
            'completed_hacks': 0,
            'completion_rate': 0.0,
            'completion_velocity': 0.0,
            'avg_time_per_hack': 0.0,
            'avg_time_per_exit': 0.0,
            'completed_exits': 0,  # Exits from hacks completed in the time period
            'total_exits': 0,  # Exits from all current (non-obsolete) hacks
            'completion_by_difficulty': {},
            'completion_by_type': {},
            'rating_distribution': {},
            'recent_completions': [],
            'filtered_completed': 0,
            'favorite_difficulty': 'N/A',
            'favorite_type': 'N/A',
            'top_rated': [],
            'hardest_completed': [],
            'perfectionist_score': 0,
            'longest_streak': 0,
            'current_streak': 0,
            'completion_streak': 0,
            'time_progression': {}  # NEW: Time progression data for charts
        }
        
        # Store both datasets for use in different calculations
        self.current_data = current_data  # For inventory metrics
        self.all_data = all_data  # For completion metrics
        
        self._calculate_basic_stats()
        self._calculate_completion_data()
        self._calculate_time_metrics()
        self._calculate_streaks()
        self._calculate_time_progression()  # NEW: Calculate time progression data
        
        return self.analytics_data
    
    def _should_include_hack(self, hack_data):
        """Check if hack should be included based on date filter"""
        if self.date_filter == "all_time":
            return True
            
        completed_date = hack_data.get('completed_date')
        if not completed_date or not hack_data.get('completed', False):
            return False
            
        try:
            date_obj = datetime.strptime(completed_date, '%Y-%m-%d')
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
            else:
                return True
                
            return date_obj >= filter_date
        except ValueError:
            return False
    
    def _calculate_basic_stats(self):
        """Calculate basic completion statistics"""
        completed_hacks = []
        all_ratings = []
        completion_dates = []
        
        # Calculate total exits from current (non-obsolete) hacks only
        total_exits = 0
        for hack_id, hack_data in self.current_data.items():
            exits = hack_data.get('exits', 0)
            if isinstance(exits, str):
                try:
                    exits = int(exits)
                except (ValueError, TypeError):
                    exits = 0
            if exits > 0:
                total_exits += exits
        
        # Calculate completion rate using current (non-obsolete) hacks only
        total_completed_current = 0
        for hack_id, hack_data in self.current_data.items():
            if hack_data.get('completed', False):
                total_completed_current += 1
        
        # For completion metrics, use ALL hacks (including obsolete)
        for hack_id, hack_data in self.all_data.items():
            if hack_data.get('completed', False):
                # Check if this hack should be included based on date filter for other metrics
                if self._should_include_hack(hack_data):
                    completed_hacks.append(hack_data)
                    self.analytics_data['completed_hacks'] += 1
                    
                    # Collect ratings
                    rating = hack_data.get('personal_rating')
                    if rating and rating != 'Not Rated':
                        try:
                            rating_val = int(rating)
                            if 1 <= rating_val <= 5:  # Only accept valid ratings 1-5
                                all_ratings.append(rating_val)
                        except (ValueError, TypeError):
                            pass
                    
                    # Collect completion dates
                    if hack_data.get('completed_date'):
                        try:
                            date_obj = datetime.strptime(hack_data['completed_date'], '%Y-%m-%d')
                            completion_dates.append(date_obj)
                        except ValueError:
                            pass
        
        # Store completion rate based on current (non-obsolete) hacks
        self.analytics_data['total_exits'] = total_exits
        if self.analytics_data['total_hacks'] > 0:
            self.analytics_data['completion_rate'] = (
                total_completed_current / self.analytics_data['total_hacks']
            ) * 100
        
        # Calculate average rating
        if all_ratings:
            self.analytics_data['average_rating'] = sum(all_ratings) / len(all_ratings)
        
        # Calculate velocity (completions per month)
        if completion_dates:
            completion_dates.sort()
            time_span = (completion_dates[-1] - completion_dates[0]).days
            months_span = max(1, time_span / 30.44)
            self.analytics_data['completion_velocity'] = len(completion_dates) / months_span
        
        # Recent completions (last 30 days)
        thirty_days_ago = datetime.now() - timedelta(days=30)
        self.analytics_data['recent_completions'] = [
            d for d in completion_dates if d >= thirty_days_ago
        ]
    
    def _calculate_completion_data(self):
        """Calculate completion data by difficulty and type"""
        difficulty_stats = defaultdict(lambda: {'completed': 0, 'total': 0})
        type_stats = defaultdict(lambda: {'completed': 0, 'total': 0})
        rating_counts = defaultdict(int)
        
        # Calculate totals using current (non-obsolete) hacks only
        for hack_id, hack_data in self.current_data.items():
            difficulty = hack_data.get('current_difficulty', 'Unknown')
            hack_types = hack_data.get('hack_types', [hack_data.get('hack_type', 'Unknown')])
            
            # Count difficulty and type totals from current hacks
            difficulty_stats[difficulty]['total'] += 1
            for hack_type in hack_types:
                type_stats[hack_type]['total'] += 1
        
        # Calculate completed stats using all hacks (including obsolete)
        for hack_id, hack_data in self.all_data.items():
            difficulty = hack_data.get('current_difficulty', 'Unknown')
            hack_types = hack_data.get('hack_types', [hack_data.get('hack_type', 'Unknown')])
            completed = hack_data.get('completed', False)
            rating = hack_data.get('personal_rating')
            
            # Only count completed hacks that pass the date filter
            if completed and self._should_include_hack(hack_data):
                # Count difficulty completions (once per hack)
                difficulty_stats[difficulty]['completed'] += 1
                
                # Count type completions (once per type for multi-type hacks)
                for hack_type in hack_types:
                    type_stats[hack_type]['completed'] += 1
                
                # Rating distribution (only for filtered completed hacks)
                if rating and rating != 'Not Rated':
                    try:
                        rating_val = int(rating)
                        if 1 <= rating_val <= 5:  # Only accept valid ratings 1-5
                            rating_counts[rating_val] += 1
                    except (ValueError, TypeError):
                        pass
        
        self.analytics_data['completion_by_difficulty'] = dict(difficulty_stats)
        self.analytics_data['completion_by_type'] = dict(type_stats)
        self.analytics_data['rating_distribution'] = dict(rating_counts)
        
        # Find favorites
        max_difficulty = max(difficulty_stats.items(), 
                           key=lambda x: x[1]['completed'], default=(None, None))
        if max_difficulty[0] and max_difficulty[1]['completed'] > 0:
            self.analytics_data['favorite_difficulty'] = max_difficulty[0]
        
        max_type = max(type_stats.items(), 
                      key=lambda x: x[1]['completed'], default=(None, None))
        if max_type[0] and max_type[1]['completed'] > 0:
            self.analytics_data['favorite_type'] = max_type[0]
    
    def _calculate_time_metrics(self):
        """Calculate time-based performance metrics"""
        total_time = 0
        completed_count = 0
        
        # Separate tracking for exit calculations
        exit_based_total_time = 0
        exit_based_total_exits = 0
        
        # Calculate completed exits SEPARATELY from time metrics (don't require time_to_beat)
        completed_exits = 0
        for hack_id, hack_data in self.all_data.items():
            if not hack_data.get('completed', False):
                continue
                
            # Only include if it passes the date filter
            if not self._should_include_hack(hack_data):
                continue
                
            # Count exits from ALL completed hacks (regardless of time_to_beat)
            exits = hack_data.get('exits', 0)
            if isinstance(exits, str):
                try:
                    exits = int(exits)
                except (ValueError, TypeError):
                    exits = 0
            
            if exits > 0:
                completed_exits += exits
        
        # Now calculate time-based metrics (these DO require time_to_beat > 0)
        for hack_id, hack_data in self.all_data.items():
            if not hack_data.get('completed', False):
                continue
                
            # Only include if it passes the date filter
            if not self._should_include_hack(hack_data):
                continue
                
            time_to_beat = hack_data.get('time_to_beat', 0)
            exits = hack_data.get('exits', 0)
            
            # Convert to numeric
            if isinstance(time_to_beat, str):
                try:
                    time_to_beat = float(time_to_beat)
                except (ValueError, TypeError):
                    time_to_beat = 0
            
            if isinstance(exits, str):
                try:
                    exits = int(exits)
                except (ValueError, TypeError):
                    exits = 0
            
            # Only include in time calculations if hack has time_to_beat data
            if time_to_beat > 0:
                total_time += time_to_beat
                completed_count += 1
                
                # Only include in exit calculations if hack has BOTH time and exit data
                if exits > 0:
                    exit_based_total_time += time_to_beat
                    exit_based_total_exits += exits
        
        # Store completed exits (calculated independently of time_to_beat)
        self.analytics_data['completed_exits'] = completed_exits
        
        # Calculate averages (convert to hours)
        if completed_count > 0:
            self.analytics_data['avg_time_per_hack'] = (total_time / completed_count) / 3600
            
            # Use only time and exits from hacks that have both pieces of data
            if exit_based_total_exits > 0:
                self.analytics_data['avg_time_per_exit'] = (exit_based_total_time / exit_based_total_exits) / 3600
    
    def _calculate_streaks(self):
        """Calculate completion streaks"""
        completion_dates = []
        
        for hack_data in self.data_manager.data.values():
            if hack_data.get('completed', False) and hack_data.get('completed_date'):
                try:
                    date_obj = datetime.strptime(hack_data['completed_date'], '%Y-%m-%d')
                    completion_dates.append(date_obj)
                except ValueError:
                    continue
        
        if not completion_dates:
            return
        
        # Sort dates
        unique_dates = sorted(set(completion_dates))
        
        # Calculate streaks
        longest_streak = 0
        current_streak = 0
        streak_from_today = 0
        
        today = datetime.now().date()
        
        # Check current streak from today backwards
        for i in range(len(unique_dates) - 1, -1, -1):
            date = unique_dates[i].date()
            days_diff = (today - date).days
            
            if days_diff <= streak_from_today + 1:
                streak_from_today += 1
            else:
                break
        
        # Calculate longest streak
        for i in range(len(unique_dates)):
            if i == 0:
                current_streak = 1
            else:
                days_diff = (unique_dates[i] - unique_dates[i-1]).days
                if days_diff <= 1:
                    current_streak += 1
                else:
                    longest_streak = max(longest_streak, current_streak)
                    current_streak = 1
        
        longest_streak = max(longest_streak, current_streak)
        
        self.analytics_data['longest_streak'] = longest_streak
        self.analytics_data['current_streak'] = streak_from_today
        self.analytics_data['completion_streak'] = streak_from_today if streak_from_today > 0 else longest_streak

    def _calculate_time_progression(self):
        """Calculate average completion time by difficulty per month for the last 6 months"""
        from collections import defaultdict
        import calendar
        
        # Calculate rolling 6 months from current date
        now = datetime.now()
        six_months_ago = now - timedelta(days=180)  # Approximate 6 months
        
        # Group completions by month and difficulty/type
        monthly_data = defaultdict(lambda: defaultdict(list))  # month -> difficulty -> [times]
        
        # Use all data (including obsolete) for time progression since this is completion-based
        for hack_id, hack_data in self.all_data.items():
            if not hack_data.get('completed', False):
                continue
                
            completed_date = hack_data.get('completed_date')
            if not completed_date:
                continue
                
            try:
                date_obj = datetime.strptime(completed_date, '%Y-%m-%d')
                if date_obj < six_months_ago:
                    continue
                    
                # Get month key (YYYY-MM format)
                month_key = date_obj.strftime('%Y-%m')
                
                difficulty = hack_data.get('current_difficulty', 'Unknown')
                # Use new hack_types array - include hack in all its type categories for time progression
                hack_types = hack_data.get('hack_types', [hack_data.get('hack_type', 'standard')])
                time_to_beat = hack_data.get('time_to_beat', 0)
                
                if time_to_beat > 0:
                    # Convert to hours
                    time_hours = time_to_beat / 3600
                    # Add entry for each hack type (so multi-type hacks appear in all relevant type filters)
                    for hack_type in hack_types:
                        monthly_data[month_key][difficulty].append({
                            'time': time_hours,
                            'type': hack_type
                        })
                    
            except ValueError:
                continue
        
        # Generate all months in the 6-month range
        progression_data = {}
        current_date = six_months_ago.replace(day=1)  # Start of month
        
        while current_date <= now:
            month_key = current_date.strftime('%Y-%m')
            month_name = current_date.strftime('%b %Y')  # e.g., "Jan 2025"
            
            progression_data[month_key] = {
                'month_name': month_name,
                'difficulties': {}
            }
            
            # Calculate average time per difficulty for this month
            if month_key in monthly_data:
                for difficulty, completions in monthly_data[month_key].items():
                    if completions:
                        avg_time = sum(c['time'] for c in completions) / len(completions)
                        progression_data[month_key]['difficulties'][difficulty] = {
                            'avg_time': avg_time,
                            'count': len(completions),
                            'types': list(set(c['type'] for c in completions))
                        }
            
            # Move to next month
            if current_date.month == 12:
                current_date = current_date.replace(year=current_date.year + 1, month=1)
            else:
                current_date = current_date.replace(month=current_date.month + 1)
        
        self.analytics_data['time_progression'] = progression_data
