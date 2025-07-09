from .components import SetupSection, FilterSection, DifficultySection
from .layout import MainLayout
import sv_ttk

DIFFICULTY_LIST = [
    "newcomer", "casual", "skilled",
    "advanced", "expert", "master", "grandmaster", "no difficulty"  # ADDED: no difficulty
]

def setup_ui(root, run_pipeline_func, toggle_theme_callback, version=None):
    """Set up the complete UI"""
    from config_manager import ConfigManager
    from logging_system import LoggingSystem
    
    # Create core components
    config_manager = ConfigManager()
    logger = LoggingSystem()
    
    # Create UI sections
    setup_section = SetupSection(None, config_manager)
    filter_section = FilterSection(None)
    difficulty_section = DifficultySection(None, DIFFICULTY_LIST)
    
    # Create main layout - pass version parameter
    layout = MainLayout(
        root, 
        run_pipeline_func, 
        toggle_theme_callback,
        setup_section, 
        filter_section, 
        difficulty_section,
        logger,
        version  # Add version parameter
    )
    
    # Build UI
    layout.create()
    
    # Return the download button for external reference
    return layout.download_button

def update_log_colors(log_text):
    """Update log colors based on current theme (used by main.py)"""
    from logging_system import LoggingSystem
    
    # Create a temporary logger just to update colors
    logger = LoggingSystem()
    logger.log_text = log_text
    logger.update_colors()
    
    # Add warning and debug tag colors
    if sv_ttk.get_theme() == "dark":
        log_text.tag_config("warning", foreground="#C76E00")  # Orange
        log_text.tag_config("debug", foreground="#888888")    # Gray
    else:
        log_text.tag_config("warning", foreground="#FFB700")  # Orange 
        log_text.tag_config("debug", foreground="#666666")    # Dark Gray