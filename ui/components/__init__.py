# UI Components package
from .table_filters import TableFilters
from .inline_editor import InlineEditor

# Import the real components from the parent level
# This avoids the circular import issue by importing from a different path
import importlib.util
import os

# Import the real SetupSection, FilterSection, DifficultySection
spec = importlib.util.spec_from_file_location("real_components", 
                                              os.path.join(os.path.dirname(os.path.dirname(__file__)), "components.py"))
real_components = importlib.util.module_from_spec(spec)
spec.loader.exec_module(real_components)

SetupSection = real_components.SetupSection
FilterSection = real_components.FilterSection  
DifficultySection = real_components.DifficultySection
