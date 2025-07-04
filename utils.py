import os
import json
import re
import shutil

DIFFICULTY_LOOKUP = {
    "newcomer": "diff_1",
    "casual": "diff_2",
    "skilled": "diff_3",
    "advanced": "diff_4",
    "expert": "diff_5",
    "master": "diff_6",
    "grand_master": "diff_7"
}

DIFFICULTY_SORTED = {
    "Newcomer": "01 - Newcomer",
    "Casual": "02 - Casual",
    "Skilled": "03 - Skilled",
    "Advanced": "04 - Advanced",
    "Expert": "05 - Expert",
    "Master": "06 - Master",
    "Grandmaster": "07 - Grandmaster"
}

def safe_filename(name):
    return re.sub(r'[<>:"/\\|?*]', '', name).strip()

def get_sorted_folder_name(display_difficulty):
    return DIFFICULTY_SORTED.get(display_difficulty, display_difficulty)

def sanitize_name(name):
    return re.sub(r"[^\w\s-]", "", name).strip().replace(" ", "_")

def make_output_path(output_dir, hack_type, display_difficulty):
    subfolder = get_sorted_folder_name(display_difficulty)
    capitalized_type = hack_type.capitalize()
    full_path = os.path.join(output_dir, capitalized_type, subfolder)
    os.makedirs(full_path, exist_ok=True)
    return full_path

def move_rom_to_folder(current_path, hack_type, new_diff, output_dir):
    filename = os.path.basename(current_path)
    new_folder = make_output_path(output_dir, hack_type, new_diff)
    new_path = os.path.join(new_folder, filename)
    shutil.move(current_path, new_path)
    return new_path

def load_processed(path="processed.json"):
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return {}

def save_processed(data, path="processed.json"):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
