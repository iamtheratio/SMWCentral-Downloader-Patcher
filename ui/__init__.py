from .components import SetupSection, FilterSection, DifficultySection
from .layout import MainLayout
import sv_ttk

DIFFICULTY_LIST = [
    "newcomer", "casual", "skilled",
    "advanced", "expert", "master", "grandmaster", "no difficulty"
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
    
    # Create main layout
    layout = MainLayout(
        root, 
        run_pipeline_func, 
        toggle_theme_callback,
        setup_section, 
        filter_section, 
        difficulty_section,
        logger,
        version
    )
    
    # Build UI
    layout.create()
    
    # Store layout reference in root for theme updates
    root.main_layout = layout
    
    # Return the download button for external reference
    return layout.get_download_button()

def update_log_colors(log_text):
    """Update log colors based on current theme (used by main.py)"""
    from logging_system import LoggingSystem
    
    # Create a temporary logger just to update colors
    logger = LoggingSystem()
    logger.log_text = log_text
    logger.update_colors()
