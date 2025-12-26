"""
SMWCentral Downloader & Patcher - Utility Functions
Core utilities for file processing, difficulty mapping, and data management

Copyright (c) 2025 iamtheratio
Licensed under the MIT License - see LICENSE file for details
"""

import os
import json
import re
import shutil
import tkinter as tk
import sys
import platform

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)

def set_window_icon(window):
    """Set the application icon for any window or dialog"""
    try:
        if platform.system() == "Linux":
            # On Linux, use PNG icon with iconphoto
            try:
                from PIL import Image, ImageTk
                # Try multiple icon sizes for better compatibility
                icon_sizes = ["64x64", "48x48", "32x32"]
                for size in icon_sizes:
                    icon_path = resource_path(f"assets/icons/smwc-downloader-{size}.png")
                    if os.path.exists(icon_path):
                        icon_image = Image.open(icon_path)
                        icon_photo = ImageTk.PhotoImage(icon_image)
                        window.iconphoto(True, icon_photo)
                        # Keep a reference to prevent garbage collection
                        if not hasattr(window, '_icon_ref'):
                            window._icon_ref = icon_photo
                        return
                        
                # If no PNG icons found, try the default from assets root
                fallback_icon = resource_path("assets/icon.ico")
                if os.path.exists(fallback_icon):
                    # Try to convert .ico to usable format on Linux
                    icon_image = Image.open(fallback_icon)
                    icon_photo = ImageTk.PhotoImage(icon_image)
                    window.iconphoto(True, icon_photo)
                    window._icon_ref = icon_photo
                    return
            except (ImportError, Exception) as e:
                print(f"Linux icon loading failed: {e}")  # Debug info
                pass
        
        # Fallback to .ico for Windows/macOS or if PNG method fails
        window.iconbitmap(resource_path("assets/icon.ico"))
    except (tk.TclError, AttributeError) as e:
        print(f"Icon setting failed: {e}")  # Debug info
        pass  # Fallback silently if icon not found or not supported

# Difficulty mappings
DIFFICULTY_LOOKUP = {
    "diff_1": "Newcomer",
    "diff_2": "Casual",
    "diff_3": "Intermediate",  # Changed from "Skilled" to match SMWC update
    "diff_4": "Advanced",
    "diff_5": "Expert",
    "diff_6": "Master",
    "diff_7": "Grandmaster",
    "": "No Difficulty"  # for hacks without difficulty
}

DIFFICULTY_KEYMAP = {
    "newcomer": "1",
    "casual": "2",
    "intermediate": "3",  # Changed from "skilled" to match SMWC update
    "skilled": "3",  # Keep for backward compatibility during transition
    "advanced": "4",
    "expert": "5",
    "master": "6",
    "grandmaster": "7",
    "no difficulty": ""  # for searching hacks without difficulty
}

DIFFICULTY_SORTED = {
    "Newcomer": "01 - Newcomer",
    "Casual": "02 - Casual",
    "Intermediate": "03 - Intermediate",  # Changed from "Skilled" to match SMWC update
    "Advanced": "04 - Advanced",
    "Expert": "05 - Expert",
    "Master": "06 - Master",
    "Grandmaster": "07 - Grandmaster",
    "No Difficulty": "08 - No Difficulty"  # for folder sorting
}

TYPE_KEYMAP = {
    "Standard": "standard",
    "Kaizo": "kaizo",
    "Puzzle": "puzzle",
    "Tool-Assisted": "tool_assisted",
    "Pit": "pit"
}

TYPE_DISPLAY_LOOKUP = {
    "standard": "Standard",
    "kaizo": "Kaizo",
    "puzzle": "Puzzle",
    "tool_assisted": "Tool-Assisted",
    "pit": "Pit"
}

# Multi-type support utilities
def get_hack_types(hack_data):
    """Get array of hack types from hack data, with backward compatibility"""
    if isinstance(hack_data, dict):
        # Prefer new hack_types array
        if "hack_types" in hack_data and isinstance(hack_data["hack_types"], list):
            return hack_data["hack_types"]
        # Fallback to single hack_type
        elif "hack_type" in hack_data:
            return [hack_data["hack_type"]]
    return ["standard"]

def get_primary_type(hack_data):
    """Get primary (first) type from hack data"""
    types = get_hack_types(hack_data)
    return types[0] if types else "standard"

def normalize_types(types_input):
    """Normalize type strings to consistent format"""
    if isinstance(types_input, str):
        types_input = [types_input]
    elif not isinstance(types_input, list):
        return ["standard"]
    
    normalized = []
    for type_str in types_input:
        if type_str:
            normalized.append(type_str.lower().replace("-", "_"))
    
    return normalized if normalized else ["standard"]

def format_types_display(hack_types):
    """Format types array for display (e.g., 'Kaizo, Tool-Assisted')"""
    if not hack_types:
        return "Unknown"
    
    display_types = []
    for type_val in hack_types:
        display_name = TYPE_DISPLAY_LOOKUP.get(type_val, type_val.title() if type_val else "Unknown")
        display_types.append(display_name)
    
    return ", ".join(display_types)

# Filename sanitization
def safe_filename(name):
    import unicodedata
    
    # First, handle common Unicode characters that cause emulator issues
    unicode_replacements = {
        '⏱︎': 'Timer',  # Timer symbol
        '⏱': 'Timer',   # Timer symbol (variant)
        '🐸': 'Frog',   # Frog emoji
        '🥣': 'Soup',   # Soup emoji
        '🍃': 'Leaf',   # Leaf emoji
        '⭐': 'Star',   # Star emoji
        '💀': 'Skull',  # Skull emoji
        '👑': 'Crown',  # Crown emoji
        '🔥': 'Fire',   # Fire emoji
        '❄️': 'Snow',   # Snowflake emoji
        '🌟': 'Star',   # Glowing star emoji
        '💎': 'Diamond', # Diamond emoji
        '🎯': 'Target', # Target emoji
        '⚡': 'Lightning', # Lightning emoji
        '🌙': 'Moon',   # Moon emoji
        '☀️': 'Sun',    # Sun emoji
        '🎵': 'Music',  # Music note emoji
        '🎶': 'Music',  # Multiple music notes emoji
        '💥': 'Explosion', # Explosion emoji
        '🚀': 'Rocket', # Rocket emoji
        '🎮': 'Game',   # Game controller emoji
        '🏆': 'Trophy', # Trophy emoji
        '⚔️': 'Swords', # Crossed swords emoji
        '🛡️': 'Shield', # Shield emoji
        '🗡️': 'Sword',  # Sword emoji
        '🏰': 'Castle', # Castle emoji
        '🌊': 'Wave',   # Wave emoji
        '🔴': 'Red',    # Red circle emoji
        '🟢': 'Green',  # Green circle emoji
        '🔵': 'Blue',   # Blue circle emoji
        '🟡': 'Yellow', # Yellow circle emoji
        '🟣': 'Purple', # Purple circle emoji
        '⚫': 'Black',  # Black circle emoji
        '⚪': 'White',  # White circle emoji
        '🔶': 'Orange', # Orange diamond emoji
        '🔷': 'Blue',   # Blue diamond emoji
        # Add more as needed
    }
    
    # Replace known Unicode characters with descriptive text
    result = name
    for unicode_char, replacement in unicode_replacements.items():
        result = result.replace(unicode_char, replacement)
    
    # Add spaces between consecutive converted words (when multiple emojis were adjacent)
    # This handles cases like "FrogSoupStarFire" -> "Frog Soup Star Fire"
    # Keep applying the regex until no more changes are made
    prev_result = ""
    while prev_result != result:
        prev_result = result
        result = re.sub(r'([a-z])([A-Z])', r'\1 \2', result)
    
    # Handle any remaining Unicode characters by converting to ASCII equivalents
    # This will convert accented characters like é→e, ñ→n, etc.
    result = unicodedata.normalize('NFD', result)
    result = ''.join(char for char in result if unicodedata.category(char) != 'Mn')
    
    # Remove any remaining non-ASCII characters that couldn't be converted
    result = result.encode('ascii', 'ignore').decode('ascii')
    
    # Remove filesystem-invalid characters
    result = re.sub(r'[<>:"/\\|?*]', '', result).strip()
    
    return result

def title_case(text):
    """
    Convert text to proper title case following English title case rules.
    
    Rules applied:
    - First and last words are always capitalized
    - Words after colons or dashes (subtitles) are capitalized
    - Articles (a, an, the) are lowercase unless first/last/after subtitle
    - Coordinating conjunctions (and, but, or, nor, for, so, yet) are lowercase unless first/last/after subtitle
    - Short prepositions (at, by, in, of, off, on, out, to, up) are lowercase unless first/last/after subtitle
    - Other short words (as, if, than, via) are lowercase unless first/last/after subtitle
    - Special abbreviations and acronyms are handled with custom capitalization
    
    Examples:
    - "super mario world: the lost levels" → "Super Mario World: The Lost Levels"
    - "mario and luigi: brothers in time" → "Mario and Luigi: Brothers in Time"
    """
    
    # Words that should NOT be capitalized in titles (unless first or last word)
    lowercase_words = {
        # Articles
        'a', 'an', 'the',
        # Coordinating conjunctions
        'and', 'but', 'or', 'nor', 'for', 'so', 'yet',
        # Short prepositions (typically under 4 letters)
        'at', 'by', 'in', 'of', 'off', 'on', 'out', 'to',
        # Other common words
        'as', 'if', 'than', 'via'
    }
    
    # Handle common abbreviations and special cases that should always be capitalized
    special_cases = {
        'smw': 'SMW',
        'nsmb': 'NSMB', 
        'nsmbw': 'NSMBW',
        'smb': 'SMB',
        'smb2': 'SMB2',
        'smb3': 'SMB3',
        'kaizo': 'Kaizo',
        'rom': 'ROM',
        'hack': 'Hack',
        'demo': 'Demo',
        'beta': 'Beta',
        'alpha': 'Alpha',
        'v1': 'v1',
        'v2': 'v2',
        'v3': 'v3',
        'ii': 'II',
        'iii': 'III',
        'iv': 'IV',
        'dx': 'DX',
        'ex': 'EX',
        'plus': 'Plus',
        'pro': 'Pro',
        'max': 'Max',
        'ultra': 'Ultra',
        'super': 'Super',
        'mega': 'Mega',
        'hyper': 'Hyper',
        'rta': 'RTA',
        # Period abbreviations
        'a.': 'A.',
        'd.': 'D.',
        'i.': 'I.',
        'a.d.d.': 'A.D.D.',
        'u.s.a.': 'U.S.A.',
        'r.p.g.': 'R.P.G.',
        'a.i.': 'A.I.'
    }
    
    # Split into words and apply proper title case rules
    words = text.split()
    result = []
    
    for i, word in enumerate(words):
        word_lower = word.lower()
        is_first_word = (i == 0)
        is_last_word = (i == len(words) - 1)
        
        # Check if previous word ends with colon or dash (indicates subtitle)
        follows_subtitle_marker = False
        if i > 0:
            prev_word = words[i-1]
            follows_subtitle_marker = prev_word.endswith((':', '-'))
        
        # Special cases always take precedence
        if word_lower in special_cases:
            result.append(special_cases[word_lower])
        # First word, last word, or word after subtitle marker should always be capitalized
        elif is_first_word or is_last_word or follows_subtitle_marker:
            # Handle apostrophes and special name patterns properly
            if "'" in word:
                result.append(capitalize_with_apostrophes(word))
            else:
                result.append(capitalize_proper_name(word))
        # Short words should be lowercase (unless they're special cases)
        elif word_lower in lowercase_words:
            result.append(word_lower)
        # All other words should be capitalized
        else:
            # Handle apostrophes and special name patterns properly for all words
            if "'" in word:
                result.append(capitalize_with_apostrophes(word))
            else:
                result.append(capitalize_proper_name(word))
    
    return ' '.join(result)

def capitalize_proper_name(word):
    """
    Properly capitalize names including Scottish/Irish prefixes and apostrophes.
    Examples: 
    - mcdonald → McDonald, mccarthy → McCarthy
    - macdonald → MacDonald, macbeth → MacBeth  
    - o'connor → O'Connor, d'angelo → D'Angelo
    - mcdonald's → McDonald's
    """
    if not word:
        return word
    
    word_lower = word.lower()
    
    # Handle apostrophes first
    if "'" in word:
        return capitalize_with_apostrophes(word)
    
    # Handle Scottish "Mc" prefix - always capitalize after Mc
    if word_lower.startswith('mc') and len(word) > 2:
        return 'Mc' + word[2].upper() + word[3:].lower()
    
    # Handle Scottish "Mac" prefix - more complex rules
    if word_lower.startswith('mac') and len(word) > 3:
        # Common Mac names that should have capital after Mac
        mac_names = {
            'macdonald', 'macbeth', 'macduff', 'macleod', 'mackenzie', 
            'macarthur', 'macmillan', 'macgregor', 'macpherson'
        }
        
        # Check if it's a known Mac name (these get MacDonald style)
        if word_lower in mac_names or any(word_lower.startswith(name) for name in mac_names):
            return 'Mac' + word[3].upper() + word[4:].lower()
        else:
            # For other Mac words (like Macintosh), just capitalize normally
            return word.capitalize()
    
    # Default capitalization for other words
    return word.capitalize()

def capitalize_with_apostrophes(word):
    """
    Properly capitalize words containing apostrophes.
    Examples: o'ghim → O'Ghim, mcdonald's → McDonald's, isn't → Isn't
    """
    if "'" not in word:
        return capitalize_proper_name(word)
    
    # Split on apostrophe and capitalize each part
    parts = word.split("'")
    capitalized_parts = []
    
    for i, part in enumerate(parts):
        if i == 0:
            # First part gets proper name capitalization (handles Mc/Mac)
            capitalized_parts.append(capitalize_proper_name(part))
        else:
            # Parts after apostrophe: capitalize if not a common suffix
            part_lower = part.lower()
            # Common contractions/possessive endings that should stay lowercase
            lowercase_suffixes = {'s', 't', 're', 've', 'll', 'd', 'm'}
            
            if part_lower in lowercase_suffixes and len(part) <= 2:
                # Keep common contractions lowercase: 's, 't, 're, 've, 'll, 'd, 'm
                capitalized_parts.append(part_lower)
            else:
                # Capitalize proper name parts: O'Ghim, McDonald's, D'Angelo
                capitalized_parts.append(capitalize_proper_name(part))
    
    return "'".join(capitalized_parts)

def clean_hack_title(title):
    """Clean and properly format hack titles with proper capitalization and roman numerals"""
    if not title:
        return "Unknown"
    
    # Handle special Unicode cases
    special_cases = {
        "Up \u1d40\u02b0\u1d49 \u1d3f\u1d52\u1d50\u02b0\u1d43\u1d9c\u1d4f": "Up the Romhack"
    }
    
    # Check for exact matches of special cases
    if title in special_cases:
        return special_cases[title]
    
    # Fix specific period abbreviations BEFORE title case processing
    period_abbreviations = {
        r'\bA\.d\.d\.\b': 'A.D.D.',
        r'\bA\.D\.D\.\b': 'A.D.D.',
        r'\ba\.d\.d\.\b': 'A.D.D.',
        r'\bU\.S\.A\.\b': 'U.S.A.',
        r'\bR\.P\.G\.\b': 'R.P.G.',
        r'\bA\.I\.\b': 'A.I.',
        r'\bA\.i\.\b': 'A.I.',
        r'\ba\.I\.\b': 'A.I.',
        r'\ba\.i\.\b': 'A.I.'
    }
    
    # Apply period abbreviation fixes first
    for pattern, replacement in period_abbreviations.items():
        title = re.sub(pattern, replacement, title, flags=re.IGNORECASE)
    
    # Then apply title case to get basic capitalization
    cleaned = title_case(title)
    
    # Define roman numeral patterns and their proper replacements
    roman_numerals = {
        r'\bI\b': 'I',
        r'\bIi\b': 'II', 
        r'\bIii\b': 'III',
        r'\bIv\b': 'IV',
        r'\bV\b': 'V',
        r'\bVi\b': 'VI',
        r'\bVii\b': 'VII',
        r'\bViii\b': 'VIII',
        r'\bIx\b': 'IX',
        r'\bX\b': 'X',
        r'\bXi\b': 'XI',
        r'\bXii\b': 'XII',
        r'\bXiii\b': 'XIII',
        r'\bXiv\b': 'XIV',
        r'\bXv\b': 'XV',
        r'\bXvi\b': 'XVI',
        r'\bXvii\b': 'XVII',
        r'\bXviii\b': 'XVIII',
        r'\bXix\b': 'XIX',
        r'\bXx\b': 'XX'
    }
    
    # Apply roman numeral corrections (case-insensitive)
    for pattern, replacement in roman_numerals.items():
        cleaned = re.sub(pattern, replacement, cleaned, flags=re.IGNORECASE)
    
    # Fix common abbreviations and acronyms
    acronyms = {
        r'\bSmw\b': 'SMW',
        r'\bUsa\b': 'USA',
        r'\bUk\b': 'UK',
        r'\bRpg\b': 'RPG',
        r'\bFps\b': 'FPS',
        r'\bDx\b': 'DX',
        r'\bEx\b': 'EX',
        r'\bVs\b': 'VS',
        r'\bAi\b': 'AI',  # Match "Ai" without periods
        r'\bGba\b': 'GBA',
        r'\bNes\b': 'NES',
        r'\bSnes\b': 'SNES',
        r'\bN64\b': 'N64',
        r'\bDs\b': 'DS',
        r'\b3d\b': '3D',
        r'\b2d\b': '2D'
    }
    
    for pattern, replacement in acronyms.items():
        cleaned = re.sub(pattern, replacement, cleaned, flags=re.IGNORECASE)
    
    return cleaned.strip()

# Path helpers
def get_sorted_folder_name(display_difficulty):
    return DIFFICULTY_SORTED.get(display_difficulty, display_difficulty)

def make_output_path(output_dir, hack_type, display_difficulty):
    subfolder = get_sorted_folder_name(display_difficulty)
    normalized_type = hack_type.lower().replace("-", "_")
    display_type = TYPE_DISPLAY_LOOKUP.get(normalized_type, hack_type)
    full_path = os.path.join(output_dir, display_type, subfolder)
    os.makedirs(full_path, exist_ok=True)
    return full_path

def move_rom_to_folder(current_path, hack_type, new_diff, output_dir):
    filename = os.path.basename(current_path)
    new_folder = make_output_path(output_dir, hack_type, new_diff)
    new_path = os.path.join(new_folder, filename)
    shutil.move(current_path, new_path)
    return new_path

def move_hack_to_new_difficulty(output_dir, hack_type, old_diff, new_diff, filename):
    old_folder = get_sorted_folder_name(old_diff)
    new_folder = get_sorted_folder_name(new_diff)

    old_path = os.path.join(make_output_path(output_dir, hack_type, old_folder), filename)
    new_path = os.path.join(make_output_path(output_dir, hack_type, new_folder), filename)

    if os.path.exists(old_path):
        os.makedirs(os.path.dirname(new_path), exist_ok=True)
        shutil.move(old_path, new_path)
        return True
    return False

# Processed tracking
def load_processed(path=None):
    if path is None:
        path = PROCESSED_JSON_PATH
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_processed(data, path=None):
    if path is None:
        path = PROCESSED_JSON_PATH
    # Ensure directory exists
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def get_user_data_path(filename):
    """Get platform-specific user data directory for storing app files"""
    system = platform.system()
    
    if system == "Windows":
        # For Windows: Store data files next to the executable for portability
        if getattr(sys, 'frozen', False):
            # Running as PyInstaller executable
            app_data_dir = os.path.dirname(sys.executable)
        else:
            # Running as script in development
            app_data_dir = os.path.dirname(os.path.abspath(__file__))
    elif system == "Darwin":  # macOS
        # Use proper macOS location
        home = os.path.expanduser("~")
        app_data_dir = os.path.join(home, "Library", "Application Support", "SMWC Downloader")
    else:  # Linux and others
        # Use proper Linux location
        home = os.path.expanduser("~")
        app_data_dir = os.path.join(home, ".smwc-downloader")
    
    return os.path.join(app_data_dir, filename)


# Centralized file paths - single source of truth for all application data files
PROCESSED_JSON_PATH = get_user_data_path("processed.json")
CONFIG_JSON_PATH = get_user_data_path("config.json")

# Get base directory (project root)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Ensure cross-platform config file exists in proper location
if not os.path.exists(CONFIG_JSON_PATH):
    # Create the directory if it doesn't exist
    os.makedirs(os.path.dirname(CONFIG_JSON_PATH), exist_ok=True)
    with open(CONFIG_JSON_PATH, 'w') as f:
        json.dump({
            "flips_path": "",
            "base_rom_path": "",
            "output_dir": ""
        }, f, indent=2)

# Multi-type support utilities
def get_hack_types(hack_data):
    """Get array of hack types from hack data, with backward compatibility"""
    if isinstance(hack_data, dict):
        # Prefer new hack_types array
        if "hack_types" in hack_data and isinstance(hack_data["hack_types"], list):
            return hack_data["hack_types"]
        # Fallback to single hack_type
        elif "hack_type" in hack_data:
            return [hack_data["hack_type"]]
    return ["standard"]

def get_primary_type(hack_data):
    """Get primary (first) type from hack data"""
    types = get_hack_types(hack_data)
    return types[0] if types else "standard"

def normalize_types(types_input):
    """Normalize type strings to consistent format"""
    if isinstance(types_input, str):
        types_input = [types_input]
    elif not isinstance(types_input, list):
        return ["standard"]
    
    normalized = []
    for type_str in types_input:
        if type_str:
            normalized.append(type_str.lower().replace("-", "_"))
    
    return normalized if normalized else ["standard"]

def make_output_paths(output_dir, hack_types, display_difficulty):
    """Create output paths for multiple types (future feature)"""
    paths = []
    for hack_type in hack_types:
        path = make_output_path(output_dir, hack_type, display_difficulty)
        paths.append(path)
    return paths

def format_types_display(hack_types):
    """Format types array for display (e.g., 'Kaizo, Tool-Assisted')"""
    if not hack_types:
        return "Unknown"
    
    display_types = []
    for type_val in hack_types:
        display_name = TYPE_DISPLAY_LOOKUP.get(type_val, type_val.title() if type_val else "Unknown")
        display_types.append(display_name)
    
    return ", ".join(display_types)
