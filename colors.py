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
            
            # UI element colors
            "api_delay": "#0078d4",
            "version_label": "#888888",
            "description": "#888888"
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
            
            # UI element colors
            "api_delay": "#0078d4",
            "version_label": "#666666",
            "description": "#888888"
        }