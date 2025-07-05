# patcher.py
import requests
import zipfile
import tempfile
import subprocess
import os
from utils import safe_filename, get_sorted_folder_name, make_output_path

def title_case(name):
    return ' '.join(word.capitalize() for word in name.split())

def extract_bps_from_zip(zip_path, extract_to):
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(extract_to)
    for root, _, files in os.walk(extract_to):
        for fname in files:
            if fname.lower().endswith(".bps"):
                return os.path.join(root, fname)
    return None

def patch_with_flips(flips_path, bps_path, base_rom, output_path):
    subprocess.run([
        flips_path, "--apply",
        bps_path,
        base_rom,
        output_path
    ], check=True)

def process_and_patch_hack(hack, flips_path, base_rom_path, output_dir, override_difficulty=None, log=None):
    if log:
        log(f"[DEBUG] Starting patch for: '{hack['title']}'", level="Debug")
        log(f"[DEBUG] Difficulty from config: '{override_difficulty}'", level="Debug")

    final_diff = get_sorted_folder_name(override_difficulty or "unknown")
    rom_type = hack.get("type", "Unknown")

    if log:
        log(f"[DEBUG] Final folder will be: '{rom_type}/{final_diff}'", level="Debug")

    temp_dir = tempfile.mkdtemp()
    zip_path = os.path.join(temp_dir, "hack.zip")

    r = requests.get(hack["download_url"])
    with open(zip_path, "wb") as f:
        f.write(r.content)

    bps_path = extract_bps_from_zip(zip_path, temp_dir)
    if not bps_path:
        raise Exception(".bps file not found in archive")

    title_clean = title_case(safe_filename(hack["title"]))
    output_filename = f"{title_clean}.smc"

    output_folder = make_output_path(output_dir, rom_type, final_diff)
    output_path = os.path.join(output_folder, output_filename)

    if log:
        log(f"[DEBUG] Saving patched ROM to → {output_path}", level="Debug")

    patch_with_flips(flips_path, bps_path, base_rom_path, output_path)

    if log:
        log(f"✅ Patched: {hack['title']} → Folder: '{final_diff}' → File: '{output_filename}'", level="Information")

    return True, final_diff
