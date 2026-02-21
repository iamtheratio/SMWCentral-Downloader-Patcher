"""
UI Constants for SMWCentral Downloader & Patcher
Centralized styling and layout constants for consistent UI across all pages
"""

# Page Padding Constants
# Based on Bulk Download page settings for consistency
PAGE_PADDING = 25  # Main frame padding for all pages
SECTION_PADDING_Y = 10  # Vertical padding between sections
SECTION_PADDING_X = 0   # Horizontal padding between sections
FILTER_PADDING_TOP = 20  # Top padding for filter sections (dashboard)
FILTER_PADDING_BOTTOM = 15  # Bottom padding for filter sections

# Internal Widget Padding
LABELFRAME_PADDING = 15  # Internal padding for LabelFrame widgets (matches bulk download)
COMPONENT_INTERNAL_PADDING = 10  # Internal padding for components

# Component Spacing
COMPONENT_SPACING = 10  # Standard spacing between components
LARGE_SPACING = 20      # Larger spacing for visual separation
SMALL_SPACING = 5       # Small spacing for related elements

# Dashboard Specific
DASHBOARD_CONTENT_PADDING_X = 20  # Horizontal padding for dashboard content
DASHBOARD_CONTENT_PADDING_Y = (FILTER_PADDING_TOP, FILTER_PADDING_BOTTOM)  # Vertical padding tuple

def get_page_padding():
    """Get the standard page padding value"""
    return PAGE_PADDING

def get_section_padding():
    """Get the standard section padding tuple (x, y)"""
    return (SECTION_PADDING_X, SECTION_PADDING_Y)

def get_dashboard_content_padding():
    """Get dashboard content padding (x, y_tuple)"""
    return (DASHBOARD_CONTENT_PADDING_X, DASHBOARD_CONTENT_PADDING_Y)

def get_labelframe_padding():
    """Get the standard LabelFrame internal padding"""
    return LABELFRAME_PADDING

# Status Message Colors
# Consistent color scheme for status/notification messages across the UI
STATUS_COLOR_INFO = "#4FC3F7"      # Light blue/cyan - for in-progress messages (⏳)
STATUS_COLOR_SUCCESS = "#66BB6A"   # Green - for success messages (✅)
STATUS_COLOR_WARNING = "#FFA726"   # Orange - for warnings (⚠️)
STATUS_COLOR_ERROR = "#EF5350"     # Red - for errors (❌)

def get_status_color(status_type):
    """Get the standard status color for a given status type
    
    Args:
        status_type: One of 'info', 'success', 'warning', 'error'
    
    Returns:
        Hex color string
    """
    colors = {
        'info': STATUS_COLOR_INFO,
        'success': STATUS_COLOR_SUCCESS,
        'warning': STATUS_COLOR_WARNING,
        'error': STATUS_COLOR_ERROR
    }
    return colors.get(status_type, STATUS_COLOR_INFO)
