# colors.py
import sv_ttk

def get_colors():
    """Get color scheme based on current theme"""
    if sv_ttk.get_theme() == "dark":
        return {
            # Log text colors
            "log_bg": "#2b2b2b",
            "log_fg": "#e0e0e0",
            "error": "#ff6b6b",
            "warning": "#FFB700",
            "debug": "#16C172",
            "filter_info": "#888888",
            "applying": "#e0e0e0",
            "app_bg": "#1c1c1c",
            
            # Cancel button colors for dark mode
            "cancel_bg": "#FF4444",        # Bright red background
            "cancel_fg": "#E0E0E0",        # Light gray text (was black)
            "cancel_hover": "#FF6666",     # Lighter red on hover
            "cancel_pressed": "#DD2222",   # Darker red when pressed

            # UI element colors
            "api_delay": "#0078d4",
            "version_label": "#888888",
            "description": "#888888",
            
            # Navigation colors
            "nav_bg": "#60cdff",      # Lighter blue for dark mode (matches accent button)
            "nav_text": "#000000",    # Black text for dark mode
            "toggle_bg": "#151515",   # ADDED: Dark gray background for toggle
            
            # Dashboard card colors
            "card_bg": "#1c1c1c",     # Dark card background
            "card_border": "#1c1c1c", # Card border color
            "text": "#e0e0e0",       # Light text
            "text_secondary": "#b0b0b0", # Secondary text
            "accent": "#60cdff",      # Accent color for values
            "success": "#16C172",     # Success/completed color
            "warning": "#FFB700",     # Warning color
            "info": "#0078d4",        # Info color
            "chart_bg": "#1c1c1c",    # Chart background
            "progress_bg": "#555555", # Progress bar background
            "progress_fill": "#60cdff", # Progress bar fill
            
            # Tooltip colors - NEW
            "tooltip_bg": "#3c3c3c",  # Dark gray background
            "tooltip_fg": "#e0e0e0",  # Light gray text
            "tooltip_border": "#555555",  # Medium gray border
            
            # Difficulty line chart colors - NEW
            "diff_newcomer": "#4FC3F7",     # Light Blue
            "diff_casual": "#66BB6A",       # Light Green  
            "diff_skilled": "#FFD54F",      # Light Yellow
            "diff_advanced": "#FF8A65",     # Light Orange
            "diff_expert": "#F06292",       # Light Pink
            "diff_master": "#BA68C8",       # Light Purple
            "diff_grandmaster": "#FF5252",  # Light Red
        }
    else:
        return {
            # Log text colors
            "log_bg": "#ffffff",
            "log_fg": "#000000",
            "error": "red",
            "warning": "#C76E00",
            "debug": "#0E8A50",
            "filter_info": "#888888",
            "applying": "#000000",
            "app_bg": "#f8f9fa",
            
            # Cancel button colors for light mode
            "cancel_bg": "#DC3545",        # Bootstrap danger red (better for light mode)
            "cancel_fg": "#2C2C2C",        # Dark gray text for better contrast in light mode
            "cancel_hover": "#C82333",     # Darker red on hover
            "cancel_pressed": "#BD2130",   # Even darker red when pressed

            # UI element colors
            "api_delay": "#0078d4",
            "version_label": "#666666",
            "description": "#888888",
            
            # Navigation colors
            "nav_bg": "#0078d4",      # Darker blue for light mode (matches accent button)  
            "nav_text": "#ffffff",    # White text for light mode
            "toggle_bg": "#EEEEEE",   # ADDED: Light gray background for toggle
            
            # Dashboard card colors
            "card_bg": "#f8f9fa",     # Light card background
            "card_border": "#f8f9fa", # Card border color
            "text": "#212529",       # Dark text
            "text_secondary": "#6c757d", # Secondary text
            "accent": "#0078d4",      # Accent color for values
            "success": "#198754",     # Success/completed color
            "warning": "#fd7e14",     # Warning color
            "info": "#0dcaf0",        # Info color
            "chart_bg": "#f8f9fa",    # Chart background
            "progress_bg": "#e9ecef", # Progress bar background
            "progress_fill": "#0078d4", # Progress bar fill
            
            # Tooltip colors - NEW
            "tooltip_bg": "#ffffe0",  # Light yellow background
            "tooltip_fg": "#000000",  # Black text
            "tooltip_border": "#888888",  # Gray border
            
            # Difficulty line chart colors - NEW
            "diff_newcomer": "#1976D2",     # Blue
            "diff_casual": "#388E3C",       # Green  
            "diff_skilled": "#F57C00",      # Orange
            "diff_advanced": "#E64A19",     # Deep Orange
            "diff_expert": "#C2185B",       # Pink
            "diff_master": "#7B1FA2",       # Purple
            "diff_grandmaster": "#D32F2F",  # Red
        }