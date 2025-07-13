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
        }