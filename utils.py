# utils.py
import os
import json
import re
import shutil

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
    return re.sub(r'[<>:"/\\|?*]', '', name).strip()

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
