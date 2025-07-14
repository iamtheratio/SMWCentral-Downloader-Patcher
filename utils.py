# utils.py
import os
import json
import re
import shutil
import tkinter as tk

def set_window_icon(window):
    """Set the application icon for any window or dialog"""
    try:
        window.iconbitmap("assets/icon.ico")
    except (tk.TclError, AttributeError):
        pass  # Fallback silently if icon not found or not supported

# Difficulty mappings
DIFFICULTY_LOOKUP = {
    "diff_1": "Newcomer",
    "diff_2": "Casual",
    "diff_3": "Skilled",
    "diff_4": "Advanced",
    "diff_5": "Expert",
    "diff_6": "Master",
    "diff_7": "Grandmaster",
    "": "No Difficulty"  # ADDED: for hacks without difficulty
}

DIFFICULTY_KEYMAP = {
    "newcomer": "1",
    "casual": "2",
    "skilled": "3",
    "advanced": "4",
    "expert": "5",
    "master": "6",
    "grandmaster": "7",
    "no difficulty": ""  # ADDED: for searching hacks without difficulty
}

DIFFICULTY_SORTED = {
    "Newcomer": "01 - Newcomer",
    "Casual": "02 - Casual",
    "Skilled": "03 - Skilled",
    "Advanced": "04 - Advanced",
    "Expert": "05 - Expert",
    "Master": "06 - Master",
    "Grandmaster": "07 - Grandmaster",
    "No Difficulty": "08 - No Difficulty"  # ADDED: for folder sorting
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

def sanitize_name(name):
    return re.sub(r"[^\w\s-]", "", name).strip().replace(" ", "_")

def title_case(text):
    """Convert text to proper title case for filenames"""
    # Handle common abbreviations and special cases
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
        'hyper': 'Hyper'
    }
    
    # Split into words and apply title case
    words = text.split()
    result = []
    
    for word in words:
        word_lower = word.lower()
        if word_lower in special_cases:
            result.append(special_cases[word_lower])
        else:
            result.append(word.capitalize())
    
    return ' '.join(result)

def clean_hack_title(title):
    """Clean and properly format hack titles with proper capitalization and roman numerals"""
    if not title:
        return "Unknown"
    
    # First, apply title case to get basic capitalization
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
        r'\bA\.?i\.?\b': 'AI',
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
    
    # Fix common words that should be lowercase (articles, prepositions, conjunctions)
    # but only if they're not at the beginning or end
    lowercase_words = r'\b(a|an|and|as|at|but|by|for|in|nor|of|on|or|so|the|to|up|yet)\b'
    
    def lowercase_middle_words(match):
        word = match.group(0)
        # Check if this word is at the beginning or end of the string
        start_pos = match.start()
        end_pos = match.end()
        
        # Don't lowercase if it's the first word or last word
        if start_pos == 0 or end_pos == len(cleaned):
            return word
        
        # Don't lowercase if it follows a colon or dash (subtitle)
        if start_pos > 0 and cleaned[start_pos-1] in ':- ':
            return word
            
        return word.lower()
    
    cleaned = re.sub(lowercase_words, lowercase_middle_words, cleaned, flags=re.IGNORECASE)
    
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
def load_processed(path="processed.json"):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_processed(data, path="processed.json"):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

# Get base directory (project root)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Config paths
CONFIG_FILE = os.path.join(BASE_DIR, "config.json")
PROCESSED_FILE = os.path.join(BASE_DIR, "processed.json")

# Ensure files exist
if not os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE, 'w') as f:
        json.dump({
            "flips_path": "",
            "base_rom_path": "",
            "output_dir": ""
        }, f, indent=2)
